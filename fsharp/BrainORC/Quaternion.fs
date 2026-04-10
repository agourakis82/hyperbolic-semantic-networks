// Quaternion.fs — Pure F# quaternionic Sinkhorn-Wasserstein solver
//
// Implements W₁_ℍ(μ, ν) by running 4 independent scalar Sinkhorn solves
// (one per quaternion component). This mirrors quaternion_sinkhorn.sio
// exactly, enabling cross-validation.
//
// Used when Sounio shared library is not available (pure-F# fallback).

module BrainORC.QuaternionSinkhorn

open BrainORC.Types

// ============================================================================
// Probability measure over node neighborhood
// ============================================================================

/// Node probability measure: support nodes + per-component weights.
type NodeMeasure = {
    Nodes:  int array    // support node indices
    Wr:     float array  // fMRI weights   (sum to 1)
    Wi:     float array  // DTI weights    (sum to 1)
    Wj:     float array  // EEG weights    (sum to 1)
    Wk:     float array  // clinical weights (sum to 1)
}

module NodeMeasure =
    /// Build lazy random walk measure (α=0.5) using a single modality weight vector.
    /// For multi-modal use, call once per component or use buildMultiModal.
    let buildUniform (nodeIdx: int) (neighbors: int array) (alpha: float) : float array =
        let n = neighbors.Length
        if n = 0 then [| 1.0 |]
        else
            let w = (1.0 - alpha) / float n
            [| yield alpha; for _ in neighbors -> w |]

    /// Build a NodeMeasure by specifying per-component weight arrays explicitly.
    let create (nodes: int array) wr wi wj wk : NodeMeasure =
        { Nodes = nodes; Wr = wr; Wi = wi; Wj = wj; Wk = wk }

// ============================================================================
// Sinkhorn-Knopp W1 (single component)
// ============================================================================

[<Literal>]
let private Floor = 1e-300

/// Compute W₁(μ, ν) for a single weight component using Sinkhorn-Knopp.
/// dist: flat N×N distance matrix, stride = graphN
let private sinkhornW1Component
    (nodesA: int array) (weightsA: float array)
    (nodesB: int array) (weightsB: float array)
    (dist: int[,]) (epsilon: float) (maxIter: int) : float =

    let na = nodesA.Length
    let nb = nodesB.Length
    if na = 0 || nb = 0 then 0.0
    else

    // Build cost matrix C[i,j] = d(nodesA[i], nodesB[j])
    let cost = Array2D.init na nb (fun i j ->
        let d = dist[nodesA[i], nodesB[j]]
        if d >= 0 then float d else 100.0)

    // Kernel K[i,j] = exp(-C[i,j] / ε)
    let kmat = Array2D.init na nb (fun i j ->
        exp (- cost[i,j] / epsilon))

    let u = Array.create na 1.0
    let v = Array.create nb 1.0

    for _ = 1 to maxIter do
        // u update: u_i = a_i / (K v)_i
        for i = 0 to na - 1 do
            let s = Array.sumBy (fun j -> kmat[i,j] * v[j]) [| 0 .. nb-1 |]
            if s > Floor then u[i] <- weightsA[i] / s
        // v update: v_j = b_j / (Kᵀ u)_j
        for j = 0 to nb - 1 do
            let s = Array.sumBy (fun i -> kmat[i,j] * u[i]) [| 0 .. na-1 |]
            if s > Floor then v[j] <- weightsB[j] / s

    // Primal objective: ⟨C, u ⊗ K ⊗ v⟩
    let mutable w1 = 0.0
    for i = 0 to na - 1 do
        for j = 0 to nb - 1 do
            w1 <- w1 + u[i] * kmat[i,j] * v[j] * cost[i,j]
    w1

// ============================================================================
// Quaternionic W1 and κ_ℍ
// ============================================================================

/// Compute W₁_ℍ(μ, ν) ∈ ℍ: 4 independent Sinkhorn solves.
let quatW1
    (mu: NodeMeasure) (nu: NodeMeasure)
    (dist: int[,]) (epsilon: float) (maxIter: int) : Quaternion =
    {
        R = sinkhornW1Component mu.Nodes mu.Wr nu.Nodes nu.Wr dist epsilon maxIter
        I = sinkhornW1Component mu.Nodes mu.Wi nu.Nodes nu.Wi dist epsilon maxIter
        J = sinkhornW1Component mu.Nodes mu.Wj nu.Nodes nu.Wj dist epsilon maxIter
        K = sinkhornW1Component mu.Nodes mu.Wk nu.Nodes nu.Wk dist epsilon maxIter
    }

/// Compute κ_ℍ(u, v) = 1 - W₁_ℍ(μ_u, μ_v) / d(u,v), component-wise.
let quatKappa
    (u: int) (v: int)
    (mu: NodeMeasure) (nu: NodeMeasure)
    (dist: int[,]) (epsilon: float) (maxIter: int) : EpistemicEdge =

    let d = max 1.0 (float dist[u, v])
    let w1q = quatW1 mu nu dist epsilon maxIter
    let kappa = {
        R = 1.0 - w1q.R / d
        I = 1.0 - w1q.I / d
        J = 1.0 - w1q.J / d
        K = 1.0 - w1q.K / d
    }
    let norm    = Quaternion.norm kappa
    let domIdx  = Quaternion.dominantComponent kappa
    {
        U = u; V = v
        Kappa   = kappa
        CI_lo   = kappa   // point estimate (no bootstrap here; see Pipeline.fs)
        CI_hi   = kappa
        NSeeds  = 1
        Norm    = norm
        DomComp = BrainModality.ofIndex domIdx
    }
