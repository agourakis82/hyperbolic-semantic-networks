"""
CliffordORC.jl — Clifford Algebra Embedding ORC

Extends the hypercomplex ORC framework from Cayley-Dickson spheres (S^(d-1))
to Clifford algebras Cl(p,q) with potentially indefinite metric signature.

Architecture:
  1. Landmark embedding: N nodes → R^(p+q) via BFS distances (same as sphere case)
  2. Clifford distance: replace geodesic arc-length with Clifford pseudo-norm
       ‖x - y‖_{p,q} = √|Σᵢ sᵢ (xᵢ-yᵢ)²|   where sᵢ = +1 (i≤p) or -1 (i>p)
  3. For Cl(n,0): signature all-positive → reduces to Euclidean distance
     For Cl(n-1,1): Minkowski-like → some distances can be imaginary (take |⋅|)
  4. ORC: same LP machinery (JuMP+HiGHS) with Clifford distances as costs

Scientific question:
  Can a Minkowski-signature Cl(p,q) embedding restore κ < 0 for high-d
  embeddings where sphere (all positive) kills negative curvature?
"""

module CliffordORC

using Graphs
using LinearAlgebra
using JuMP
using HiGHS
using Statistics
using Random

export CliffordSignature, CliffordEmbedding
export clifford_embed, clifford_distance_matrix
export clifford_edge_curvature, clifford_all_curvatures

# ─────────────────────────────────────────────────────────────────
# Clifford signature
# ─────────────────────────────────────────────────────────────────

"""
    CliffordSignature(p, q)

Represents the metric signature (p, q):
  - p generators eᵢ with eᵢ² = +1 (spacelike)
  - q generators eⱼ with eⱼ² = -1 (timelike)
  - Total dimension: p + q

Notable cases:
  - Cl(n, 0): Euclidean → all distances positive (like sphere embedding)
  - Cl(1, 1): Split-complex plane → indefinite distances
  - Cl(3, 1): Spacetime (Minkowski-like) in 4D
  - Cl(1, 3): Dirac algebra signature
  - Cl(n-1, 1): "Almost Euclidean" with one timelike direction
"""
struct CliffordSignature
    p::Int  # positive generators
    q::Int  # negative generators
    function CliffordSignature(p::Int, q::Int)
        p >= 0 && q >= 0 || error("p,q must be non-negative")
        p + q >= 1 || error("total dimension must be ≥1")
        new(p, q)
    end
end

Base.show(io::IO, sig::CliffordSignature) = print(io, "Cl($(sig.p),$(sig.q))")
dim(sig::CliffordSignature) = sig.p + sig.q

# Standard signatures for sweep
const SIGNATURES = [
    CliffordSignature(4, 0),    # Euclidean 4D (= S³ comparison)
    CliffordSignature(8, 0),    # Euclidean 8D (= S⁷ comparison)
    CliffordSignature(16, 0),   # Euclidean 16D (= S¹⁵ comparison)
    CliffordSignature(3, 1),    # Cl(3,1): spacetime-like, 4D total
    CliffordSignature(7, 1),    # Cl(7,1): 8D total, 1 timelike
    CliffordSignature(15, 1),   # Cl(15,1): 16D total, 1 timelike
    CliffordSignature(2, 2),    # Cl(2,2): balanced split, 4D
    CliffordSignature(6, 2),    # Cl(6,2): mostly positive, 8D
    CliffordSignature(1, 3),    # Cl(1,3): mostly timelike, 4D
]

# ─────────────────────────────────────────────────────────────────
# Landmark embedding (same as hypercomplex_lp.jl)
# ─────────────────────────────────────────────────────────────────

"""
    select_landmarks(D_hop, n_lm; rng) -> Vector{Int}

Greedy farthest-first landmark selection from BFS distance matrix.
"""
function select_landmarks(D_hop::Matrix{Int}, n_lm::Int;
                           rng::AbstractRNG=MersenneTwister(42))::Vector{Int}
    N = size(D_hop, 1)
    n_lm = min(n_lm, N)
    landmarks = [rand(rng, 1:N)]
    min_dists = D_hop[landmarks[1], :]
    for _ in 2:n_lm
        push!(landmarks, argmax(min_dists))
        min_dists = min.(min_dists, D_hop[landmarks[end], :])
    end
    return landmarks
end

"""
    landmark_raw_embed(D_hop, landmarks) -> Matrix{Float64}

Embed N nodes into R^d using distances to d landmarks.
Returns raw (unnormalized) embedding X ∈ R^(N×d).
"""
function landmark_raw_embed(D_hop::Matrix{Int}, landmarks::Vector{Int})::Matrix{Float64}
    N = size(D_hop, 1)
    d = length(landmarks)
    X = zeros(Float64, N, d)
    for (j, lm) in enumerate(landmarks)
        for i in 1:N
            dist = D_hop[i, lm]
            X[i, j] = dist == typemax(Int) ? Float64(N) : Float64(dist)
        end
    end
    return X
end

# ─────────────────────────────────────────────────────────────────
# Clifford pseudo-distance
# ─────────────────────────────────────────────────────────────────

"""
    clifford_pseudo_norm_sq(x, sig) -> Float64

Compute the Clifford pseudo-norm squared:
    ‖x‖²_{p,q} = Σᵢ₌₁ᵖ xᵢ² - Σⱼ₌₁ᵍ x_{p+j}²

This can be negative for timelike vectors in split signatures.
"""
function clifford_pseudo_norm_sq(x::AbstractVector{Float64}, sig::CliffordSignature)::Float64
    s = 0.0
    for i in 1:sig.p
        s += x[i]^2
    end
    for j in 1:sig.q
        s -= x[sig.p + j]^2
    end
    return s
end

"""
    clifford_distance(x, y, sig) -> Float64

Clifford distance between two embedded points:
    d_{p,q}(x, y) = √|‖x - y‖²_{p,q}|

For Cl(n,0): this is Euclidean distance (always ≥ 0).
For split signatures: the pseudo-norm of (x-y) can be negative
  (timelike separation), giving an imaginary "distance".
  We take the absolute value to get a real non-negative cost.
"""
function clifford_distance(x::AbstractVector{Float64}, y::AbstractVector{Float64},
                            sig::CliffordSignature)::Float64
    diff = x - y
    nsq = clifford_pseudo_norm_sq(diff, sig)
    return sqrt(abs(nsq))
end

"""
    clifford_distance_matrix(X, sig) -> Matrix{Float64}

Pairwise Clifford distances for N×d embedding matrix X.
"""
function clifford_distance_matrix(X::Matrix{Float64}, sig::CliffordSignature)::Matrix{Float64}
    N = size(X, 1)
    d = size(X, 2)
    d == dim(sig) || error("Embedding dim $d ≠ signature dim $(dim(sig))")
    C = zeros(Float64, N, N)
    for i in 1:N
        for j in (i+1):N
            c = clifford_distance(X[i,:], X[j,:], sig)
            C[i,j] = c
            C[j,i] = c
        end
    end
    return C
end

# ─────────────────────────────────────────────────────────────────
# LP Wasserstein (same as unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                             C::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    @variable(model, gamma[1:n, 1:n] >= 0)
    @constraint(model, [i=1:n], sum(gamma[i,j] for j in 1:n) == mu[i])
    @constraint(model, [j=1:n], sum(gamma[i,j] for i in 1:n) == nu[j])
    @objective(model, Min, sum(C[i,j]*gamma[i,j] for i in 1:n, j in 1:n))
    optimize!(model)
    termination_status(model) == OPTIMAL || return NaN
    return objective_value(model)
end

# ─────────────────────────────────────────────────────────────────
# Core Clifford ORC for a single edge
# ─────────────────────────────────────────────────────────────────

"""
    clifford_edge_curvature(g, u, v, X, C_clifford; alpha=0.5) -> Float64

ORC for edge (u,v) using Clifford embedding X and Clifford cost matrix C_clifford.
Standard idleness-α probability measures; graph structure (neighbors) from g.
"""
function clifford_edge_curvature(g::SimpleGraph, u::Int, v::Int,
                                  X::Matrix{Float64}, C_clifford::Matrix{Float64};
                                  alpha::Float64=0.5)::Float64
    nbrs_u = neighbors(g, u)
    nbrs_v = neighbors(g, v)

    mu_dict = Dict{Int,Float64}(u => alpha)
    nu_dict = Dict{Int,Float64}(v => alpha)

    if !isempty(nbrs_u)
        w = (1.0 - alpha) / length(nbrs_u)
        for z in nbrs_u; mu_dict[z] = get(mu_dict, z, 0.0) + w; end
    end
    if !isempty(nbrs_v)
        w = (1.0 - alpha) / length(nbrs_v)
        for z in nbrs_v; nu_dict[z] = get(nu_dict, z, 0.0) + w; end
    end

    all_nodes = sort(unique(vcat(collect(keys(mu_dict)), collect(keys(nu_dict)))))
    n = length(all_nodes)
    idx = Dict(node => i for (i,node) in enumerate(all_nodes))

    mu_vec = zeros(n); nu_vec = zeros(n)
    for (node,p) in mu_dict; mu_vec[idx[node]] = p; end
    for (node,p) in nu_dict; nu_vec[idx[node]] = p; end

    # Cost from Clifford distance matrix
    C = C_clifford[all_nodes, all_nodes]

    d_uv = C_clifford[u, v]
    # For indefinite signatures, null vectors give d≈0 — skip such edges
    d_uv < 1e-4 && return NaN

    W1 = exact_wasserstein1(mu_vec, nu_vec, C)
    isnan(W1) && return NaN
    kappa = 1.0 - W1 / d_uv
    # Guard against numerical blow-up in indefinite signatures
    (isnan(kappa) || abs(kappa) > 100.0) && return NaN
    return kappa
end

# ─────────────────────────────────────────────────────────────────
# Batch computation
# ─────────────────────────────────────────────────────────────────

"""
    clifford_all_curvatures(g, sig; n_lm=nothing, alpha=0.5, rng) -> Vector{Float64}

Compute ORC for all edges of graph g using Clifford(p,q) embedding.
n_lm: number of landmarks (defaults to dim(sig)).
"""
function clifford_all_curvatures(g::SimpleGraph, sig::CliffordSignature;
                                   n_lm::Union{Int,Nothing}=nothing,
                                   alpha::Float64=0.5,
                                   rng::AbstractRNG=MersenneTwister(42))::Vector{Float64}
    N = nv(g)
    d = dim(sig)
    n_lm_use = isnothing(n_lm) ? d : n_lm

    # APSP
    D_hop = Matrix{Int}(undef, N, N)
    Threads.@threads for v in 1:N
        D_hop[v,:] = gdistances(g, v)
    end

    # Landmark embedding
    landmarks = select_landmarks(D_hop, n_lm_use; rng=rng)
    X_raw = landmark_raw_embed(D_hop, landmarks)  # N × n_lm_use

    # Pad/truncate to exactly d dimensions (p+q)
    if n_lm_use < d
        # Pad with zeros
        X = hcat(X_raw, zeros(Float64, N, d - n_lm_use))
    elseif n_lm_use > d
        X = X_raw[:, 1:d]
    else
        X = X_raw
    end

    # Normalize each row to unit length (consistent with sphere embedding)
    for i in 1:N
        nrm = norm(X[i,:])
        if nrm > 1e-10
            X[i,:] ./= nrm
        end
    end

    # Clifford distance matrix
    C_clifford = clifford_distance_matrix(X, sig)

    # Edge curvatures
    edge_list = collect(edges(g))
    kappas = Vector{Float64}(undef, length(edge_list))
    Threads.@threads for i in 1:length(edge_list)
        e = edge_list[i]
        kappas[i] = clifford_edge_curvature(g, src(e), dst(e), X, C_clifford; alpha=alpha)
    end

    return kappas
end

end  # module CliffordORC
