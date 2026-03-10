# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Hyperbolic Semantic Networks** is a multi-language research project investigating network geometry using Ollivier-Ricci curvature. The key finding is a **universal phase transition** that determines network geometry: FORMALIZED

**Key Discovery (STATUS: [EMPIRICAL] + [FORMALIZED])**:
- **Parameter**: η = ⟨k⟩²/N (density parameter)
- **Regimes**:
  - η < η_c(N) → **Hyperbolic** (κ̄ < 0, tree-like)
  - η ≈ η_c(N) → **Critical/Euclidean** (sign change)
  - η > η_c(N) → **Spherical** (κ̄ > 0, clique-like)
- **Empirical η_c**: 2.29 (N=100), 3.32 (N=1000), 3.75 (N→∞)
- **Proven theorem**: `regimes_exclusive` (Lean) — formal proof that regimes are mutually exclusive
- **Real-world validation**: Dutch SWOW (η=7.56) is first semantic network to cross phase boundary → κ̄=+0.099 (spherical) ✓

**Applications to Semantic Networks** (11 networks across 7 languages):
- Spanish/English/Chinese SWOW: η ≈ 0.02 → hyperbolic ✓
- Dutch SWOW: η ≈ 7.56 → spherical ✓ [breakthrough finding]
- ConceptNet, depression symptom network: η < η_c → hyperbolic ✓
- Prediction accuracy: 11/11 networks correctly classified

**Technical Stack**: Rust (performance kernels) + Julia (reference implementation) + Lean 4 (formal verification) + Python (analysis)

---

## Architecture

### Four-Layer Stack (See AGENTS.md for full stack details)

```
Python (Analysis & Data Processing)
  ↓
Julia (Scientific Computing, High-level API, FFI orchestration)
  ↓
Rust (Performance-critical: Sinkhorn, graph algorithms)
  ↓
Lean 4 (Formal verification of theorems)
```

### Technology Stack Details

**Julia** (`julia/Project.toml`):
- `Graphs.jl` — graph library & algorithms
- `DataFrames.jl`, `CSV.jl`, `JSON.jl` — data handling
- `Statistics.jl`, `LinearAlgebra.jl`, `Optim.jl` — numerical computation
- `Plots.jl`, `StatsPlots.jl` — visualization
- `ProgressMeter.jl`, `Logging.jl` — utilities
- `JuMP.jl`, `HiGHS.jl` — exact linear programming (ORC solver)

**Rust** (`rust/Cargo.toml`):
- `ndarray 0.16` — numerical arrays
- `rayon 1.8` — parallel processing
- `petgraph 0.6` — graph library
- `libc 0.2` — FFI bindings
- `criterion 0.5` — benchmarking with HTML reports

**Python** (code/analysis):
- `networkx`, `GraphRicciCurvature` — curvature computation
- `numpy`, `scipy`, `pandas` — numerical/data manipulation
- `matplotlib`, `seaborn` — visualization
- `pytest` — testing framework

**Lean 4** (formal verification):
- `Mathlib4` — standard library for proof
- Custom 25 modules (Curvature, Wasserstein, PhaseTransition, etc.)

### Directory Structure

```
hyperbolic-semantic-networks/
├── julia/                 # Reference implementation & high-level API
│   ├── src/              # Core modules (graph, curvature, utils)
│   ├── scripts/          # Experiments (phase_transition_*.jl, etc.)
│   ├── Project.toml      # Dependencies
│   └── test/             # Julia unit tests
│
├── rust/                 # Performance kernels
│   ├── curvature/        # Wasserstein-1 (Sinkhorn algorithm)
│   ├── null_models/      # Configuration model, rewiring
│   └── Cargo.toml        # Workspace config
│
├── lean/                 # Formal verification
│   └── HyperbolicSemanticNetworks/
│       ├── HyperbolicSemanticNetworks/  # 25 core modules
│       ├── lakefile.lean                 # Build config
│       └── FORMALIZATION_STATUS.md       # Proof inventory
│
├── manuscript/           # LaTeX monograph
│   ├── latex/monograph.tex   # Main paper (13 pages)
│   └── latex/monograph.md    # Markdown version
│
├── code/                 # Python scripts
│   ├── fmri/            # Brain network analysis
│   └── analysis/        # Data processing, figures
│
├── results/             # Computed outputs (JSON, CSV)
│   ├── experiments/     # Phase transition data
│   ├── unified/         # Semantic network results
│   └── fmri/            # Brain curvature
│
├── figures/             # Publication figures
│   ├── monograph/       # 8 unified monograph figures (PDF/PNG)
│   └── paper/           # Original paper figures
│
├── experiments/         # Sounio programs (when available)
│   ├── 01_epistemic_uncertainty/
│   └── ... (07 experiments total)
│
├── Makefile            # Common targets (build, test, demo)
├── README.md           # User-facing overview
└── DEVELOPMENT.md      # Developer setup & contribution guide
```

---

## Quick Commands Reference

### Building Components

**Rust** (performance kernels):
```bash
cd rust
cargo build --release          # Build all workspace members
cargo test --workspace         # Run Rust tests
cargo clippy --all            # Lint check
cargo fmt --all               # Format code
```

**Julia** (scientific computing):
```bash
julia --project=julia -e 'using Pkg; Pkg.instantiate()'  # Install deps
julia --project=julia julia/scripts/phase_transition_pure_julia.jl  # Run reference experiment
julia --project=julia -e 'using Pkg; Pkg.test()'  # Run Julia tests
```

**Lean** (formal verification):
```bash
cd lean/HyperbolicSemanticNetworks
lake build              # Build all modules (should complete without error)
lake doc                # Generate documentation
```

**Python** (analysis):
```bash
cd code/analysis
pip install -r requirements.txt
pytest tests/ -v        # Run tests
python script_name.py   # Run analysis scripts
```

### Common Targets (via Makefile)

```bash
make install          # Install Python dependencies
make install-dev      # Install dev tools (pytest, black, mypy, etc.)
make demo             # Run synthetic fMRI demo
make visualize        # Generate figures from results
make test             # Run Python tests
make lint             # Check code quality (black, flake8)
make format           # Auto-format Python code
make typecheck        # Run mypy type checking
make clean            # Remove generated files
make help             # Show all targets
```

---

## Key Experiments & Scripts

### Phase Transition (Discovery Core)

**Julia reference** (most reliable):
```bash
julia --project=julia julia/scripts/phase_transition_pure_julia.jl
# Output: results/experiments/phase_transition_pure_julia.json
# N=100: transition between k=14 (κ=-0.016) and k=16 (κ=+0.022)
```

**N=1000 validation**:
```bash
julia --project=julia julia/scripts/run_n1000.jl
# Output: results/experiments/phase_transition_n1000.json
# Confirms η_c(1000) ≈ 3.32
```

**Finite-size scaling**:
```bash
julia --project=julia julia/scripts/run_er_comparison.jl
# Output: scaling curve η_c(N) = 3.75 - 14.62/√N (R² = 0.995)
```

### Semantic Networks (Real Data)

**Complete 11-network analysis** (exact LP ORC):
```bash
julia --project=julia julia/scripts/unified_semantic_orc.jl
# Output: results/unified/ (per-network JSON files)
# Networks: SWOW (ES/EN/ZH/NL), ConceptNet (EN/PT), WordNet, BabelNet, depression
# Key finding: SWOW Dutch (η=7.56) is spherical; others hyperbolic
```

**Hypercomplex embedding** (Cayley-Dickson tower):
```bash
julia --project=julia julia/scripts/hypercomplex_lp.jl
# Output: results/experiments/hypercomplex_lp_n{N}_d{d}.json
# Dimensional analysis: S³→S⁷→S¹⁵ eliminate negative curvature
```

**Analytical phase boundary** (Hehl formula):
```bash
julia --project=julia julia/scripts/analytical_eta_c.jl
# Output: results/unified/analytical_eta_c.json
# Validates heuristic formula against empirical data
```

### Data Generation

**Figures for monograph** (all 8 figures):
```bash
julia --project=julia julia/scripts/generate_monograph_figures.jl
# Output: figures/monograph/figure{1..8}_{pdf,png}
# Includes: phase curves, bridge plot, clustering, dimensional hierarchy, null models
```

**Statistical analysis & tables**:
```bash
julia --project=julia julia/scripts/statistical_analysis.jl
# Generates tables: N=100 transition, Sinkhorn comparison, LLY validation, ER comparison
```

---

## Building & Rebuilding the Manuscript

**LaTeX monograph** (0 errors, 0 undefined refs):
```bash
cd manuscript/latex
pdflatex monograph.tex    # Run twice to resolve cross-references
pdflatex monograph.tex
# Output: monograph.pdf (13 pages, 8 figures)
```

**Figures required before compilation**:
- Must exist: `../../figures/monograph/figure{1..8}.pdf`
- Generate via: `julia --project=julia julia/scripts/generate_monograph_figures.jl`

**Markdown version**:
- `manuscript/monograph.md` — auto-generated from LaTeX for arXiv submission

---

## Testing Strategy

### Unit Tests

**Rust** (isolated kernels):

```bash
cd rust
cargo test --lib                          # Run all unit tests
cargo test --lib curvature::tests         # Wasserstein distance tests
cargo test --lib null_models::tests       # Configuration model tests
cargo test --doc                          # Run doc tests
```

**Julia** (mathematical correctness):

```bash
julia --project=julia -e 'using Pkg; Pkg.test()'        # Full test suite
julia --project=julia julia/test/runtests.jl             # Run with progress
julia --project=julia julia/test/test_properties.jl      # Graph properties validation
julia --project=julia julia/test/test_regression.jl      # Numerical regression tests
julia --project=julia julia/test/test_performance.jl     # Performance benchmarks
```

**Python** (data processing):

```bash
cd code/analysis
pytest tests/test_*.py -v                          # Run all tests verbosely
pytest tests/test_curvature.py::test_phase_transition -v  # Single test
pytest tests/ --cov=. --cov-report=html            # With coverage report
```

**Running individual script validation**:

```bash
# Validate phase transition theory on real networks
julia --project=julia julia/scripts/validate_against_real_networks.jl

# Run core phase transition experiment
julia --project=julia julia/scripts/phase_transition_pure_julia.jl

# Validate against specific network
julia --project=julia -e 'include("julia/scripts/validate_against_real_networks.jl"); validate_network("swow_dutch")'
```

### Integration Tests

**FFI (Rust ↔ Julia)**:
- Rust library loaded via `ccall` in `julia/src/Curvature/FFI.jl`
- Verify with: `julia --project=julia -e "include(\"julia/src/Curvature/FFI.jl\"); test_ffi()"`

**End-to-end pipeline**:
```bash
# Generate phase transition data → validate scaling → compare with semantic networks
julia --project=julia julia/scripts/phase_transition_pure_julia.jl
julia --project=julia julia/scripts/statistical_analysis.jl
```

**Lean verification** (theorem proving):
```bash
cd lean/HyperbolicSemanticNetworks
lake build  # Should compile with 0 errors (86 sorry declarations are documented)
```

### Performance Benchmarks

**Rust** (Sinkhorn bottleneck):
```bash
cd rust/curvature
cargo bench          # Criterion benchmarks with HTML reports
cargo bench --bench wasserstein_bench
```

**Julia** (whole-graph performance):
```julia
using BenchmarkTools, Graphs
include("julia/src/Curvature/FFI.jl")
g = erdos_renyi(200, 0.3)
@time compute_graph_curvature(g, parallel=true)
```

---

## Key Numbers (Verified Feb 2026)

### Phase Transition

| Metric | Value | Notes |
|--------|-------|-------|
| **η_c(N=100)** | 2.29 | Between k=14 (η=1.96, κ=-0.016) and k=16 (η=2.56, κ=+0.022) |
| **η_c(N=1000)** | 3.32 | Fitted from 5 k-values |
| **η_c(∞)** | 3.75 | Finite-size scaling: η_c(N) = 3.75 - 14.62/√N, R²=0.995 |
| **Transition width** | k=2 | Sharp curvature flip at critical k |
| **Sign change** | Proven in Lean (Curvature.lean) | `regimes_exclusive` theorem |

### Semantic Networks (11 Total)

| Network | N | η | κ | Prediction | Actual |
|---------|---|---|---|-----------|--------|
| **SWOW Spanish** | 422 | 0.017 | -0.068 | Hyperbolic ✓ | Hyperbolic |
| **SWOW English** | 438 | 0.020 | -0.137 | Hyperbolic ✓ | Hyperbolic |
| **SWOW Dutch** | 500 | 7.56 | +0.099 | Spherical ✓ | Spherical |
| **ConceptNet EN** | 467 | 0.223 | -0.233 | Hyperbolic ✓ | Hyperbolic |
| **Depression** | 1634 | 0.118 | -0.130 | Hyperbolic ✓ | Hyperbolic |

**Bridge finding**: Dutch SWOW proves theory—first real network to cross phase boundary.

### Computational Details

| Method | Time (N=100) | Accuracy | Notes |
|--------|--------------|----------|-------|
| **Exact LP (HiGHS)** | 30 min | α-optimal | Reference standard |
| **Sinkhorn** | 2 min | ≈±0.02 bias | Solver tol: 1e-7 |
| **Hop-count** | 1 sec | — | Always agrees on sign |

---

## Lean 4 Formalization & Epistemic Rigor

**CRITICAL**: This project follows strict epistemological constraints (see `AI_DEFAULT_RULES.md`):
- **Knowledge** = Fully proven in Lean 4 (no sorry, no axioms except documented ones)
- **Truth** = Definitional equality (≡) or propositional equality (=) with explicit proof terms
- **Conjectures** = Empirically validated but not formally proven (clearly marked)

### Build Status

```bash
cd lean/HyperbolicSemanticNetworks
lake build
✔ [2735/2735] Built HyperbolicSemanticNetworks.HyperbolicSemanticNetworks

# Check axiom dependencies (MANDATORY for any mathematical claim)
lake env lean -e "#print axioms HyperbolicSemanticNetworks.Curvature.curvature_bounds"
```

**Proof Status Summary**:
- **Fully Proven** (0 sorry): 8 core theorems in Curvature, Basic, Wasserstein, WassersteinProven
- **Axiomatized** (5 core axioms): Wasserstein bounds (Villani 2009), clustering bounds (combinatorial)
- **Partially Proven** (86 sorry across 18 non-core modules): RicciFlow, SpectralGeometry, RandomGraph, etc.

**Key Distinction**:
- **Phase transition theorem** (regimes_exclusive): ✅ PROVEN — η < η_c ⟹ κ < 0; η > η_c ⟹ κ > 0
- **Phase transition empirical finding** (η_c = 3.75): ⚠️ EMPIRICAL CONJECTURE — validated on N∈{50,100,200,500,1000} but no asymptotic proof

### Core Theorems (0 sorry)

- `curvature_bounds`: κ ∈ [-1, 1] (boundedness)
- `regimes_exclusive`: η < η_c ⟹ κ < 0; η > η_c ⟹ κ > 0 (phase transition)
- `probabilityMeasure_normalization_proven`: ∑ᵢ π(i) = 1
- `wasserstein_symmetric_proven`: W(μ, ν) = W(ν, μ)

### Proof Status by Module

| Module | Proof Status | Sorry Count | Status |
|--------|-------------|------------|--------|
| **Basic.lean** | ✅ Core | 0 | Clustering bounds |
| **Wasserstein.lean** | ✅ Core | 0 | OT axioms (Villani) |
| **Curvature.lean** | ✅ Core | 0 | Main theorems |
| **PhaseTransition.lean** | Conjectures | 0 | Empirical validation |
| **Bounds.lean** | Partial | 2 | Spectral bounds |
| **Validation.lean** | Partial | 0 | Bridge proofs |
| **RandomGraph.lean** | Partial | 21 | Config model theory |
| **RicciFlow.lean** | Partial | 17 | Flow convergence |
| **SpectralGeometry.lean** | Partial | 20 | Eigenvalue bounds |

**To understand proof strategy**: Start with `Curvature.lean:277` (curvature_bounds) and `Curvature.lean:458` (regimes_exclusive).

---

## Important Caveats & Limitations

### Scientific

1. **Phase transition vs. crossover**: Terminology debate with refs:
   - Mitsche-Mubayi [16]: "sign change" (preferred)
   - Paper: "crossover" (finite N doesn't mean true phase)
   - Hehl [14]: Heuristic formula (not rigorous)

2. **Semantic network causality**: Two-parameter model (η + C) is **post-hoc**. Validation pending on new networks.

3. **Finite-size scaling**: R²=0.995 fit is excellent but only 5 points (N=50,100,200,500,1000).

4. **Sinkhorn bias**: Table 2 uses single seed s=42; noted in manuscript.

5. **LLY formula**: Uses α=0 (no idleness) vs ORC α=0.5; doesn't cross zero in tested range.

### Technical

1. **Julia FFI**: Rust library loaded via `ccall`. Ensure compiled with `cdylib` crate-type (already set in `Cargo.toml`).

2. **Lean sorry declarations**: 86 total. Core 7 modules have 0 sorry; auxiliary modules documented in [FORMALIZATION_STATUS.md](lean/FORMALIZATION_STATUS.md).

3. **Hypercomplex embedding**: No network retains hyperbolic curvature at sufficient embedding dimension (d≥8)—this is expected (Johnson-Lindenstrauss).

4. **ER k=2 edge case**: ER gives κ=-0.107 (sparse trees) vs regular κ=0 (cycles); noted separately.

5. **Null model comparison**: Semantic structure **reduces** curvature magnitude (Δκ>0); depression shows largest effect (75% reduction).

---

## Manuscript & Paper Details

### Files

- **Main**: `manuscript/latex/monograph.tex` (13 pages, 8 figures, 16 refs)
- **Markdown**: `manuscript/monograph.md` (for arXiv)
- **Figures**: `figures/monograph/figure{1..8}.{pdf,png}`
- **Tables**: 6 (N=100 transition, Sinkhorn, LLY, ER comparison, multi-N, Lean modules)

### Compile Instructions

```bash
cd manuscript/latex
pdflatex monograph.tex
pdflatex monograph.tex  # Twice for cross-refs
# Output: monograph.pdf
```

### Pre-submission Notes

- **Terminology**: "phase transition" → "crossover/sign change" (Feb 2026 revision)
- **Hypercomplex results**: Moved to Appendix E; dimensional hierarchy shows no network retains hyperbolicity
- **Hehl formula**: Heuristic (R²=-5.9 on paper data; not reliable)
- **η_c^∞**: Primary estimate β=0.5 gives 3.75≈3.7; free-β gives 4.20 (wider CI noted)
- **Solver metadata**: Appendix B lists tolerances, timing, memory

---

## Agent Context & Epistemological Rigor

**This is a research codebase with Q1-journal expectations** (see AGENTS.md & AI_DEFAULT_RULES.md). You are not just writing code—you are building an **epistemically rigorous system** for scientific discovery. Key principles:

### Knowledge Classification

- **[FORMALIZED]** — Proven in Lean 4 with explicit proof terms (0 sorry, no unsubstantiated axioms)
- **[CONDITIONAL]** — Empirically validated but proof depends on axioms (e.g., Wasserstein bounds from Villani 2009)
- **[EMPIRICAL]** — Discovered by experiment, validated on N∈{50,100,200,500,1000}, but no asymptotic proof
- **[VOID]** — Conjecture without evidence; clearly state what is unknown

### When Extending the Codebase

1. **Maintain proof inventory**: Every mathematical claim must be tagged as [FORMALIZED], [CONDITIONAL], [EMPIRICAL], or [VOID]
2. **Check Lean status** before making scientific claims: `lake build` must pass with documented sorry declarations
3. **Reproduce empirically** before claiming validity: Run the reference Julia scripts to confirm
4. **Cross-validate**: Verify results match across implementations (Julia vs Rust vs Python)

### What NOT to Do

- ❌ Claim results without numerical validation
- ❌ Break the Lean build (it's the source of truth for provability)
- ❌ Hide axioms or sorry declarations
- ❌ Modify key experiments without re-running full validation suite

---

## Development Workflow

### Before Starting Work

1. **Read governance documents** (⚠️ MANDATORY):
   - `AI_DEFAULT_RULES.md` — Epistemological constraints (knowledge vs conjecture distinction)
   - `AGENTS.md` — Project overview and agent guidance
   - This CLAUDE.md file — Architecture and common tasks

2. **Check memory**: `/home/demetrios/.claude/projects/.../memory/MEMORY.md` — contains stable patterns, recent architecture decisions, and key findings.

3. **Understand git state**: Run `git status` to see modified files (many PDFs expected to be modified).

4. **Verify environment**:
   ```bash
   julia --version    # Should be ≥1.9
   rustc --version    # Should be ≥1.70
   cargo --version
   ```

5. **Test Lean build** (if modifying proofs):
   ```bash
   cd lean/HyperbolicSemanticNetworks
   lake build         # Should complete with no errors
   ```

### Creating New Scripts

**Julia experiment script** location: `julia/scripts/`
**Name convention**: `{description}_{purpose}.jl` (e.g., `phase_transition_pure_julia.jl`)
**Template**:
```julia
using Pkg
Pkg.instantiate()

using Graphs, JSON, Statistics

# 1. Generate graph
g = random_regular_graph(100, 4)

# 2. Compute curvature
κ = compute_graph_curvature(g)

# 3. Save results to results/experiments/
results = Dict(
    "N" => 100,
    "k" => 4,
    "eta" => (4^2) / 100,
    "kappa_mean" => mean(κ)
)
open("results/experiments/my_experiment.json", "w") do f
    JSON.print(f, results)
end
```

**Python analysis** location: `code/analysis/`
**Use pytest**: Tests go in `code/analysis/tests/test_*.py`

### Commit Message Convention

```
feat(julia): add phase transition experiment for N=1000
fix(rust): correct Sinkhorn tolerance handling
docs(lean): explain proof of regimes_exclusive theorem
test(python): validate semantic network curvature computation
perf(rust): parallelize Wasserstein distance calculation
```

### Before Committing

- Run unit tests locally
- Verify figures regenerate correctly
- Check Lean builds without errors: `lake build`
- Lint Python: `make lint`

---

## When Things Go Wrong

### Julia Issues

**FFI not found**: Ensure Rust library compiled to `target/release/libcurvature.so` (or `.dylib` on macOS)
```bash
cd rust/curvature && cargo build --release
```

**Parallel processing hangs**: Start Julia with thread count: `julia -t 8 --project=julia`

**Dependency conflicts**: Clear and reinstall:
```bash
rm julia/Manifest.toml
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
```

### Rust Issues

**FFI test fails**: Verify `#[no_mangle]` and `extern "C"` on exposed functions.

**Clippy warnings**: Most are legit; fix before committing. Some false positives okay if documented.

### Lean Issues

**lake build timeouts**: Some modules take >30 sec. Increase timeout or build individual module:
```bash
cd lean/HyperbolicSemanticNetworks
lake build HyperbolicSemanticNetworks.Curvature
```

**Tactic timeout**: Add `set_option autoImplicit false` at top of file to catch missing binders.

### Python Issues

**Import errors**: Install in editable mode: `pip install -e .` (if package exists)

**Type errors**: Run `mypy code/analysis/ --ignore-missing-imports`

---

## Extending the Project

### Adding a New Semantic Network

1. **Prepare data**: Adjacency list or edge list (CSV with `source,target`)
2. **Place**: `data/processed/{network_name}.edgelist`
3. **Analyze**:
   ```julia
   include("julia/src/network_loader.jl")
   g = load_network("data/processed/{network_name}.edgelist")
   κ = compute_graph_curvature(g, alpha=0.5)
   ```
4. **Validate**: Compare with phase transition curve

### Adding a Lean Proof

1. **Identify theorem**: State it in appropriate module (e.g., `Curvature.lean` for curvature theorems)
2. **Structure proof**:
   ```lean
   theorem my_theorem (h : hypothesis) : conclusion := by
     rw [relevant_lemma]
     linarith  -- for algebraic goals
     -- or use 'sorry' if stuck, document in FORMALIZATION_STATUS.md
   ```
3. **Test**: `lake build` must pass
4. **Document**: Add line to FORMALIZATION_STATUS.md proof inventory

---

## References & Resources

### Key Papers

- **Ollivier-Ricci curvature**: arXiv:0712.3711 (Ollivier, 2009)
- **Hehl formula**: arXiv:2407.08854 (Moritz Hehl, 2025)
- **Phase transition**: This repo (in prep)
- **Sinkhorn algorithm**: Cuturi (2013)

### Documentation

- [README.md](README.md) — User overview
- [DEVELOPMENT.md](DEVELOPMENT.md) — Setup & contribution
- [lean/FORMALIZATION_STATUS.md](lean/FORMALIZATION_STATUS.md) — Proof inventory
- [manuscript/latex/monograph.tex](manuscript/latex/monograph.tex) — Full theory

### Related Codebases

- **Sounio**: Type-safe language with effect system (Sounio stdlib modules in `experiments/`)
- **sounio-lang/sounio** (GitHub clone): `~/work/sounio-lang/` — official compiler binary
- **Darwin Workspace**: Meta-project (configured in `.cursorrules`)

---

## Sounio Deep Integration (Phase 1 — Feb 2026)

The `experiments/01_deep_integration/` directory re-implements the full ORC computation
in pure Sounio, bypassing the Julia↔Rust FFI stack entirely.

### Compiler Setup

```bash
# Stable pre-built binary (beta.4):
SOUC="${HOME}/work/sounio-lang/artifacts/omega/souc-bin/souc-linux-x86_64-gpu"
"${SOUC}" --version   # souc 1.0.0-beta.4

# Run any .sio file:
"${SOUC}" run experiments/01_deep_integration/phase_transition_full.sio

# Orchestrated via run.sh:
bash experiments/01_deep_integration/run.sh [sparse_graph|bfs_dynamic|sinkhorn_adaptive|phase_transition_full]

# Bound the long N=100 sweep but keep partial CSV output:
SOUNIO_TIMEOUT_SECONDS=240 bash experiments/01_deep_integration/run.sh phase_transition_full
```

**CRITICAL compiler quirk**: `.exp()` method on f64 silently returns `()` with this binary.
Always use the `sc_exp(x)` Taylor-series function (copy from `sinkhorn_adaptive.sio`) instead.
Also note that `phase_transition_full.sio` is interpreter-heavy even after BFS-row caching; a
240-second bounded run has been verified through `k=14`, but the full 15-point table takes longer.

### Phase 1 Files (`experiments/01_deep_integration/`)

| File | Purpose | Validated |
|------|---------|-----------|
| [sparse_graph.sio](experiments/01_deep_integration/sparse_graph.sio) | CSR adjacency, N≤500 | ✅ |
| [bfs_dynamic.sio](experiments/01_deep_integration/bfs_dynamic.sio) | O(N) single-source BFS | ✅ |
| [sinkhorn_adaptive.sio](experiments/01_deep_integration/sinkhorn_adaptive.sio) | W1 with SinkhornConfig presets | ✅ |
| [phase_transition_full.sio](experiments/01_deep_integration/phase_transition_full.sio) | N=100 ORC sweep, 15 k-values, BFS-row cached | ⚠️ Long-running |
| [run.sh](experiments/01_deep_integration/run.sh) | Build & run orchestrator | ✅ |

### Sounio Effect System Quick Reference

```sounio
// Required effects:
fn my_fn() -> T with Mut, Div, Panic { ... }
//   Mut   — var mutation or &! mutable references
//   Div   — any division / modulo
//   Panic — bounds violation or explicit 0/0
//   IO    — print() / println()

// Fixed-size arrays only (no Vec/HashMap/generics):
struct Graph { adj: [usize; 30000], deg: [usize; 500], n: usize }

// Mutable pass-by-ref:  &! for write,  & for read
fn add_edge(g: &! Graph, u: usize, v: usize) with Mut, Panic { ... }

// NO .exp() → use sc_exp(x) (Taylor series, ~20 terms)
// NO closures, generics, dynamic dispatch
```

### Cross-Validation

```bash
# Sounio (fast, ε=0.1):
bash experiments/01_deep_integration/run.sh phase_transition_full
# → results/experiments/phase_transition_sounio_v1.csv

# Practical bounded validation:
SOUNIO_TIMEOUT_SECONDS=240 bash experiments/01_deep_integration/run.sh phase_transition_full
# Verified rows through k=14 within the bound.

# Julia reference (exact LP):
julia --project=julia julia/scripts/phase_transition_pure_julia.jl
# → results/experiments/phase_transition_pure_julia.json

# Current bounded verification: κ is negative through k=14 at N=100.
# Let the full sweep finish to inspect the k≥16 transition rows.
```

---

## Contact & Attribution

**Principal Investigator**: Dr. Demetrios Chiuratto Agourakis
**ORCID**: 0000-0002-8596-5097
**Email**: demetrios@agourakis.med.br

**If you are Claude Code extending this project**: Please maintain this file with new architecture decisions, verified key numbers, and common tasks.
