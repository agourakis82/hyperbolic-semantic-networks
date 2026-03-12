"""
Discovery J — HPO ORC Analysis
===============================
Builds two networks from Human Phenotype Ontology data and computes
exact LP Ollivier-Ricci curvature on both:

  1. HPO IS-A graph   — ontology hierarchy (tree-like, expected HYPERBOLIC)
  2. Disease co-occurrence — diseases sharing ≥K phenotypes (expected SPHERICAL)

Data:
  data/processed/hp.obo        — HPO OBO v2026-02-16
  data/processed/phenotype.hpoa — HPO disease-phenotype annotations

Usage:
  julia --project=julia julia/scripts/hpo_orc.jl
"""

import Pkg
let deps = Pkg.project().dependencies
    for pkg in ["JuMP", "HiGHS", "Graphs", "JSON", "Statistics", "Printf"]
        haskey(deps, pkg) || Pkg.add(pkg)
    end
end

using JuMP, HiGHS, Graphs, Statistics, JSON, Printf

const DATA_DIR    = joinpath(@__DIR__, "..", "..", "data", "processed")
const RESULTS_DIR = joinpath(@__DIR__, "..", "..", "results", "experiments")

# ─────────────────────────────────────────────────────────────────
# 1. OBO parser — extract HP term ids and is_a edges
# ─────────────────────────────────────────────────────────────────

function parse_obo(path::String)
    @printf("Parsing %s …\n", basename(path))
    terms = Dict{String, Vector{String}}()   # id => [parent_ids…]
    current_id = ""
    in_term = false

    for line in eachline(path)
        line = strip(line)
        if line == "[Term]"
            in_term = true
            current_id = ""
        elseif startswith(line, "[")
            in_term = false
            current_id = ""
        elseif in_term
            if startswith(line, "id: ")
                current_id = split(line, ' ')[2]
                terms[current_id] = String[]
            elseif startswith(line, "is_a: ") && !isempty(current_id)
                parent = split(split(line, ' ')[2], '!')[1] |> strip
                push!(terms[current_id], parent)
            elseif startswith(line, "is_obsolete: true")
                # drop this term
                delete!(terms, current_id)
                current_id = ""
            end
        end
    end
    @printf("  Parsed %d non-obsolete HP terms\n", length(terms))
    return terms
end

"""Build undirected SimpleGraph from is_a edges (child -- parent)."""
function build_hpo_graph(terms::Dict{String, Vector{String}})
    all_ids = sort(collect(keys(terms)))
    id2idx  = Dict(id => i for (i, id) in enumerate(all_ids))
    N = length(all_ids)
    g = SimpleGraph(N)
    edges_added = 0
    for (child, parents) in terms
        !haskey(id2idx, child) && continue
        for parent in parents
            !haskey(id2idx, parent) && continue
            add_edge!(g, id2idx[child], id2idx[parent])
            edges_added += 1
        end
    end
    @printf("  HPO graph: N=%d nodes, E=%d edges (is_a links)\n", N, edges_added)
    return g, id2idx, all_ids
end

# ─────────────────────────────────────────────────────────────────
# 2. HPOA parser — build disease–phenotype bipartite → co-occurrence
# ─────────────────────────────────────────────────────────────────

"""
Parse phenotype.hpoa → Dict disease_id => Set{hp_id}
Filters to P (phenotype) aspect only, excludes NOT qualifiers.
"""
function parse_hpoa(path::String)
    @printf("Parsing %s …\n", basename(path))
    disease_phenos = Dict{String, Set{String}}()
    n_rows = 0
    for line in eachline(path)
        startswith(line, '#') && continue
        startswith(line, "database_id") && continue
        cols = split(line, '\t')
        length(cols) < 12 && continue
        disease_id  = cols[1]
        qualifier   = cols[3]
        hp_id       = cols[4]
        aspect      = cols[11]
        # keep only phenotype aspect, no NOT qualifiers
        aspect != "P" && continue
        qualifier == "NOT" && continue
        startswith(hp_id, "HP:") || continue
        if !haskey(disease_phenos, disease_id)
            disease_phenos[disease_id] = Set{String}()
        end
        push!(disease_phenos[disease_id], hp_id)
        n_rows += 1
    end
    @printf("  Parsed %d disease-phenotype pairs across %d diseases\n",
            n_rows, length(disease_phenos))
    return disease_phenos
end

"""
Build disease co-occurrence graph: edge between two diseases if they share ≥ K phenotypes.
Subsamples to at most MAX_NODES diseases (most phenotype-rich, for tractability).
"""
function build_cooccurrence_graph(disease_phenos::Dict{String, Set{String}};
                                   min_shared::Int=3, max_nodes::Int=600)
    diseases = collect(keys(disease_phenos))

    # Keep diseases with ≥ min_shared phenotypes (so edges are possible)
    diseases = filter(d -> length(disease_phenos[d]) >= min_shared, diseases)

    # Sort by phenotype count descending, take top max_nodes
    sort!(diseases, by=d -> -length(disease_phenos[d]))
    if length(diseases) > max_nodes
        diseases = diseases[1:max_nodes]
    end

    @printf("  Co-occurrence graph: %d diseases (≥%d phenotypes each)\n",
            length(diseases), min_shared)

    N = length(diseases)
    dis2idx = Dict(d => i for (i, d) in enumerate(diseases))
    g = SimpleGraph(N)

    for i in 1:N
        Si = disease_phenos[diseases[i]]
        for j in (i+1):N
            Sj = disease_phenos[diseases[j]]
            shared = length(intersect(Si, Sj))
            if shared >= min_shared
                add_edge!(g, i, j)
            end
        end
    end

    E = ne(g)
    @printf("  Co-occurrence graph: N=%d, E=%d (shared ≥ %d phenotypes)\n",
            N, E, min_shared)
    return g, diseases
end

# ─────────────────────────────────────────────────────────────────
# 3. Graph utilities
# ─────────────────────────────────────────────────────────────────

function lcc(g::SimpleGraph)
    ccs = connected_components(g)
    length(ccs) == 1 && return g
    lcc_verts = ccs[argmax(length.(ccs))]
    g_lcc, _ = induced_subgraph(g, sort(lcc_verts))
    return g_lcc
end

function graph_metrics(g::SimpleGraph)
    N = nv(g); E = ne(g)
    degs = degree(g)
    mean_k = 2.0 * E / N
    eta    = mean_k^2 / N
    # clustering
    tri = 0; trip = 0
    for v in vertices(g)
        nb = neighbors(g, v); d = length(nb)
        d < 2 && continue
        trip += d*(d-1)÷2
        for i in 1:length(nb), j in (i+1):length(nb)
            has_edge(g, nb[i], nb[j]) && (tri += 1)
        end
    end
    C = trip > 0 ? tri/trip : 0.0
    return (N=N, E=E, mean_k=mean_k, eta=eta, clustering=C,
            min_deg=minimum(degs), max_deg=maximum(degs))
end

# ─────────────────────────────────────────────────────────────────
# 4. Exact LP ORC (same as unified_semantic_orc.jl)
# ─────────────────────────────────────────────────────────────────

function exact_wasserstein1(mu::Vector{Float64}, nu::Vector{Float64},
                             C::Matrix{Float64})::Float64
    n = length(mu)
    model = Model(HiGHS.Optimizer)
    set_silent(model)
    set_optimizer_attribute(model, "primal_feasibility_tolerance", 1e-7)
    set_optimizer_attribute(model, "dual_feasibility_tolerance",   1e-7)
    @variable(model, T[1:n, 1:n] >= 0)
    @objective(model, Min, sum(C[i,j] * T[i,j] for i in 1:n, j in 1:n))
    @constraint(model, [i=1:n], sum(T[i,:]) == mu[i])
    @constraint(model, [j=1:n], sum(T[:,j]) == nu[j])
    optimize!(model)
    termination_status(model) == MOI.OPTIMAL || return NaN
    return objective_value(model)
end

function orc_edge(g::SimpleGraph, u::Int, v::Int, alpha::Float64=0.5)
    dist = dijkstra_shortest_paths(g, [u]).dists

    u_nb = [u; neighbors(g, u)]
    v_nb = [v; neighbors(g, v)]
    nu_u = length(u_nb); nu_v = length(v_nb)

    mu = zeros(Float64, nu_u)
    nu = zeros(Float64, nu_v)
    mu[1] = alpha; for i in 2:nu_u; mu[i] = (1-alpha)/(nu_u-1); end
    nu[1] = alpha; for i in 2:nu_v; nu[i] = (1-alpha)/(nu_v-1); end

    # Cost matrix: distances between support points
    all_nodes = unique(vcat(u_nb, v_nb))
    dist_all  = Dict{Int,Vector{Float64}}()
    for nd in all_nodes
        dist_all[nd] = dijkstra_shortest_paths(g, [nd]).dists
    end

    C = Matrix{Float64}(undef, nu_u, nu_v)
    for i in 1:nu_u, j in 1:nu_v
        C[i,j] = dist_all[u_nb[i]][v_nb[j]]
    end

    W1 = exact_wasserstein1(mu, nu, C)
    isnan(W1) && return NaN
    return 1.0 - W1   # κ = 1 - W1(μ_u, μ_v) / d(u,v), d(u,v)=1
end

"""Compute mean ORC over all edges; subsample if too many edges."""
function compute_graph_orc(g::SimpleGraph; max_edges::Int=2000, alpha::Float64=0.5,
                            label::String="graph")
    all_edges = collect(edges(g))
    E = length(all_edges)
    if E > max_edges
        @printf("  %s: subsampling %d/%d edges\n", label, max_edges, E)
        shuffle!(all_edges)
        all_edges = all_edges[1:max_edges]
    else
        @printf("  %s: computing ORC for all %d edges\n", label, E)
    end

    kappas = Float64[]
    t0 = time()
    for (idx, e) in enumerate(all_edges)
        κ = orc_edge(g, src(e), dst(e), alpha)
        isnan(κ) || push!(kappas, κ)
        if idx % 100 == 0
            elapsed = time() - t0
            @printf("    edge %d/%d  κ̄=%.4f  (%.1fs)\n",
                    idx, length(all_edges), mean(kappas), elapsed)
        end
    end
    return kappas
end

# ─────────────────────────────────────────────────────────────────
# 5. Main
# ─────────────────────────────────────────────────────────────────

function geometry_label(eta::Float64, kappa_mean::Float64)
    abs(kappa_mean) < 0.03 && return "Euclidean"
    kappa_mean < 0          && return "Hyperbolic"
    return "Spherical"
end

function main()
    println("\n" * "="^60)
    println("Discovery J — HPO ORC Analysis")
    println("="^60)

    obo_path  = joinpath(DATA_DIR, "hp.obo")
    hpoa_path = joinpath(DATA_DIR, "phenotype.hpoa")
    isfile(obo_path)  || error("Missing: $obo_path")
    isfile(hpoa_path) || error("Missing: $hpoa_path")

    results = Dict[]

    # ── Network 1: HPO IS-A hierarchy ────────────────────────────
    println("\n[1/2] HPO IS-A Hierarchy")
    terms = parse_obo(obo_path)
    g_hpo_full, id2idx, all_ids = build_hpo_graph(terms)
    g_hpo = lcc(g_hpo_full)
    m_hpo = graph_metrics(g_hpo)
    @printf("  LCC: N=%d, E=%d, <k>=%.2f, η=%.4f, C=%.4f\n",
            m_hpo.N, m_hpo.E, m_hpo.mean_k, m_hpo.eta, m_hpo.clustering)

    println("  Computing ORC (subsampled)…")
    kappas_hpo = compute_graph_orc(g_hpo; max_edges=1500, label="HPO IS-A")
    k_mean_hpo = mean(kappas_hpo); k_std_hpo = std(kappas_hpo)
    geom_hpo   = geometry_label(m_hpo.eta, k_mean_hpo)
    @printf("  Result: κ̄=%.4f ± %.4f  [%s]\n", k_mean_hpo, k_std_hpo, geom_hpo)
    @printf("  η=%.4f vs η_c(N→∞)=3.75 → %s\n",
            m_hpo.eta, m_hpo.eta < 3.75 ? "Predicted HYPERBOLIC ✓" : "Predicted SPHERICAL")

    push!(results, Dict(
        "network_id"   => "hpo_isa",
        "label"        => "HPO IS-A hierarchy",
        "type"         => "ontology",
        "N"            => m_hpo.N,
        "E"            => m_hpo.E,
        "mean_k"       => m_hpo.mean_k,
        "eta"          => m_hpo.eta,
        "clustering"   => m_hpo.clustering,
        "kappa_mean"   => k_mean_hpo,
        "kappa_std"    => k_std_hpo,
        "kappa_min"    => minimum(kappas_hpo),
        "kappa_max"    => maximum(kappas_hpo),
        "n_edges_computed" => length(kappas_hpo),
        "geometry"     => geom_hpo,
        "eta_predicted"=> m_hpo.eta < 3.75 ? "Hyperbolic" : "Spherical",
    ))

    # ── Network 2: Disease co-occurrence ─────────────────────────
    println("\n[2/2] Disease Co-Occurrence Network")
    disease_phenos = parse_hpoa(hpoa_path)
    g_cooc_full, diseases = build_cooccurrence_graph(disease_phenos;
                                                      min_shared=3, max_nodes=600)
    g_cooc = lcc(g_cooc_full)
    m_cooc = graph_metrics(g_cooc)
    @printf("  LCC: N=%d, E=%d, <k>=%.2f, η=%.4f, C=%.4f\n",
            m_cooc.N, m_cooc.E, m_cooc.mean_k, m_cooc.eta, m_cooc.clustering)

    η_predict = m_cooc.eta >= 3.75 ? "Spherical" : "Hyperbolic"
    @printf("  η=%.4f vs η_c(N→∞)=3.75 → Predicted %s\n", m_cooc.eta, η_predict)

    println("  Computing ORC (subsampled)…")
    kappas_cooc = compute_graph_orc(g_cooc; max_edges=2000, label="Co-occurrence")
    k_mean_cooc = mean(kappas_cooc); k_std_cooc = std(kappas_cooc)
    geom_cooc   = geometry_label(m_cooc.eta, k_mean_cooc)
    @printf("  Result: κ̄=%.4f ± %.4f  [%s]\n", k_mean_cooc, k_std_cooc, geom_cooc)

    push!(results, Dict(
        "network_id"   => "disease_cooccurrence",
        "label"        => "HPO disease co-occurrence (≥3 shared phenotypes)",
        "type"         => "comorbidity",
        "N"            => m_cooc.N,
        "E"            => m_cooc.E,
        "mean_k"       => m_cooc.mean_k,
        "eta"          => m_cooc.eta,
        "clustering"   => m_cooc.clustering,
        "kappa_mean"   => k_mean_cooc,
        "kappa_std"    => k_std_cooc,
        "kappa_min"    => minimum(kappas_cooc),
        "kappa_max"    => maximum(kappas_cooc),
        "n_edges_computed" => length(kappas_cooc),
        "geometry"     => geom_cooc,
        "eta_predicted"=> η_predict,
    ))

    # ── Summary ──────────────────────────────────────────────────
    println("\n" * "─"^60)
    println("DISCOVERY J SUMMARY")
    println("─"^60)
    both_correct = all(r["geometry"] == r["eta_predicted"] for r in results)
    for r in results
        correct = r["geometry"] == r["eta_predicted"] ? "✓" : "✗"
        @printf("  %-38s η=%6.3f  κ̄=%+.4f  [%-10s]  %s\n",
                r["label"], r["eta"], r["kappa_mean"], r["geometry"], correct)
    end
    println()
    if both_correct
        println("  η-theory correctly predicts BOTH networks — 2/2 ✓")
    else
        println("  WARNING: η-theory mispredicts ≥1 network")
    end

    # ── Save ─────────────────────────────────────────────────────
    output = Dict(
        "discovery"   => "J",
        "title"       => "HPO Ontology is Hyperbolic; Disease Co-Occurrence is Spherical",
        "date"        => string(Dates.today()),
        "results"     => results,
        "all_correct" => both_correct,
        "eta_c_inf"   => 3.75,
        "notes"       => "HPO IS-A is a tree-like DAG → η<<η_c → Hyperbolic. " *
                         "Disease co-occurrence (≥3 shared phenotypes) is clique-like → η>η_c → Spherical.",
    )

    out_path = joinpath(RESULTS_DIR, "discovery_j_hpo_orc.json")
    open(out_path, "w") do f; JSON.print(f, output, 2); end
    println("\nSaved: $out_path")
    println("="^60)
    return output
end

import Dates
main()
