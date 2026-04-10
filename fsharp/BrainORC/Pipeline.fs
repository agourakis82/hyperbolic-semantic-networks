// Pipeline.fs — Full quaternionic brain ORC pipeline
//
// classifyBrainNetwork: MultiModalData → BrainNetwork
//
// Stages:
//   1. Build adjacency from fMRI threshold
//   2. Compute all-pairs BFS distances
//   3. Build NodeMeasures (4 modalities per node)
//   4. Compute κ_ℍ per edge (pure F# Sinkhorn)
//   5. Bootstrap CI over random graph seeds
//   6. Classify geometry by η vs η_c(N)
//   7. Return typed BrainNetwork

module BrainORC.Pipeline

open BrainORC.Types
open BrainORC.QuaternionSinkhorn
open BrainORC.BrainGraph

// ============================================================================
// Configuration
// ============================================================================

type OrcConfig = {
    Alpha:       float    // lazy random walk idleness (default 0.5)
    Epsilon:     float    // Sinkhorn regularisation (default 0.1)
    MaxIter:     int      // Sinkhorn iterations (default 300)
    FmriThresh:  float    // fMRI correlation threshold for adjacency (default 0.1)
    NSeeds:      int      // bootstrap seeds for epistemic CI (default 10)
    Percentile:  float    // CI percentile (default 0.05 for 90% CI)
}

module OrcConfig =
    let defaults = {
        Alpha      = 0.5
        Epsilon    = 0.1
        MaxIter    = 300
        FmriThresh = 0.1
        NSeeds     = 10
        Percentile = 0.05
    }

// ============================================================================
// Edge enumeration
// ============================================================================

let private enumerateEdges (adj: AdjList) : (int * int) list =
    [| for u = 0 to adj.Length - 1 do
           for v in adj[u] do
               if v > u then yield (u, v) |]
    |> Array.toList

// ============================================================================
// Bootstrap CI computation
// ============================================================================

/// Compute CI for a single edge by perturbing modality weights with Gaussian noise.
/// In practice this simulates subject-to-subject variability in the weights.
let private bootstrapEdge
    (u: int) (v: int)
    (adj: AdjList)
    (dist: int[,])
    (data: MultiModalData)
    (cfg: OrcConfig)
    (nSeeds: int) : EpistemicEdge =

    let rng = System.Random 42

    let kappas =
        [| for seed = 0 to nSeeds - 1 do
               // Perturb each modality row with small Gaussian noise (σ=0.05)
               let noiseScale = 0.05
               let perturb (arr: float[]) =
                   arr |> Array.map (fun x ->
                       let noise = rng.NextDouble() * 2.0 - 1.0  // U(-1,1)
                       max 0.0 (x + noiseScale * noise))

               let fmriRow = [| for j in 0 .. data.N-1 do data.FMRI[u,j] |] |> perturb
               let dtiRow  = [| for j in 0 .. data.N-1 do data.DTI[u,j]  |] |> perturb
               let eegRow  = [| for j in 0 .. data.N-1 do data.EEG[u,j]  |] |> perturb

               let fmriRowV = [| for j in 0 .. data.N-1 do data.FMRI[v,j] |] |> perturb
               let dtiRowV  = [| for j in 0 .. data.N-1 do data.DTI[v,j]  |] |> perturb
               let eegRowV  = [| for j in 0 .. data.N-1 do data.EEG[v,j]  |] |> perturb

               let muU = buildNodeMeasure adj u cfg.Alpha fmriRow dtiRow eegRow data.Clinical
               let muV = buildNodeMeasure adj v cfg.Alpha fmriRowV dtiRowV eegRowV data.Clinical

               let edge = quatKappa u v muU muV dist cfg.Epsilon cfg.MaxIter
               yield edge.Kappa
        |]

    let n = float kappas.Length
    let mean = kappas |> Array.fold Quaternion.add Quaternion.zero |> Quaternion.scale (1.0 / n)

    // Simple percentile CI: sort R-components and take 5th/95th percentile
    let sortedR = kappas |> Array.map (fun q -> q.R) |> Array.sort
    let sortedI = kappas |> Array.map (fun q -> q.I) |> Array.sort
    let sortedJ = kappas |> Array.map (fun q -> q.J) |> Array.sort
    let sortedK = kappas |> Array.map (fun q -> q.K) |> Array.sort

    let loIdx = max 0 (int (cfg.Percentile * float nSeeds))
    let hiIdx = min (nSeeds - 1) (int ((1.0 - cfg.Percentile) * float nSeeds))

    let ci_lo = { R = sortedR[loIdx]; I = sortedI[loIdx]; J = sortedJ[loIdx]; K = sortedK[loIdx] }
    let ci_hi = { R = sortedR[hiIdx]; I = sortedI[hiIdx]; J = sortedJ[hiIdx]; K = sortedK[hiIdx] }

    {
        U = u; V = v
        Kappa   = mean
        CI_lo   = ci_lo
        CI_hi   = ci_hi
        NSeeds  = nSeeds
        Norm    = Quaternion.norm mean
        DomComp = BrainModality.ofIndex (Quaternion.dominantComponent mean)
    }

// ============================================================================
// Main pipeline
// ============================================================================

/// Full pipeline: MultiModalData → BrainNetwork with epistemic edges.
let classifyBrainNetwork (data: MultiModalData) (cfg: OrcConfig) : BrainNetwork =
    let adj  = buildAdjacency data.FMRI cfg.FmriThresh
    let dist = allPairsDistances adj

    let edges = enumerateEdges adj
    let totalEdges = List.length edges
    eprintfn "BrainORC: N=%d, |E|=%d, computing quaternionic κ_ℍ..." data.N totalEdges

    let epistemicEdges =
        edges
        |> List.mapi (fun idx (u, v) ->
            if idx % 50 = 0 then eprintfn "  edge %d/%d..." idx totalEdges
            let fmriRow  = [| for j in 0 .. data.N-1 do data.FMRI[u,j] |]
            let dtiRow   = [| for j in 0 .. data.N-1 do data.DTI[u,j]  |]
            let eegRow   = [| for j in 0 .. data.N-1 do data.EEG[u,j]  |]
            let fmriRowV = [| for j in 0 .. data.N-1 do data.FMRI[v,j] |]
            let dtiRowV  = [| for j in 0 .. data.N-1 do data.DTI[v,j]  |]
            let eegRowV  = [| for j in 0 .. data.N-1 do data.EEG[v,j]  |]

            let muU = buildNodeMeasure adj u cfg.Alpha fmriRow dtiRow eegRow data.Clinical
            let muV = buildNodeMeasure adj v cfg.Alpha fmriRowV dtiRowV eegRowV data.Clinical

            if cfg.NSeeds <= 1 then
                quatKappa u v muU muV dist cfg.Epsilon cfg.MaxIter
            else
                bootstrapEdge u v adj dist data cfg cfg.NSeeds)

    let meanDeg =
        adj |> Array.map (fun nb -> float nb.Length) |> Array.average
    let eta   = meanDeg * meanDeg / float data.N
    let etaC  = NetworkGeometry.etaCritical data.N
    let geom  = NetworkGeometry.classify data.N meanDeg
    let meanK = BrainNetwork.meanKappa epistemicEdges

    {
        N          = data.N
        Edges      = epistemicEdges
        MeanDegree = meanDeg
        Eta        = eta
        EtaCrit    = etaC
        Geometry   = geom
        MeanKappa  = meanK
        Cohort     = data.Cohort
    }
