# Demetrios Integration: Network Geometry Library

## Executive Summary

**Objective:** Implement hyperbolic network geometry algorithms in Demetrios, showcasing:
- Epistemic computing for uncertainty propagation
- Algebraic effects for explicit side effects
- Units of measure for geometric quantities
- Linear types for memory safety
- Parallel computing for performance

**Scientific Goal:** Validate phase transition at ⟨k⟩²/N ≈ 2.5 using type-safe epistemic computing

**Language Goal:** Make network geometry THE flagship scientific application for Demetrios

---

## I. ASSESSMENT (Complete)

### ✅ What Demetrios Has
- [x] Compiler infrastructure (Rust-based)
- [x] Effect system (`with Alloc`, `with IO`, `with Prob`)
- [x] Units of measure (dimensional analysis)
- [x] Epistemic computing framework
- [x] Linear algebra (`linalg::Matrix`, BLAS/LAPACK)
- [x] Numerical methods (ODE, optimization)
- [x] Probabilistic programming (distributions, MCMC)
- [x] FFI support (Julia, Python interop)
- [x] GPU support (kernel syntax)
- [x] VS Code LSP integration

### 🔧 What We Need to Add
- [ ] Graph data structures
- [ ] Graph algorithms (BFS, shortest paths)
- [ ] Optimal transport (Sinkhorn algorithm)
- [ ] Ollivier-Ricci curvature computation
- [ ] Random graph generation (configuration model)
- [ ] Network statistics (clustering, degree distribution)

### 💡 Unique Demetrios Advantages
1. **Epistemic Computing**: Uncertainty in κ propagates automatically
2. **Effect Tracking**: `with Parallel, Alloc, Random` explicit
3. **Units**: `Curvature`, `Degree`, `Distance` type-safe
4. **Linear Types**: Cost matrices can't be accidentally copied
5. **GPU-Native**: Parallel curvature computation

---

## II. API DESIGN

### Core Types

```d
module graph

use units::{dimensionless}

// Dimensional types
type NodeId = usize : dimensionless
type Degree = usize : dimensionless
type Count = usize : dimensionless
type Distance = usize : dimensionless
type Curvature = f64 : dimensionless
type Probability = f64 : dimensionless
type Ratio = f64 : dimensionless

// Graph structure
struct Graph {
    n_nodes: Count,
    adjacency: Vec<Vec<NodeId>>,  // Adjacency lists
    edges: Vec<Edge>
}

struct Edge {
    u: NodeId,
    v: NodeId
}

// Probability measure for curvature
struct Measure {
    support: Vec<NodeId>,
    probabilities: Vec<Probability>
}

// Network metrics with epistemic types
struct NetworkMetrics with Confidence {
    n_nodes: Count,
    n_edges: Count,
    avg_degree: Degree with Confidence,
    clustering: f64 with Confidence,
    kappa_mean: Curvature with Confidence,
    kappa_std: Curvature with Confidence,
    geometry: Geometry
}

enum Geometry {
    Hyperbolic,
    Euclidean,
    Spherical
}
```

### Graph Construction

```d
impl Graph {
    /// Create empty graph
    fn new(n: Count) -> Graph with Alloc {
        Graph {
            n_nodes: n,
            adjacency: vec![vec![]; n],
            edges: vec![]
        }
    }

    /// Add undirected edge
    fn add_edge(mut self, u: NodeId, v: NodeId) -> Graph {
        require u < self.n_nodes;
        require v < self.n_nodes;

        self.adjacency[u].push(v);
        self.adjacency[v].push(u);
        self.edges.push(Edge { u, v });
        self
    }

    /// Get neighbors of node
    fn neighbors(&self, u: NodeId) -> &[NodeId] {
        require u < self.n_nodes;
        &self.adjacency[u]
    }

    /// Degree of node
    fn degree(&self, u: NodeId) -> Degree {
        require u < self.n_nodes;
        self.adjacency[u].len()
    }
}
```

### Graph Algorithms

```d
/// Breadth-first search to compute distances
fn bfs_distances(g: &Graph, source: NodeId) -> Vec<Distance> with Alloc {
    require source < g.n_nodes;

    let mut dist = vec![Distance::MAX; g.n_nodes];
    let mut queue = VecDeque::new() with Alloc;

    dist[source] = 0;
    queue.push_back(source);

    while let Some(u) = queue.pop_front() {
        for &v in g.neighbors(u) {
            if dist[v] == Distance::MAX {
                dist[v] = dist[u] + 1;
                queue.push_back(v);
            }
        }
    }

    dist
}

/// All-pairs shortest paths (for cost matrix)
fn all_pairs_shortest_paths(g: &Graph) -> Matrix<Distance> linear with Alloc {
    let n = g.n_nodes;
    let mut dist_matrix = Matrix::zeros(n, n) with Alloc;

    for u in 0..n {
        let distances = bfs_distances(g, u);
        for v in 0..n {
            dist_matrix[u, v] = distances[v];
        }
    }

    dist_matrix  // Linear: consumed, can't be copied
}
```

### Sinkhorn Algorithm (Optimal Transport)

```d
/// Compute Wasserstein-1 distance via Sinkhorn algorithm
fn sinkhorn_wasserstein(
    mu: Vec<Probability>,
    nu: Vec<Probability>,
    cost: Matrix<f64> linear,  // Linear type prevents copying!
    epsilon: f64,
    max_iter: Count
) -> f64 with Alloc {
    require mu.len() == nu.len();
    require cost.rows() == mu.len();
    require epsilon > 0.0;

    let n = mu.len();
    let mut u = vec![1.0; n] with Alloc;
    let mut v = vec![1.0; n] with Alloc;

    // Kernel matrix
    let K = cost.map(|c| (-c / epsilon).exp());

    // Sinkhorn iterations
    for iter in 0..max_iter {
        let u_old = u.clone();

        // Update scaling vectors
        u = mu.element_wise_div(&(K.matmul(&v)));
        v = nu.element_wise_div(&(K.transpose().matmul(&u)));

        // Check convergence
        if iter % 10 == 0 {
            let diff = u.sub(&u_old).l1_norm();
            if diff < 1e-6 {
                break;
            }
        }
    }

    // Compute transport plan
    let P = Matrix::diag(&u).matmul(&K).matmul(&Matrix::diag(&v));

    // Wasserstein distance = <P, C>
    P.element_wise_mul(&cost).sum()
}
```

### Ollivier-Ricci Curvature

```d
/// Build probability measure for Ollivier-Ricci curvature
fn probability_measure(
    g: &Graph,
    u: NodeId,
    alpha: f64
) -> Measure with Alloc {
    require 0.0 <= alpha && alpha <= 1.0;
    require u < g.n_nodes;

    let mut measure = Measure {
        support: vec![u],
        probabilities: vec![alpha]
    };

    let neighbors = g.neighbors(u);
    if neighbors.len() > 0 {
        let neighbor_prob = (1.0 - alpha) / neighbors.len() as f64;

        for &v in neighbors {
            measure.support.push(v);
            measure.probabilities.push(neighbor_prob);
        }
    }

    measure
}

/// Compute Ollivier-Ricci curvature for an edge
fn ollivier_ricci_curvature(
    g: &Graph,
    edge: Edge,
    alpha: f64
) -> Curvature with Confidence, Alloc {
    // Build probability measures
    let mu = probability_measure(g, edge.u, alpha);
    let nu = probability_measure(g, edge.v, alpha);

    // Get all nodes in support
    let mut all_nodes = mu.support.clone();
    all_nodes.extend(&nu.support);
    all_nodes.sort();
    all_nodes.dedup();

    let n = all_nodes.len();
    let node_to_idx: HashMap<NodeId, usize> = all_nodes.iter()
        .enumerate()
        .map(|(i, &node)| (node, i))
        .collect();

    // Build probability vectors
    let mut mu_vec = vec![0.0; n];
    let mut nu_vec = vec![0.0; n];

    for (node, prob) in mu.support.iter().zip(&mu.probabilities) {
        mu_vec[node_to_idx[node]] = *prob;
    }

    for (node, prob) in nu.support.iter().zip(&nu.probabilities) {
        nu_vec[node_to_idx[node]] = *prob;
    }

    // Build cost matrix (shortest path distances)
    let mut cost = Matrix::zeros(n, n) linear with Alloc;
    for i in 0..n {
        let node_i = all_nodes[i];
        let distances = bfs_distances(g, node_i);

        for j in 0..n {
            let node_j = all_nodes[j];
            cost[i, j] = distances[node_j] as f64;
        }
    }

    // Compute Wasserstein distance
    let W1 = sinkhorn_wasserstein(mu_vec, nu_vec, cost, 0.01, 1000);

    // Curvature formula: κ = 1 - W₁/d(u,v)
    let d_uv = 1.0;  // Edge distance
    let kappa = 1.0 - W1 / d_uv;

    // Return with epistemic confidence
    // (For now, placeholder - will integrate proper uncertainty later)
    Knowledge::new(
        value: kappa,
        confidence: 0.95,
        source: Source::Computation("Ollivier-Ricci")
    )
}
```

### Parallel Curvature Computation

```d
/// Compute curvature for all edges (parallel)
fn compute_graph_curvature(
    g: &Graph,
    alpha: f64
) -> Vec<(Edge, Curvature with Confidence)>
    with Parallel, Alloc, Confidence
{
    g.edges.parallel_map(|edge| {
        let kappa = ollivier_ricci_curvature(g, *edge, alpha)
            with Confidence, Alloc;
        (*edge, kappa)
    }).collect() with Alloc
}

/// Compute statistics from curvature distribution
fn curvature_statistics(
    curvatures: Vec<Curvature with Confidence>
) -> (Curvature with Confidence, Curvature with Confidence)
    with Confidence
{
    let mean = curvatures.mean() with Confidence;  // Epistemic!
    let std = curvatures.std() with Confidence;    // Epistemic!
    (mean, std)
}
```

### Random Graph Generation

```d
/// Generate random k-regular graph (configuration model)
fn random_regular_graph(
    n: Count,
    k: Degree
) -> Graph with Random, Alloc {
    require k * n % 2 == 0;  // Refinement type!
    require k < n;

    // Create degree sequence
    let mut stubs: Vec<NodeId> = vec![] with Alloc;
    for node in 0..n {
        for _ in 0..k {
            stubs.push(node);
        }
    }

    // Shuffle stubs
    stubs.shuffle() with Random;

    // Pair stubs to create edges
    let mut g = Graph::new(n) with Alloc;

    for i in (0..stubs.len()).step_by(2) {
        let u = stubs[i];
        let v = stubs[i+1];

        // Skip self-loops and duplicate edges
        if u != v && !g.has_edge(u, v) {
            g = g.add_edge(u, v);
        }
    }

    // Extract largest connected component
    g.largest_connected_component() with Alloc
}
```

### Phase Transition Experiment

```d
/// Phase point in the transition
struct PhasePoint with Confidence {
    k: Degree,
    ratio: Ratio,
    kappa_mean: Curvature with Confidence,
    kappa_std: Curvature with Confidence,
    geometry: Geometry
}

/// Run phase transition experiment
fn phase_transition_experiment(
    N: Count,
    k_values: Vec<Degree>
) -> Vec<PhasePoint> with Confidence
    with Parallel, Alloc, Random, IO
{
    println!("Starting phase transition experiment...");
    println!("N = {}, testing {} values of k", N, k_values.len());

    k_values.parallel_map(|k| {
        println!("  Testing k = {}...", k);

        // Generate random graph
        let g = random_regular_graph(N, *k) with Random, Alloc;

        // Compute curvatures (parallel!)
        let curvatures = compute_graph_curvature(&g, 0.5)
            with Parallel, Alloc, Confidence;

        // Extract just the curvature values
        let kappa_values: Vec<_> = curvatures.iter()
            .map(|(_, kappa)| *kappa)
            .collect();

        // Statistics (epistemic computing automatically propagates uncertainty!)
        let (kappa_mean, kappa_std) = curvature_statistics(kappa_values)
            with Confidence;

        // Compute ratio
        let ratio = (*k as f64 * *k as f64) / N as f64;

        // Classify geometry
        let geometry = if kappa_mean.value < -0.05 {
            Geometry::Hyperbolic
        } else if kappa_mean.value > 0.05 {
            Geometry::Spherical
        } else {
            Geometry::Euclidean
        };

        println!("  k={}: κ={:.4} ± {:.4}, geometry={:?}",
                 k, kappa_mean.value, kappa_std.value, geometry);

        PhasePoint {
            k: *k,
            ratio: ratio,
            kappa_mean: kappa_mean,
            kappa_std: kappa_std,
            geometry: geometry
        }
    }).collect() with Alloc
}
```

---

## III. IMPLEMENTATION ROADMAP

### Week 1: Foundation
**Files to create:**
- `stdlib/graph/mod.d` - Graph module
- `stdlib/graph/types.d` - Core types
- `stdlib/graph/algorithms.d` - BFS, shortest paths

**Tasks:**
- [x] Design API (this document)
- [ ] Implement Graph struct
- [ ] Implement BFS
- [ ] Test against Julia reference

**Success**: Graph creation and BFS match Julia

### Week 2: Curvature Core
**Files to create:**
- `stdlib/graph/sinkhorn.d` - Wasserstein distance
- `stdlib/graph/curvature.d` - Ollivier-Ricci

**Tasks:**
- [ ] Implement Sinkhorn algorithm
- [ ] Implement probability measures
- [ ] Implement Ollivier-Ricci curvature
- [ ] Validate against Julia (ε < 1e-6)

**Success**: Curvature values match Julia

### Week 3: Random Graphs
**Files to create:**
- `stdlib/graph/random.d` - Random graph generation

**Tasks:**
- [ ] Configuration model
- [ ] Random regular graphs
- [ ] Connected component extraction
- [ ] Statistical validation

**Success**: Degree distributions correct

### Week 4: Phase Transition
**Files to create:**
- `examples/network_geometry/phase_transition.d`
- `examples/network_geometry/validation.d`

**Tasks:**
- [ ] Full phase transition experiment
- [ ] Compare to Julia results
- [ ] Validate ⟨k⟩²/N ≈ 2.5 transition

**Success**: Transition found, matches Julia

### Week 5: Real Networks
**Files to create:**
- `examples/network_geometry/load_swow.d`
- `examples/network_geometry/analyze.d`

**Tasks:**
- [ ] CSV loading
- [ ] SWOW network construction
- [ ] Full analysis pipeline
- [ ] Validate Spanish/English/Chinese/Dutch

**Success**: All networks analyzed correctly

---

## IV. FEATURES SHOWCASED

### 1. Epistemic Computing
```d
// Uncertainty propagates automatically!
let kappa1: Curvature with Confidence = measure(edge1);
let kappa2: Curvature with Confidence = measure(edge2);
let mean: Curvature with Confidence = [kappa1, kappa2].mean();
// mean.confidence is automatically computed correctly!
```

### 2. Effect System
```d
fn experiment() -> Results
    with Parallel,    // Parallel execution
         Alloc,       // Memory allocation
         Random,      // Randomness
         Confidence,  // Epistemic
         IO           // I/O operations
{
    // All side effects explicitly tracked!
}
```

### 3. Units of Measure
```d
let k: Degree = 10;
let N: Count = 200;
let ratio: Ratio = (k * k) / N;  // Type-checked!
// let bad: Curvature = k + N;   // Compile error!
```

### 4. Linear Types
```d
let cost: Matrix<f64> linear = build_cost_matrix(...);
// cost can only be used once - no accidental copying!
let W1 = sinkhorn(mu, nu, cost);
// cost is consumed, can't use again
```

### 5. Refinement Types
```d
fn random_regular(n: Count, k: {k: Degree | k * n % 2 == 0})
    -> Graph
{
    // SMT solver ensures k*n is even at compile time!
}
```

### 6. Parallel Computing
```d
let curvatures = edges.parallel_map(|e| {
    compute_curvature(e) with Alloc, Confidence
}) with Parallel, Alloc;
// Parallelism explicit and type-safe!
```

---

## V. SUCCESS METRICS

### Minimum Success
- [ ] Graph data structure compiles
- [ ] BFS works, matches Julia
- [ ] One edge curvature computed
- [ ] Demonstrates epistemic computing

### Target Success
- [ ] Full phase transition experiment
- [ ] Transition at ⟨k⟩²/N ≈ 2.5 found
- [ ] All results match Julia
- [ ] Performance within 5× Julia
- [ ] All Demetrios features used

### Stretch Success
- [ ] GPU acceleration working
- [ ] 10-100× speedup
- [ ] Paper published featuring Demetrios
- [ ] Contributed to Demetrios stdlib
- [ ] Tutorial documentation

---

## VI. NEXT STEPS

**Immediate Actions:**
1. Build Demetrios compiler
2. Run existing examples
3. Start implementing `stdlib/graph/` module
4. Create test suite against Julia

**You Design, I Implement:**
- You make architectural decisions as we discover needs
- I implement and test
- We iterate based on what works

**Goal:** Ship network geometry library in Demetrios by Week 5! 🚀

Ready to start building!
