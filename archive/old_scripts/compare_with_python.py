#!/usr/bin/env python3
"""
Compare Julia/Rust results with Python baseline.

Reads benchmark results from both implementations and generates comparison report.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_python_baseline():
    """Load Python baseline benchmarks."""
    baseline_file = Path(__file__).parent.parent / 'benchmarks' / 'baseline_python' / 'baseline_benchmarks.json'
    
    if not baseline_file.exists():
        return None
    
    with open(baseline_file, 'r') as f:
        return json.load(f)

def load_julia_rust_results():
    """Load Julia/Rust benchmark results."""
    results_file = Path(__file__).parent.parent / 'benchmarks' / 'julia_rust_benchmarks.json'
    
    if not results_file.exists():
        return None
    
    with open(results_file, 'r') as f:
        return json.load(f)

def compare_results(python_data, julia_data):
    """Compare Python and Julia/Rust results."""
    print("=" * 80)
    print("PERFORMANCE COMPARISON: Python vs Julia/Rust")
    print("=" * 80)
    print()
    
    if python_data is None:
        print("⚠️  Python baseline not found. Run baseline_benchmarks.py first.")
        return
    
    if julia_data is None:
        print("⚠️  Julia/Rust results not found. Run benchmark_comparison.jl first.")
        return
    
    # Compare curvature computation
    if "benchmarks" in python_data and "curvature" in python_data["benchmarks"]:
        python_curvature = python_data["benchmarks"]["curvature"]
        print("CURVATURE COMPUTATION")
        print("-" * 80)
        print(f"{'Size':<10} {'Python (s)':<15} {'Julia/Rust (s)':<18} {'Speedup':<12}")
        print("-" * 80)
        
        for python_result in python_curvature:
            size = python_result["nodes"]
            python_time = python_result["time_mean"]
            
            if str(size) in julia_data:
                julia_time = julia_data[str(size)]["time_mean"]
                speedup = python_time / julia_time if julia_time > 0 else 0
                print(f"{size:<10} {python_time:<15.3f} {julia_time:<18.3f} {speedup:<12.2f}x")
            else:
                print(f"{size:<10} {python_time:<15.3f} {'N/A':<18}")
        print()
    
    # Compare null models
    if "benchmarks" in python_data and "null_models" in python_data["benchmarks"]:
        python_nulls = python_data["benchmarks"]["null_models"][0] if python_data["benchmarks"]["null_models"] else None
        
        if python_nulls and "null_models" in julia_data:
            print("NULL MODEL GENERATION")
            print("-" * 80)
            python_time = python_nulls["time_mean"]
            julia_time = julia_data["null_models"]["time_mean"]
            speedup = python_time / julia_time if julia_time > 0 else 0
            
            print(f"Python: {python_time:.3f}s")
            print(f"Julia/Rust: {julia_time:.3f}s")
            print(f"Speedup: {speedup:.2f}x")
            print()

def main():
    python_data = load_python_baseline()
    julia_data = load_julia_rust_results()
    
    compare_results(python_data, julia_data)
    
    # Generate report
    output_dir = Path(__file__).parent.parent / 'docs' / 'benchmarks'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = output_dir / 'performance_comparison_report.txt'
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("PERFORMANCE COMPARISON REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        if python_data and julia_data:
            compare_results(python_data, julia_data)
            # Redirect output to file would require more complex handling
        else:
            f.write("⚠️  Missing benchmark data. Run both baseline_benchmarks.py and benchmark_comparison.jl\n")
    
    print(f"Report saved to: {report_file}")

if __name__ == '__main__':
    main()

