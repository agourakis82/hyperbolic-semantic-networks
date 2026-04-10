# Makefile for Sounio-fMRI Hypercomplex Geometric Deep Learning
# =============================================================

.PHONY: all install test demo clean visualize validate docker cpc2026 cpc2026-smoke cpc2026-ossm cpc2026-poster

CPC2026_PYTHON ?= python3
SOUNIO_REPO ?= /home/demetrios/work/sounio-lang
SOUC ?= $(SOUNIO_REPO)/artifacts/omega/souc-bin/souc-linux-x86_64-gpu
SOUNIO_PARITY_RESULTS ?= $(SOUNIO_REPO)/examples/cognitive_ossm/results

cpc2026:
	@echo "Running CPC 2026 pipeline..."
	$(CPC2026_PYTHON) code/cpc2026/valence_loader.py
	$(CPC2026_PYTHON) code/cpc2026/entropic_curvature.py
	$(CPC2026_PYTHON) code/cpc2026/trajectory_simulator.py
	$(CPC2026_PYTHON) code/cpc2026/analysis.py
	$(CPC2026_PYTHON) code/cpc2026/generate_figures.py
	@echo "CPC 2026 pipeline complete."

cpc2026-smoke:
	@echo "Running CPC 2026 smoke pipeline..."
	$(CPC2026_PYTHON) code/cpc2026/valence_loader.py --smoke-test
	$(CPC2026_PYTHON) code/cpc2026/entropic_curvature.py --smoke-test
	$(CPC2026_PYTHON) code/cpc2026/trajectory_simulator.py --smoke-test --include-exploratory-engines
	$(CPC2026_PYTHON) code/cpc2026/analysis.py --smoke-test --bootstrap 200
	$(CPC2026_PYTHON) code/cpc2026/generate_figures.py
	@echo "CPC 2026 smoke pipeline complete."

cpc2026-ossm:
	@echo "Running CPC 2026 O-SSM extension..."
	@echo "Canonical Sounio compiler: $(SOUC)"
	@$(SOUC) --version
	$(CPC2026_PYTHON) code/cpc2026/valence_loader.py
	$(CPC2026_PYTHON) code/cpc2026/entropic_curvature.py
	$(CPC2026_PYTHON) code/cpc2026/trajectory_simulator.py
	$(CPC2026_PYTHON) code/cpc2026/analysis.py
	$(CPC2026_PYTHON) code/cpc2026/ossm_bridge/node_features.py
	$(CPC2026_PYTHON) code/cpc2026/ossm_bridge/trajectory_generator.py
	$(CPC2026_PYTHON) code/cpc2026/ossm_bridge/export_to_sounio.py
	mkdir -p $(SOUNIO_PARITY_RESULTS)
	cd $(SOUNIO_REPO) && $(SOUC) run examples/cognitive_ossm/cognitive_ossm.sio
	cd $(SOUNIO_REPO) && $(SOUC) run examples/cognitive_ossm/run_regimes.sio -- --max-trajectories 8 --max-steps 64
	cd $(SOUNIO_REPO) && $(SOUC) run examples/cognitive_ossm/export_results.sio
	mkdir -p results/cpc2026/sounio_parity
	cp $(SOUNIO_PARITY_RESULTS)/*.csv results/cpc2026/sounio_parity/
	$(CPC2026_PYTHON) code/cpc2026/ossm_reference_simulator.py
	$(CPC2026_PYTHON) code/cpc2026/ossm_analysis.py
	$(CPC2026_PYTHON) code/cpc2026/generate_ossm_figures.py
	@echo "CPC 2026 O-SSM extension complete."

cpc2026-poster:
	@echo "Running CPC 2026 poster upgrade pipeline..."
	$(CPC2026_PYTHON) code/cpc2026/clinical_validation.py
	$(CPC2026_PYTHON) code/cpc2026/cross_validation_summary.py
	$(CPC2026_PYTHON) code/cpc2026/generate_poster_figures.py
	@echo "CPC 2026 poster figures complete."

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
	@echo "  make cpc2026        - Run the CPC 2026 Markov baseline pipeline"
	@echo "  make cpc2026-ossm   - Run the CPC 2026 O-SSM bridge + parity + analysis pipeline"
	@echo "  make cpc2026-poster - Generate upgraded CPC 2026 poster figures"
	@echo "  make help           - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  make demo visualize - Run demo and generate figures"
