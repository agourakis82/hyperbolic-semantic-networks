#!/bin/bash
# Build Rust libraries for FFI

set -e

echo "Building Rust libraries for FFI..."
echo "===================================="

cd rust

# Build curvature library
echo ""
echo "Building curvature library..."
cd curvature
cargo build --release
cd ..

# Build null_models library
echo ""
echo "Building null_models library..."
cd null_models
cargo build --release
cd ..

cd ..

echo ""
echo "✅ Rust libraries built successfully!"
echo ""
echo "Libraries should be in:"
echo "  - rust/target/release/libhyperbolic_curvature.so (Linux)"
echo "  - rust/target/release/libhyperbolic_curvature.dylib (macOS)"
echo "  - rust/target/release/hyperbolic_curvature.dll (Windows)"

