# For the Demetrios Designer: Complete Plan & Key Questions

## 🎯 Executive Summary

We've **discovered** a universal geometric phase transition in networks (⟨k⟩²/N ≈ 2.5) using Julia.

Now we want to **implement** this in **Demetrios** to:
1. ✅ Validate the scientific discovery
2. ✅ Showcase ALL Demetrios features (epistemic, effects, types, GPU)
3. ✅ Create THE flagship scientific application
4. ✅ Publish paper demonstrating type-safe epistemic computing

---

## 📊 What We've Discovered (Julia Implementation)

### The Phase Transition
```
⟨k⟩²/N < 2.5  →  Hyperbolic (κ < 0)  [Semantic networks live here]
⟨k⟩²/N ≈ 2.5  →  Transition (κ ≈ 0)   [Critical point]
⟨k⟩²/N > 3.5  →  Spherical (κ > 0)   [Dense networks]
```

### Validation
- ✅ Tested 11 synthetic networks (k=2 to k=50, N=200)
- ✅ Found exact transition: ⟨k⟩ ≈ 22.3
- ✅ Predicts Spanish/English/Chinese (all hyperbolic) perfectly
- ✅ Predicts Dutch (spherical) perfectly
- ✅ Computation time: 0.6 seconds (Julia, 32 threads)

### Files Created
- `PHASE_TRANSITION_DISCOVERY.md` - Complete scientific findings
- `DEEP_SCIENCE_ANALYSIS.md` - Mathematical foundations
- `SCIENTIFIC_DISCOVERIES.md` - Implications and beauty
- `RESEARCH_ROADMAP.md` - Future experiments
- `phase_transition_pure_julia.jl` - Working implementation
- `results/experiments/phase_transition_pure_julia.json` - Data

---

## 🏗️ What We Want to Build in Demetrios

### Module Structure
```
stdlib/graph/
├── types.d           # Core graph types
├── algorithms.d      # BFS, shortest paths
├── sinkhorn.d        # Optimal transport (Wasserstein)
├── curvature.d       # Ollivier-Ricci curvature
├── random.d          # Random graph generation
├── stats.d           # Network statistics
└── mod.d             # Module exports

examples/network_geometry/
├── phase_transition.d      # Main experiment
├── analyze_network.d       # Real network analysis
├── parallel_demo.d         # Parallel curvature
└── gpu_demo.d              # GPU version (if ready)
```

### Complete API Design
See `DEMETRIOS_INTEGRATION_PLAN.md` for full API with:
- Graph data structures
- All algorithms (BFS, Sinkhorn, Ollivier-Ricci)
- Random graph generation
- Phase transition experiment
- Effect annotations
- Epistemic types

---

## 🔑 KEY DESIGN QUESTIONS FOR YOU

These are decisions only you (as language designer) can make:

### 1. Epistemic Computing Integration

**Question:** How should curvature confidence be computed?

**Context:** Each edge curvature κ is a measurement with uncertainty. When we compute mean across edges, how does confidence propagate?

**Options:**
```d
// Option A: Sample-based (Bootstrap)
let kappa: Curvature with Confidence = measure(edge);
// confidence from bootstrap samples

// Option B: Analytical
let kappa: Curvature with Confidence = measure(edge);
// confidence from Sinkhorn convergence variance

// Option C: User-specified
let kappa = Knowledge::new(
    value: measure(edge),
    confidence: user_specified,
    source: Source::Computation("Ollivier-Ricci")
);
```

**My recommendation:** Option B (analytical) + Option C (fallback)

**Your decision needed:**
- Is epistemic computing fully implemented?
- How should confidence combine in parallel_map?
- Should we compute multiple samples or single value + confidence?

---

### 2. Linear Types for Matrices

**Question:** Should cost matrices be linear to prevent copying?

**Context:** Cost matrices in Sinkhorn are N×N, potentially large. Linear types prevent accidental copies.

**Proposed API:**
```d
fn sinkhorn_wasserstein(
    mu: Vec<f64>,
    nu: Vec<f64>,
    cost: Matrix<f64> linear,  // <-- Linear type!
    epsilon: f64,
    max_iter: usize
) -> f64
```

**Benefits:**
- Memory safe (no accidental 10GB copy)
- Performance (no copying overhead)
- Explicit resource management

**Trade-off:**
- More restrictive API
- Caller must reconstruct if needed multiple times

**Your decision needed:**
- Are linear types fully working?
- Should we use them for this use case?
- What's the syntax? (`linear`, `@linear`, something else?)

---

### 3. Effect System Granularity

**Question:** How fine-grained should effect tracking be?

**Context:** Our functions have many effects. How should we annotate them?

**Options:**
```d
// Option A: Fine-grained (explicit everything)
fn phase_transition() -> Results
    with Parallel, Alloc, Random, Confidence, IO

// Option B: Coarse-grained (bundle common effects)
fn phase_transition() -> Results
    with Scientific  // implies Alloc, Random, Confidence

// Option C: Minimal (only unusual effects)
fn phase_transition() -> Results
    with Parallel, IO  // Alloc assumed

// Option D: Effect inference
fn phase_transition() -> Results {
    // Compiler infers effects
}
```

**My recommendation:** Option A for now (explicit), Option D long-term (inference)

**Your decision needed:**
- What's the current effect system status?
- Should we define custom effect bundles?
- Is effect inference on the roadmap?

---

### 4. Refinement Types vs Runtime Checks

**Question:** How should we enforce graph preconditions?

**Context:** `random_regular_graph(n, k)` requires `k * n % 2 == 0`. How to enforce?

**Options:**
```d
// Option A: Refinement type (SMT)
fn random_regular_graph(
    n: Count,
    k: {x: Degree | x * n % 2 == 0}  // SMT solver checks
) -> Graph

// Option B: Runtime require
fn random_regular_graph(n: Count, k: Degree) -> Graph {
    require k * n % 2 == 0;  // Runtime check
    // ...
}

// Option C: Result type
fn random_regular_graph(n: Count, k: Degree)
    -> Result<Graph, GraphError>

// Option D: Panic
fn random_regular_graph(n: Count, k: Degree) -> Graph {
    assert!(k * n % 2 == 0, "k*n must be even");
    // ...
}
```

**My recommendation:** Option B (require) for now, Option A (refinement) later

**Your decision needed:**
- Is SMT integration working?
- What's the performance cost of refinement types?
- Should we use Result for validation or panic?

---

### 5. Parallel Map Semantics

**Question:** How does parallel_map interact with epistemic types?

**Context:** We compute curvatures in parallel. Each has confidence. How combine?

**Scenario:**
```d
let curvatures: Vec<Curvature with Confidence> =
    edges.parallel_map(|e| {
        compute_curvature(e) with Confidence
    }) with Parallel;

let mean: Curvature with Confidence = curvatures.mean();
```

**Questions:**
- Does parallel_map preserve epistemic annotations?
- How is confidence combined in mean()?
- Should we run multiple parallel samples for better confidence?

**Your decision needed:**
- Current parallel + epistemic interaction?
- Should parallel operations affect confidence?
- Performance implications?

---

### 6. GPU Integration Strategy

**Question:** When/how should we add GPU support?

**Context:** Curvature computation is embarrassingly parallel. Perfect for GPU.

**Options:**
```d
// Option A: GPU kernel (if ready)
kernel fn compute_curvatures_gpu(
    graph: GPUGraph,
    edges: GPUSlice<Edge>,
    output: GPUSlice<Curvature>
) {
    let idx = thread_id();
    output[idx] = ollivier_ricci_gpu(graph, edges[idx]);
}

// Option B: Automatic (compiler decides)
let curvatures = edges.parallel_map(|e| compute(e))
    with GPU;  // Compiler generates GPU kernel

// Option C: Later (CPU first)
// Implement CPU version first, GPU later
```

**My recommendation:** Option C (CPU first), then Option A (explicit kernels)

**Your decision needed:**
- Is GPU codegen working?
- Should we target this for Week 6 (optimization)?
- What GPU architectures? (CUDA, OpenCL, both?)

---

### 7. Units of Measure Implementation

**Question:** Are units of measure fully working?

**Context:** We want to use dimensional types everywhere:

```d
type Curvature = f64 : dimensionless
type Degree = usize : dimensionless
type Distance = usize : dimensionless
type Ratio = f64 : dimensionless

let ratio: Ratio = (k: Degree * k: Degree) / (n: Count);
```

**Your decision needed:**
- Are units fully implemented?
- Can we mix numeric types (usize, f64) with units?
- Performance cost of unit checking?
- Should we use this extensively or sparingly?

---

### 8. Error Handling Philosophy

**Question:** Result vs exceptions vs panics?

**Context:** Many operations can fail (file I/O, graph operations, numerical issues)

**Options:**
```d
// Option A: Result types (Rust-style)
fn load_graph(path: string) -> Result<Graph, GraphError>
    with IO

// Option B: Effects as errors (algebraic effects)
fn load_graph(path: string) -> Graph
    with IO, Panic

// Option C: Exceptions
fn load_graph(path: string) -> Graph
    with IO
    throws GraphException

// Option D: Panics
fn load_graph(path: string) -> Graph with IO {
    if !file_exists(path) {
        panic!("File not found: {}", path);
    }
}
```

**My recommendation:** Option A (Result) for recoverable, Option D (panic) for invariants

**Your decision needed:**
- What's the Demetrios error handling story?
- Should we use algebraic effects for errors?
- Performance implications of Result?

---

## 📅 Timeline & Milestones

### Week 1 (Dec 23-29): Foundation
**Goal:** Understand Demetrios, create basic graph structure

**Your input needed:**
- Compiler setup guidance
- Feature availability confirmation
- API design review

**Deliverable:** First graph program in Demetrios

---

### Week 2 (Dec 30 - Jan 5): Core Algorithms
**Goal:** Implement Sinkhorn and curvature

**Your input needed:**
- Linear type integration
- Effect system guidance
- Performance optimization hints

**Deliverable:** Curvature computation working

---

### Week 3 (Jan 6-12): Random Graphs
**Goal:** Graph generation with refinement types

**Your input needed:**
- Refinement type integration
- Random effect semantics
- Precondition checking strategy

**Deliverable:** Random graph generation working

---

### Week 4 (Jan 13-19): Phase Transition
**Goal:** Full experiment with parallelism

**Your input needed:**
- Parallel + epistemic interaction
- Performance tuning
- Result interpretation

**Deliverable:** Phase transition found in Demetrios

---

### Week 5 (Jan 20-26): Real Networks
**Goal:** Analyze SWOW languages

**Your input needed:**
- I/O integration
- Error handling strategy
- Data pipeline design

**Deliverable:** All networks analyzed

---

### Week 6-8 (Jan 27 - Feb 16): Paper & Polish
**Goal:** Optimization, documentation, publication

**Your input needed:**
- Compiler optimization features
- GPU integration (if ready)
- Paper review (language sections)

**Deliverable:** Published paper

---

## 🎯 Success Criteria

### Must Have
- [ ] Phase transition found (⟨k⟩²/N ≈ 2.5)
- [ ] Results match Julia
- [ ] Demonstrates epistemic computing
- [ ] Demonstrates effect system
- [ ] Demonstrates units of measure

### Should Have
- [ ] Performance < 5× Julia
- [ ] All Demetrios features used
- [ ] Comprehensive documentation
- [ ] Reusable graph library

### Nice to Have
- [ ] GPU acceleration
- [ ] Published paper
- [ ] Community adoption

---

## 🤝 What I Need From You

### Immediate (This Week)
1. **Compiler access** - How do I build/run Demetrios programs?
2. **Feature confirmation** - Which features are working?
3. **API design approval** - Review `DEMETRIOS_INTEGRATION_PLAN.md`
4. **First design decisions** - Answer 1-2 key questions above

### Ongoing (Weekly)
1. **Design reviews** - Approve API changes
2. **Feature additions** - Add capabilities as we discover needs
3. **Bug reports** - I'll find issues, you can fix
4. **Performance guidance** - Optimization strategies

### End Goal (February)
1. **Paper co-authorship** - Write language design sections
2. **Publicity** - Announce flagship application
3. **Community** - Help promote Demetrios + network geometry

---

## 💡 Why This is Perfect for Demetrios

### Showcases Unique Features
1. **Epistemic Computing** - No other language has this
2. **Effect System** - Makes side effects explicit and safe
3. **Units of Measure** - Prevents dimensional errors
4. **Linear Types** - Memory safety without GC
5. **Refinement Types** - SMT-backed correctness
6. **GPU-Native** - First-class GPU support

### Solves Real Problem
- Not a toy example
- Publishable science
- Validates real networks
- Discovers new laws

### Builds Community
- Scientists need type safety
- Network analysis is common
- Reusable library
- Tutorial for others

---

## 🚀 Let's Build This Together!

**Your role:** Design the language features we need
**My role:** Implement and validate the algorithms
**Together:** Create the flagship scientific application for Demetrios

**Next steps:**
1. You confirm which features are ready
2. I start implementing basic graph structure
3. We iterate on API design
4. We build toward the phase transition experiment

**Questions?** Let's discuss any of the 8 key design questions above!

**Ready?** Let's make Demetrios THE language for type-safe scientific computing! 🎯🔬✨

---

*Created: 2025-12-23*
*Status: Awaiting designer input on key questions*
*Goal: Ship network geometry library in 8 weeks*
