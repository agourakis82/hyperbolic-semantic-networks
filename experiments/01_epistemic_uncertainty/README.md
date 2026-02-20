# Experiment 1: Epistemic Uncertainty in Curvature Estimates

**Status**: Design phase
**Sounio Advantage**: Automatic uncertainty propagation through epistemic computing

---

## Scientific Question

**How does curvature uncertainty vary with network size, density, and measurement quality?**

Specifically:
1. Does uncertainty decrease with network size (N)?
2. Does uncertainty increase near the phase transition?
3. Can we quantify confidence in geometry classification?
4. How does Sinkhorn convergence affect uncertainty?

---

## Hypothesis

**H1**: Larger networks yield higher confidence curvature estimates
- More edges → better statistics → lower uncertainty

**H2**: Transition zone (⟨k⟩²/N ≈ 2.5) has highest uncertainty
- κ ≈ 0 → small changes matter → higher uncertainty

**H3**: Sinkhorn convergence directly correlates with epistemic confidence
- Better convergence → higher confidence

---

## Experimental Design

### Phase 1: Synthetic Networks

Generate random regular graphs with varying parameters:

| Parameter | Values | Purpose |
|-----------|--------|---------|
| N (nodes) | 50, 100, 200, 500 | Test size effect |
| k (degree) | 3, 10, 22, 30, 40 | Span phase transition |
| α (laziness) | 0.0, 0.5 | Standard vs lazy walk |
| ε (Sinkhorn) | 0.01, 0.1 | Regularization effect |

**Total**: 4 × 5 × 2 × 2 = 80 network configurations
**Replicates**: 10 per configuration = **800 measurements**

### Phase 2: Real Networks

Apply to semantic networks:
- Spanish SWOW (N=9,246, ⟨k⟩=3.0)
- English SWOW (N=10,571, ⟨k⟩=3.1)
- Chinese SWOW (N=8,857, ⟨k⟩=3.2)
- Dutch SWOW (N=2,962, ⟨k⟩=61.6)

Compare epistemic uncertainty across languages.

---

## Implementation

### Sounio Code

```d
module experiments::epistemic_uncertainty

use graph::types::{Graph, NetworkStats};
use graph::curvature::{mean_curvature_epistemic, CurvatureParams};
use graph::random::random_regular_graph;

// Epistemic result with full uncertainty tracking
pub struct EpistemicResult {
    pub n: usize,
    pub k: usize,
    pub ratio: f64,
    pub kappa_value: f64,
    pub kappa_uncertainty: f64,
    pub confidence: f64,
    pub geometry: Geometry,
    pub sinkhorn_iters: usize,
}

// Run single trial with epistemic tracking
pub fn run_trial(n: usize, k: usize, params: CurvatureParams)
    -> EpistemicResult with Alloc, Random, Confidence {

    // Generate network
    let g = random_regular_graph(n, k, 100).unwrap();

    // Compute stats
    let stats = NetworkStats::from_graph(&g);

    // Compute curvature WITH epistemic tracking
    let kappa = mean_curvature_epistemic(&g, params);

    EpistemicResult {
        n,
        k,
        ratio: stats.sparsity_ratio,
        kappa_value: kappa.value(),
        kappa_uncertainty: kappa.uncertainty(),  // ← Automatic from Sounio!
        confidence: kappa.confidence(),          // ← Automatic confidence level
        geometry: Geometry::from_curvature(kappa.value()),
        sinkhorn_iters: kappa.metadata().iterations,
    }
}

// Run full experiment sweep
pub fn run_experiment() -> [EpistemicResult] with Alloc, Random, Confidence {
    let n_values = [50, 100, 200, 500];
    let k_values = [3, 10, 22, 30, 40];
    let alpha_values = [0.0, 0.5];
    let epsilon_values = [0.01, 0.1];

    var results: [EpistemicResult] = [];

    // Sweep parameters
    for n in n_values {
        for k in k_values {
            for alpha in alpha_values {
                for epsilon in epsilon_values {
                    let params = CurvatureParams {
                        alpha,
                        epsilon,
                        max_iter: 1000,
                    };

                    // 10 replicates per configuration
                    var rep: usize = 0;
                    while rep < 10 {
                        let result = run_trial(n, k, params);
                        results.push(result);
                        rep = rep + 1;
                    }
                }
            }
        }
    }

    results
}
```

### Comparison: Julia Bootstrap

```julia
# Compare Sounio epistemic uncertainty to bootstrap confidence intervals
using Statistics, Bootstrap

function bootstrap_curvature(g::Graph, n_samples=1000)
    edge_curvatures = compute_all_curvatures(g)

    # Bootstrap resample
    bootstrap_means = [
        mean(sample(edge_curvatures, length(edge_curvatures)))
        for _ in 1:n_samples
    ]

    mean_κ = mean(edge_curvatures)
    ci = quantile(bootstrap_means, [0.025, 0.975])

    return (
        mean = mean_κ,
        lower = ci[1],
        upper = ci[2],
        uncertainty = (ci[2] - ci[1]) / 4  # ~95% CI → std
    )
end
```

**Question**: Does Sounio epistemic uncertainty match bootstrap uncertainty?

---

## Measurements

### Primary Outcomes

1. **κ_value** - Mean curvature
2. **κ_uncertainty** - Epistemic uncertainty (from Sounio)
3. **confidence** - Confidence level (0-1)
4. **geometry** - Classification (Hyperbolic/Euclidean/Spherical)

### Secondary Outcomes

5. **sinkhorn_iters** - Convergence iterations
6. **sinkhorn_residual** - Final residual
7. **execution_time** - Wall clock time
8. **memory_usage** - Peak memory

### Derived Metrics

9. **uncertainty_vs_N** - Does uncertainty ∝ 1/√N?
10. **uncertainty_vs_ratio** - Peak at ⟨k⟩²/N ≈ 2.5?
11. **confidence_vs_geometry** - Higher for extreme geometries?
12. **epistemic_vs_bootstrap** - Correlation with Julia bootstrap?

---

## Analysis Plan

### Statistical Tests

1. **Effect of N on uncertainty**:
   - Linear regression: log(uncertainty) ~ log(N)
   - Expected slope: -0.5 (1/√N scaling)

2. **Uncertainty peak at transition**:
   - Compare uncertainty for ratio < 2, 2-3, > 3
   - ANOVA: Is transition zone significantly higher?

3. **Confidence calibration**:
   - Compare Sounio confidence to bootstrap coverage
   - "95% confidence" should cover true value 95% of time

4. **Sinkhorn convergence effect**:
   - Correlation: iterations vs uncertainty
   - More iterations → better convergence → lower uncertainty?

### Visualizations

1. **Uncertainty heatmap**: N vs k, color = uncertainty
2. **Phase diagram**: ratio vs κ, error bars = uncertainty
3. **Calibration plot**: Sounio confidence vs bootstrap coverage
4. **Scaling plot**: log(N) vs log(uncertainty)

---

## Expected Results

### Quantitative Predictions

1. **Scaling**: uncertainty ∝ N^(-0.5 ± 0.1)
2. **Transition peak**: 2-3x higher uncertainty at ratio ≈ 2.5
3. **Calibration**: Sounio confidence within ±5% of bootstrap
4. **Convergence**: uncertainty ∝ 1/√iterations

### Qualitative Findings

- Small networks (N<100): Low confidence, high uncertainty
- Transition zone: Epistemic uncertainty captures ambiguity
- Large networks (N>500): High confidence, low uncertainty
- Sounio automatic tracking matches manual bootstrap

---

## Success Criteria

### Must Achieve

- [x] Implement epistemic curvature in Sounio
- [ ] Run 800 synthetic network trials
- [ ] Compare to Julia bootstrap (correlation > 0.8)
- [ ] Document uncertainty sources

### Should Achieve

- [ ] Validate 1/√N scaling
- [ ] Confirm transition zone peak
- [ ] Calibrate confidence levels
- [ ] Apply to real semantic networks

### Stretch Goals

- [ ] Real-time uncertainty visualization
- [ ] Adaptive Sinkhorn (stop when confident)
- [ ] Uncertainty-based active learning
- [ ] Publish epistemic network geometry paper

---

## Timeline

**Week 1**: Implementation
- Day 1-2: Implement epistemic tracking in Sounio
- Day 3-4: Implement Julia bootstrap comparison
- Day 5: Debug and validate

**Week 2**: Experiments
- Day 1-2: Run synthetic network sweep (800 trials)
- Day 3: Analyze results
- Day 4-5: Apply to real networks

**Week 3**: Analysis & Writing
- Day 1-2: Statistical tests and visualizations
- Day 3-4: Write results section
- Day 5: Integrate into paper

---

## Files

```
experiments/01_epistemic_uncertainty/
├── README.md                    (this file)
├── sounio/
│   ├── epistemic_trial.d       (single trial)
│   ├── epistemic_sweep.d       (full sweep)
│   └── run.sh                  (execution script)
├── julia/
│   ├── bootstrap_comparison.jl (bootstrap CI)
│   └── analysis.jl             (statistical tests)
├── results/
│   ├── synthetic_sweep.csv     (800 trials)
│   ├── real_networks.csv       (4 languages)
│   └── calibration.csv         (Sounio vs bootstrap)
├── figures/
│   ├── uncertainty_heatmap.png
│   ├── phase_diagram.png
│   ├── calibration_plot.png
│   └── scaling_plot.png
└── report.md                    (final writeup)
```

---

## Next Steps

1. ✅ Design complete
2. 🔨 Implement epistemic tracking in Sounio
3. 🔨 Implement Julia bootstrap baseline
4. 🧪 Run pilot experiment (N=100, k=10, 10 reps)
5. 📊 Validate measurements
6. 🚀 Run full experiment

---

**Status**: Ready to implement
**Owner**: Claude + Maria
**Estimated Duration**: 3 weeks
**Sounio Features Used**: Epistemic computing, effect system, confidence tracking
