// Types.fs — Core domain types for Quaternionic Brain ORC
//
// Implements the type-safe domain model for multi-modal brain network
// analysis using quaternionic Ollivier-Ricci curvature.
//
// Modality mapping (mirrors quaternion_sinkhorn.sio):
//   R-component → fMRI BOLD functional connectivity
//   I-component → DTI structural tractography strength
//   J-component → EEG/MEG spectral power
//   K-component → clinical phenotype score (ASD/ADHD-RS)

module BrainORC.Types

// ============================================================================
// Quaternion arithmetic
// ============================================================================

/// A quaternion q = r + i·î + j·ĵ + k·k̂ over ℝ⁴.
/// Used to represent multi-modal curvature κ_ℍ ∈ ℍ per edge.
[<Struct>]
type Quaternion = {
    R: float   // fMRI BOLD component
    I: float   // DTI tractography component
    J: float   // EEG/MEG spectral component
    K: float   // clinical phenotype component
}

module Quaternion =
    let zero  = { R = 0.0; I = 0.0; J = 0.0; K = 0.0 }
    let norm2 q = q.R*q.R + q.I*q.I + q.J*q.J + q.K*q.K
    let norm  q = sqrt (norm2 q)
    let scale s q = { R = s*q.R; I = s*q.I; J = s*q.J; K = s*q.K }
    let add   a b = { R = a.R+b.R; I = a.I+b.I; J = a.J+b.J; K = a.K+b.K }
    let sub   a b = { R = a.R-b.R; I = a.I-b.I; J = a.J-b.J; K = a.K-b.K }

    /// Returns index of the component with largest absolute value.
    /// 0=fMRI(R), 1=DTI(I), 2=EEG(J), 3=clinical(K)
    let dominantComponent q =
        let abs x = if x >= 0.0 then x else -x
        let comps = [| abs q.R; abs q.I; abs q.J; abs q.K |]
        comps |> Array.indexed |> Array.maxBy snd |> fst

// ============================================================================
// Brain modalities
// ============================================================================

/// The 4 brain imaging/clinical modalities fused into quaternionic ORC.
type BrainModality = FMRI | DTI | EEG | Clinical

module BrainModality =
    let label = function
        | FMRI     -> "fMRI BOLD"
        | DTI      -> "DTI tractography"
        | EEG      -> "EEG/MEG spectral"
        | Clinical -> "Clinical phenotype"

    let ofIndex = function
        | 0 -> FMRI | 1 -> DTI | 2 -> EEG | _ -> Clinical

// ============================================================================
// Network geometry classification
// ============================================================================

/// Geometric regime of a brain network, determined by η vs η_c(N).
/// Mirrors the phase transition theory from the monograph.
type NetworkGeometry =
    | Hyperbolic   // η < η_c(N): tree-like, sparse, fragile — κ̄ < 0
    | Critical     // η ≈ η_c(N): sign-change boundary             — κ̄ ≈ 0
    | Spherical    // η > η_c(N): clique-like, redundant, robust   — κ̄ > 0

module NetworkGeometry =
    /// Finite-size scaling: η_c(N) = 3.75 - 14.62/√N  [EMPIRICAL, R²=0.995]
    let etaCritical (n: int) =
        3.75 - 14.62 / sqrt (float n)

    /// Classify network by density parameter η = ⟨k⟩²/N.
    let classify (n: int) (meanDegree: float) =
        let eta   = meanDegree * meanDegree / float n
        let eta_c = etaCritical n
        if   eta < eta_c * 0.95 then Hyperbolic
        elif eta > eta_c * 1.05 then Spherical
        else Critical

    let label = function
        | Hyperbolic -> "HYPERBOLIC"
        | Critical   -> "CRITICAL"
        | Spherical  -> "SPHERICAL"

// ============================================================================
// Edge-level curvature with epistemic uncertainty
// ============================================================================

/// Quaternionic ORC with bootstrap confidence intervals for a single edge.
/// An edge is "strongly robust"   if CI_lo.R > 0
/// An edge is "strongly fragile"  if CI_hi.R < 0
/// An edge is "uncertain"         otherwise
type EpistemicEdge = {
    U:        int           // source node
    V:        int           // target node
    Kappa:    Quaternion    // point estimate κ_ℍ
    CI_lo:    Quaternion    // lower bootstrap CI (5th percentile)
    CI_hi:    Quaternion    // upper bootstrap CI (95th percentile)
    NSeeds:   int           // number of bootstrap seeds used
    Norm:     float         // |κ_ℍ| = overall edge robustness magnitude
    DomComp:  BrainModality // modality that drives edge fragility
}

module EpistemicEdge =
    type Verdict = StronglyRobust | StronglyFragile | Uncertain

    let verdict (e: EpistemicEdge) =
        if   e.CI_lo.R > 0.0 then StronglyRobust
        elif e.CI_hi.R < 0.0 then StronglyFragile
        else Uncertain

    let verdictLabel = function
        | StronglyRobust  -> "STRONGLY ROBUST  (CI_lo.R > 0)"
        | StronglyFragile -> "STRONGLY FRAGILE (CI_hi.R < 0)"
        | Uncertain       -> "UNCERTAIN"

// ============================================================================
// Brain network (typed graph)
// ============================================================================

/// A brain network with typed geometric classification and epistemic edges.
type BrainNetwork = {
    N:          int                      // number of nodes
    Edges:      EpistemicEdge list       // curvature-annotated edges
    MeanDegree: float                    // ⟨k⟩
    Eta:        float                    // η = ⟨k⟩²/N
    EtaCrit:    float                    // η_c(N) from finite-size scaling
    Geometry:   NetworkGeometry          // phase classification
    MeanKappa:  Quaternion               // mean κ_ℍ across edges
    Cohort:     string                   // e.g. "ASD", "ADHD", "Control"
}

module BrainNetwork =
    let meanKappa (edges: EpistemicEdge list) =
        match edges with
        | [] -> Quaternion.zero
        | _  ->
            let n = float (List.length edges)
            edges
            |> List.map (fun e -> e.Kappa)
            |> List.fold Quaternion.add Quaternion.zero
            |> Quaternion.scale (1.0 / n)

    let summary (net: BrainNetwork) =
        let k = net.MeanKappa
        sprintf "%s | N=%d η=%.3f η_c=%.3f → %s | κ̄_R=%.4f |κ̄_ℍ|=%.4f"
            net.Cohort net.N net.Eta net.EtaCrit
            (NetworkGeometry.label net.Geometry)
            k.R (Quaternion.norm k)
