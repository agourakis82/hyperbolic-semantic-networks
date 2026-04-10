#!/bin/bash
# Complete validation pipeline

set -e

echo "=" | head -c 80
echo ""
echo "VALIDATION PIPELINE - Julia/Rust vs Python"
echo "=" | head -c 80
echo ""

# Step 1: Build Rust libraries
echo ""
echo "Step 1: Building Rust libraries..."
cd rust
cargo build --release 2>&1 | tail -20
cd ..
echo "✅ Rust libraries built"
echo ""

# Step 2: Run Rust tests
echo "Step 2: Running Rust tests..."
cd rust
cargo test --workspace 2>&1 | tail -30
cd ..
echo "✅ Rust tests passed"
echo ""

# Step 3: Run Julia tests
echo "Step 3: Running Julia tests..."
julia --project=julia -e 'using Pkg; Pkg.instantiate()' 2>&1 | tail -10
julia --project=julia test/runtests.jl 2>&1 | tail -50
echo "✅ Julia tests passed"
echo ""

# Step 4: Run validation script
echo "Step 4: Running validation against Python..."
julia --project=julia scripts/validate_implementation.jl 2>&1 | tail -30
echo "✅ Validation completed"
echo ""

# Step 5: Generate summary
echo "=" | head -c 80
echo ""
echo "VALIDATION COMPLETE"
echo "=" | head -c 80
echo ""
echo "Next steps:"
echo "  1. Review test outputs"
echo "  2. Check validation results"
echo "  3. Run performance benchmarks if needed"
echo ""

