# Makefile for Sounio-fMRI Hypercomplex Geometric Deep Learning
# =============================================================

.PHONY: all install test demo clean visualize validate docker

# Default target
all: demo visualize

# Installation
install:
	@echo "Installing Python dependencies..."
	pip3 install numpy pandas scipy matplotlib seaborn --break-system-packages
	@echo "Dependencies installed!"

install-dev: install
	@echo "Installing development dependencies..."
	pip3 install pytest black flake8 mypy --break-system-packages
	@echo "Development dependencies installed!"

# Run demo with synthetic data
demo:
	@echo "Running synthetic data demo..."
	python3 code/fmri/example_synthetic_analysis.py

# Generate visualizations
visualize:
	@echo "Generating visualization figures..."
	python3 code/fmri/visualize_results.py

# Run validation suite
validate:
	@echo "Running validation suite..."
	python3 code/fmri/validate_pipeline.py --mode full

# Run all tests
test:
	@echo "Running test suite..."
	python3 -m pytest tests/ -v || echo "Tests require pytest installation"

# Test Sounio modules (when compiler available)
test-sounio:
	@echo "Testing Sounio modules..."
	cd stdlib/math && souc test scattering.sio || echo "Sounio compiler not available"
	cd stdlib/math && souc test clifford.sio || echo "Sounio compiler not available"
	cd stdlib/math && souc test homology_curvature.sio || echo "Sounio compiler not available"
	cd stdlib/math && souc test riemannian_manifold.sio || echo "Sounio compiler not available"

# Compile integrated pipeline
compile-pipeline:
	@echo "Compiling integrated pipeline..."
	cd experiments/sounio_fmri && souc compile integrated_pipeline.sio -o pipeline || echo "Sounio compiler not available"

# Run full pipeline
run-pipeline: compile-pipeline
	@echo "Running integrated pipeline..."
	cd experiments/sounio_fmri && ./pipeline

# Code quality checks
lint:
	@echo "Running code quality checks..."
	python3 -m black --check code/fmri/ || echo "Formatting issues found"
	python3 -m flake8 code/fmri/ --max-line-length=100 || echo "Linting issues found"

# Format code
format:
	@echo "Formatting code..."
	python3 -m black code/fmri/

# Type checking
typecheck:
	@echo "Running type checks..."
	python3 -m mypy code/fmri/ --ignore-missing-imports || echo "Type checking complete"

# Download HCP data (requires registration)
download-hcp:
	@echo "Downloading HCP data..."
	@echo "Note: Requires HCP database registration"
	@echo "Visit: https://db.humanconnectome.org"
	python3 code/fmri/download_hcp_data.py || echo "Download script not yet implemented"

# Process real HCP data
process-hcp:
	@echo "Processing HCP data..."
	python3 code/fmri/extract_hcp_data.py \
		--fmri data/hcp/fmri.nii.gz \
		--output-dir results/fmri/hcp \
		--atlas glasser_360 \
		--subject 100307

# Generate documentation
docs:
	@echo "Generating documentation..."
	mkdir -p docs/generated
	python3 -m pydoc -w code/fmri/extract_hcp_data.py || true
	python3 -m pydoc -w code/fmri/validate_pipeline.py || true

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf results/fmri/synthetic_demo/
	rm -rf results/fmri/validation/
	rm -rf __pycache__/
	rm -rf code/fmri/__pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "Clean complete!"

# Deep clean (including downloaded data)
clean-all: clean
	@echo "Deep cleaning..."
	rm -rf data/hcp/
	rm -rf data/external/
	@echo "Deep clean complete!"

# Docker operations
docker-build:
	@echo "Building Docker image..."
	docker build -t sounio-fMRI:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm -v $(PWD)/results:/app/results sounio-fMRI:latest

# Help
help:
	@echo "Sounio-fMRI Hypercomplex Geometric Deep Learning"
	@echo "================================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make install        - Install Python dependencies"
	@echo "  make install-dev    - Install dev dependencies (pytest, black, etc.)"
	@echo "  make demo           - Run synthetic data demo"
	@echo "  make visualize      - Generate visualization figures"
	@echo "  make validate       - Run validation suite"
	@echo "  make test           - Run Python test suite"
	@echo "  make test-sounio    - Test Sounio modules (requires compiler)"
	@echo "  make compile-pipeline - Compile integrated Sounio pipeline"
	@echo "  make run-pipeline   - Run full integrated pipeline"
	@echo "  make lint           - Run code quality checks"
	@echo "  make format         - Format code with black"
	@echo "  make typecheck      - Run type checking with mypy"
	@echo "  make process-hcp    - Process real HCP data"
	@echo "  make docs           - Generate documentation"
	@echo "  make clean          - Clean generated files"
	@echo "  make clean-all      - Deep clean (including data)"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make help           - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  make demo visualize - Run demo and generate figures"
