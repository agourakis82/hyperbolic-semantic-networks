// BrainGraph.fs — Brain graph construction and BFS distances
//
// Builds typed brain graphs from multi-modal data matrices.
// Computes all-pairs shortest path distances via BFS (unweighted adjacency).

module BrainORC.BrainGraph

open BrainORC.Types
open BrainORC.QuaternionSinkhorn

// ============================================================================
// Multi-modal brain data input
// ============================================================================

/// Raw multi-modal brain data: one N×N matrix per modality.
/// Values should be non-negative; adjacency derived by thresholding.
type MultiModalData = {
    N:          int
    FMRI:       float[,]   // functional connectivity (partial corr or z-score)
    DTI:        float[,]   // structural tractography (streamline count, normalized)
    EEG:        float[,]   // spectral coherence or power coupling
    Clinical:   float[]    // per-node clinical score (ADOS, ADHD-RS, etc.)
    Cohort:     string
}

// ============================================================================
// Graph construction
// ============================================================================

/// Adjacency list: neighbors[u] = list of neighbor node indices
type AdjList = int array array

/// Build adjacency list from fMRI connectivity matrix by thresholding.
/// threshold: minimum absolute correlation to keep an edge
let buildAdjacency (fmri: float[,]) (threshold: float) : AdjList =
    let n = Array2D.length1 fmri
    Array.init n (fun u ->
        [| for v = 0 to n-1 do
               if u <> v && abs fmri[u,v] >= threshold then yield v |])

/// BFS from source node; returns distance array (int, -1 = unreachable).
let bfsDistances (adj: AdjList) (source: int) : int array =
    let n = adj.Length
    let dist = Array.create n -1
    dist[source] <- 0
    let queue = System.Collections.Generic.Queue<int>()
    queue.Enqueue source
    while queue.Count > 0 do
        let u = queue.Dequeue()
        for v in adj[u] do
            if dist[v] = -1 then
                dist[v] <- dist[u] + 1
                queue.Enqueue v
    dist

/// Compute all-pairs BFS distance matrix (N×N).
let allPairsDistances (adj: AdjList) : int[,] =
    let n = adj.Length
    let dist = Array2D.create n n -1
    for u = 0 to n-1 do
        let d = bfsDistances adj u
        for v = 0 to n-1 do
            dist[u,v] <- d[v]
    dist

// ============================================================================
// Node measures from multi-modal data
// ============================================================================

/// Build lazy random walk measure at node u, weighted by modality values.
/// Returns (support nodes array, weight array normalized to sum=1).
let private buildWeightedMeasure
    (adj: AdjList) (u: int) (alpha: float) (nodeWeights: float[]) : int array * float array =

    let neighbors = adj[u]
    let deg = neighbors.Length
    if deg = 0 then
        [| u |], [| 1.0 |]
    else
        // Compute denominator: sum of neighbor weights (mass action principle)
        let totalWeight =
            neighbors |> Array.sumBy (fun v -> max 0.0 nodeWeights[v])
        let safeTotal = if totalWeight < 1e-12 then 1.0 else totalWeight

        let nodes = [| yield u; yield! neighbors |]
        let probs = [|
            yield alpha                          // idle mass at u
            for v in neighbors ->
                (1.0 - alpha) * (max 0.0 nodeWeights[v]) / safeTotal
        |]
        nodes, probs

/// Build NodeMeasure at node u fusing all 4 modalities.
/// fmriRow: row u of fMRI connectivity (edge-level signal)
/// dtiRow:  row u of DTI tractography
/// eegRow:  row u of EEG coherence
/// clinical: per-node clinical score vector
let buildNodeMeasure
    (adj: AdjList) (u: int) (alpha: float)
    (fmriRow: float[]) (dtiRow: float[]) (eegRow: float[]) (clinical: float[])
    : NodeMeasure =

    let _, wr = buildWeightedMeasure adj u alpha fmriRow
    let _, wi = buildWeightedMeasure adj u alpha dtiRow
    let _, wj = buildWeightedMeasure adj u alpha eegRow
    let nodes, wk = buildWeightedMeasure adj u alpha clinical

    NodeMeasure.create nodes wr wi wj wk
