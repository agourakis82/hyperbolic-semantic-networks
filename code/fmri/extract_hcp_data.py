#!/usr/bin/env python3
"""
HCP fMRI Data Extraction Bridge
==============================
Extracts 4D spatial-temporal data from HCP NIfTI files and formats as 
Quaternion-ready time series for Sounio ingestion.

Output format: CSV with columns [time, x, y, z, signal] for each ROI
where (x, y, z) are spatial coordinates and signal is the BOLD time series.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
try:
    import nibabel as nib
    from nilearn import datasets, plotting
    from nilearn.maskers import NiftiLabelsMasker
    NILEARN_AVAILABLE = True
except ImportError:
    NILEARN_AVAILABLE = False
    print("Warning: nilearn not available. Install with: pip install nilearn")


class HCPDataExtractor:
    """Extract and format HCP fMRI data for Sounio hypercomplex analysis."""
    
    def __init__(self, atlas: str = "glasser_360"):
        """
        Initialize extractor with parcellation atlas.
        
        Args:
            atlas: Parcellation atlas name ("glasser_360", "schaefer_400", "aal")
        """
        self.atlas = atlas
        self.roi_coords = None
        self.time_series = None
        
    def load_atlas(self) -> Tuple[np.ndarray, List[str]]:
        """
        Load parcellation atlas with ROI coordinates.
        
        Returns:
            Tuple of (roi_coordinates, roi_labels)
        """
        if self.atlas == "glasser_360":
            # Glasser 2016 multimodal parcellation
            # Coordinates from MNI space
            atlas_path = datasets.fetch_atlas_glasser_2016()
            atlas_img = nib.load(atlas_path["maps"])
            labels = atlas_path["labels"].tolist()
            
            # Extract centroid coordinates for each ROI
            atlas_data = atlas_img.get_fdata()
            roi_coords = []
            
            for i, label in enumerate(labels, 1):
                mask = atlas_data == i
                if np.any(mask):
                    coords = np.argwhere(mask)
                    centroid = coords.mean(axis=0)
                    # Convert voxel to MNI coordinates
                    affine = atlas_img.affine
                    mni_coords = nib.affines.apply_affine(affine, centroid)
                    roi_coords.append(mni_coords)
                else:
                    roi_coords.append([0, 0, 0])
                    
            return np.array(roi_coords), labels
            
        elif self.atlas == "schaefer_400":
            # Schaefer 2018 400-parcel atlas
            atlas_path = datasets.fetch_atlas_schaefer_2018(
                n_rois=400, yeo_networks=7, resolution_mm=2
            )
            atlas_img = nib.load(atlas_path["maps"])
            labels = atlas_path["labels"].tolist()
            
            # Extract centroids
            atlas_data = atlas_img.get_fdata()
            roi_coords = []
            
            for i, label in enumerate(labels, 1):
                mask = atlas_data == i
                if np.any(mask):
                    coords = np.argwhere(mask)
                    centroid = coords.mean(axis=0)
                    affine = atlas_img.affine
                    mni_coords = nib.affines.apply_affine(affine, centroid)
                    roi_coords.append(mni_coords)
                else:
                    roi_coords.append([0, 0, 0])
                    
            return np.array(roi_coords), labels
            
        else:
            raise ValueError(f"Unknown atlas: {self.atlas}")
    
    def extract_time_series(
        self, 
        fmri_path: Path,
        confounds: Optional[pd.DataFrame] = None
    ) -> np.ndarray:
        """
        Extract time series from fMRI NIfTI file.
        
        Args:
            fmri_path: Path to preprocessed fMRI NIfTI file
            confounds: Optional confound regressors
            
        Returns:
            Time series array (n_timepoints, n_rois)
        """
        if not NILEARN_AVAILABLE:
            raise RuntimeError("nilearn required for fMRI extraction")
            
        # Load atlas
        atlas_path = datasets.fetch_atlas_glasser_2016()
        
        # Create masker
        masker = NiftiLabelsMasker(
            labels_img=atlas_path["maps"],
            standardize=True,
            detrend=True,
            low_pass=0.1,
            high_pass=0.01,
            t_r=0.72  # HCP TR
        )
        
        # Extract time series
        time_series = masker.fit_transform(str(fmri_path), confounds=confounds)
        
        return time_series
    
    def format_as_quaternion_csv(
        self,
        time_series: np.ndarray,
        roi_coords: np.ndarray,
        output_path: Path
    ) -> None:
        """
        Format time series as Quaternion-ready CSV.
        
        Each row represents a 4D point: [t, x, y, z, signal]
        where (x, y, z) are spatial coordinates and signal is BOLD.
        
        Args:
            time_series: Array (n_timepoints, n_rois)
            roi_coords: Array (n_rois, 3) of MNI coordinates
            output_path: Output CSV path
        """
        n_timepoints, n_rois = time_series.shape
        
        # Create DataFrame with all timepoints × ROIs
        rows = []
        for t in range(n_timepoints):
            for roi in range(n_rois):
                x, y, z = roi_coords[roi]
                signal = time_series[t, roi]
                rows.append({
                    'time': t,
                    'x': x,
                    'y': y,
                    'z': z,
                    'roi': roi,
                    'signal': signal
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        print(f"Saved Quaternion-ready data to {output_path}")
        print(f"  Shape: {n_timepoints} timepoints × {n_rois} ROIs = {len(df)} rows")
    
    def compute_functional_connectivity(
        self,
        time_series: np.ndarray,
        method: str = "pearson"
    ) -> np.ndarray:
        """
        Compute functional connectivity matrix.
        
        Args:
            time_series: Array (n_timepoints, n_rois)
            method: Correlation method ("pearson", "partial", "precision")
            
        Returns:
            Connectivity matrix (n_rois, n_rois)
        """
        if method == "pearson":
            # Pearson correlation
            corr = np.corrcoef(time_series.T)
            # Fisher z-transform for normalization
            corr_z = np.arctanh(np.clip(corr, -0.999, 0.999))
            return corr_z
        else:
            raise NotImplementedError(f"Method {method} not implemented")
    
    def save_connectivity_matrix(
        self,
        connectivity: np.ndarray,
        roi_coords: np.ndarray,
        labels: List[str],
        output_path: Path
    ) -> None:
        """
        Save connectivity matrix as edge list for Sounio graph construction.
        
        Args:
            connectivity: Connectivity matrix (n_rois, n_rois)
            roi_coords: ROI coordinates (n_rois, 3)
            labels: ROI labels
            output_path: Output CSV path
        """
        n_rois = len(labels)
        
        # Threshold and create edge list
        edges = []
        threshold = 0.1  # Minimum correlation
        
        for i in range(n_rois):
            for j in range(i+1, n_rois):
                weight = connectivity[i, j]
                if abs(weight) > threshold:
                    edges.append({
                        'source': labels[i],
                        'target': labels[j],
                        'source_x': roi_coords[i, 0],
                        'source_y': roi_coords[i, 1],
                        'source_z': roi_coords[i, 2],
                        'target_x': roi_coords[j, 0],
                        'target_y': roi_coords[j, 1],
                        'target_z': roi_coords[j, 2],
                        'weight': weight
                    })
        
        df = pd.DataFrame(edges)
        df.to_csv(output_path, index=False)
        print(f"Saved connectivity edges to {output_path}")
        print(f"  {len(df)} edges (threshold |r| > {threshold})")


def main():
    """Example usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract HCP fMRI data for Sounio")
    parser.add_argument("--fmri", type=Path, required=True, help="Path to fMRI NIfTI file")
    parser.add_argument("--output-dir", type=Path, default=Path("results/fmri"), help="Output directory")
    parser.add_argument("--atlas", default="glasser_360", choices=["glasser_360", "schaefer_400"])
    parser.add_argument("--subject", default="test_subject", help="Subject ID")
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize extractor
    extractor = HCPDataExtractor(atlas=args.atlas)
    
    # Load atlas
    print(f"Loading {args.atlas} atlas...")
    roi_coords, labels = extractor.load_atlas()
    print(f"  Loaded {len(labels)} ROIs")
    
    # Extract time series
    print(f"Extracting time series from {args.fmri}...")
    time_series = extractor.extract_time_series(args.fmri)
    print(f"  Time series shape: {time_series.shape}")
    
    # Save as Quaternion-ready CSV
    quaternion_path = args.output_dir / f"{args.subject}_quaternion_timeseries.csv"
    extractor.format_as_quaternion_csv(time_series, roi_coords, quaternion_path)
    
    # Compute and save connectivity
    print("Computing functional connectivity...")
    connectivity = extractor.compute_functional_connectivity(time_series)
    
    connectivity_path = args.output_dir / f"{args.subject}_connectivity_edges.csv"
    extractor.save_connectivity_matrix(connectivity, roi_coords, labels, connectivity_path)
    
    print("\nExtraction complete!")
    print(f"  Quaternion data: {quaternion_path}")
    print(f"  Connectivity edges: {connectivity_path}")


if __name__ == "__main__":
    main()
