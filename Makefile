# Makefile for Hyperbolic Semantic Networks

.PHONY: help build-rust test-julia test-rust test-all validate clean

help:
	@echo "Available targets:"
	@echo "  build-rust    - Build Rust libraries"
	@echo "  test-julia    - Run Julia tests"
	@echo "  test-rust     - Run Rust tests"
	@echo "  test-all      - Run all tests"
	@echo "  validate      - Validate implementation"
	@echo "  clean         - Clean build artifacts"

build-rust:
	@echo "Building Rust libraries..."
	cd rust && cargo build --release

test-rust:
	@echo "Running Rust tests..."
	cd rust && cargo test

test-julia:
	@echo "Running Julia tests..."
	julia --project=julia test/runtests.jl

test-all: test-rust test-julia
	@echo "All tests completed!"

validate: build-rust
	@echo "Validating implementation..."
	julia --project=julia scripts/validate_implementation.jl

clean:
	@echo "Cleaning build artifacts..."
	cd rust && cargo clean
	rm -rf julia/Manifest.toml

.DEFAULT_GOAL := help

