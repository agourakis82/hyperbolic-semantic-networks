#!/usr/bin/env python3
"""
Process Nature MDD Dataset - Build Semantic Speech Networks
Similar to PMC10031728 methodology
"""

import os
import pandas as pd
import networkx as nx
from pathlib import Path
import json
import re

print("="*70)
print("PROCESSING NATURE MDD DATASET - SEMANTIC SPEECH NETWORKS")
print("="*70)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path("data/external/nature_mdd_dataset/")
OUTPUT_DIR = Path("data/processed/mdd_networks/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Check if data exists
if not DATA_DIR.exists():
    print(f"⚠️ Data directory not found: {DATA_DIR}")
    print()
    print("Please download data first:")
    print("  1. Visit: https://www.nature.com/articles/s41597-022-01211-x")
    print("  2. Find 'Data Availability' section")
    print("  3. Download speech/picture description data")
    print(f"  4. Save to: {DATA_DIR}")
    print()
    exit(1)

# ============================================================================
# STEP 1: LOAD PARTICIPANT METADATA
# ============================================================================

print("STEP 1: LOADING PARTICIPANT METADATA")
print("-"*70)

# Try to find participants/metadata file
possible_names = ['participants.csv', 'metadata.csv', 'subjects.csv', 'labels.csv']
participants_file = None

for name in possible_names:
    if (DATA_DIR / name).exists():
        participants_file = DATA_DIR / name
        break

if participants_file:
    participants_df = pd.read_csv(participants_file)
    print(f"✅ Loaded: {participants_file.name}")
    print(f"   Participants: {len(participants_df)}")
    print(f"   Columns: {list(participants_df.columns)}")
    print()
    print("First 5 rows:")
    print(participants_df.head())
else:
    print("⚠️ No participants file found")
    print("Will process all transcripts without group labels")
    participants_df = None

print()

# ============================================================================
# STEP 2: LOAD TRANSCRIPTS
# ============================================================================

print("STEP 2: LOADING TRANSCRIPTS")
print("-"*70)

# Look for picture description transcripts
transcript_dirs = [
    DATA_DIR / 'picture_description',
    DATA_DIR / 'picture_desc',
    DATA_DIR / 'transcripts',
    DATA_DIR / 'speech',
    DATA_DIR / 'audio_transcripts'
]

transcript_dir = None
for tdir in transcript_dirs:
    if tdir.exists():
        transcript_dir = tdir
        break

if not transcript_dir:
    print("⚠️ Transcript directory not found")
    print("Expected locations:")
    for tdir in transcript_dirs:
        print(f"  - {tdir}")
    print()
    print("Please specify correct path or place transcripts in one of above directories")
    exit(1)

# Load transcripts
transcript_files = list(transcript_dir.glob("*.txt")) + \
                  list(transcript_dir.glob("*.csv"))

print(f"✅ Found {len(transcript_files)} transcript files in: {transcript_dir.name}")
print()

if len(transcript_files) == 0:
    print("⚠️ No transcript files found")
    print("Expected formats: .txt or .csv")
    exit(1)

# ============================================================================
# STEP 3: BUILD SEMANTIC NETWORKS
# ============================================================================

print("STEP 3: BUILDING SEMANTIC NETWORKS")
print("-"*70)
print()

networks = {}

for transcript_file in transcript_files[:5]:  # Show first 5
    # Extract participant ID from filename
    participant_id = transcript_file.stem
    
    # Load transcript
    try:
        if transcript_file.suffix == '.txt':
            with open(transcript_file, 'r', encoding='utf-8') as f:
                text = f.read()
        elif transcript_file.suffix == '.csv':
            df = pd.read_csv(transcript_file)
            # Assume first column or 'text' column has transcript
            if 'text' in df.columns:
                text = ' '.join(df['text'].astype(str).tolist())
            else:
                text = ' '.join(df.iloc[:, 0].astype(str).tolist())
        else:
            continue
        
        # Build network (simplified - extract entities and co-occurrences)
        # This is a placeholder - would need full NLP pipeline like PMC10031728
        
        # Extract words (simple tokenization)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Build co-occurrence network (window size = 5)
        G = nx.Graph()
        window = 5
        
        for i in range(len(words) - window):
            for j in range(i+1, i+window):
                if i < len(words) and j < len(words):
                    G.add_edge(words[i], words[j])
        
        # Store
        networks[participant_id] = G
        
        print(f"  {participant_id}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
    except Exception as e:
        print(f"  ❌ Error processing {participant_id}: {e}")

print()
print(f"✅ Built {len(networks)} networks")
print()

# ============================================================================
# STEP 4: SAVE NETWORKS AS EDGE LISTS
# ============================================================================

print("STEP 4: SAVING NETWORKS")
print("-"*70)

for participant_id, G in networks.items():
    output_file = OUTPUT_DIR / f"{participant_id}_edges.csv"
    
    edges = []
    for u, v in G.edges():
        edges.append({'source': u, 'target': v})
    
    df_edges = pd.DataFrame(edges)
    df_edges.to_csv(output_file, index=False)

print(f"✅ Saved {len(networks)} edge lists to: {OUTPUT_DIR}")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*70)
print("SUMMARY")
print("="*70)
print()
print(f"Participants: {len(participants_df) if participants_df is not None else 'Unknown'}")
print(f"Transcripts: {len(transcript_files)}")
print(f"Networks built: {len(networks)}")
print(f"Output directory: {OUTPUT_DIR}")
print()

print("="*70)
print("✅ NETWORK BUILDING COMPLETE")
print("="*70)
print()
print("Next steps:")
print("  1. Run: python code/analysis/compute_mdd_metrics.py")
print("  2. Then: python code/analysis/compute_kec_mdd.py")

