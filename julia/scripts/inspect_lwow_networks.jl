"""
Inspect LWOW network properties before running expensive ORC.
Computes N, E, <k>, η, clustering C for each LLM network
and compares to SWOW-EN baseline.
"""

using Pkg; Pkg.instantiate()
using CSV, DataFrames, Graphs, Statistics, Printf

DATA_DIR = joinpath(@__DIR__, "../../data/processed")

η_c_inf = 3.75  # asymptotic critical density
η_c(N) = 3.75 - 14.62 / sqrt(N)  # finite-size scaling

function load_and_inspect(filename, label)
    filepath = joinpath(DATA_DIR, filename)
    df = CSV.read(filepath, DataFrame; stringtype=String)
    # Collect unique nodes
    all_nodes = sort(unique(vcat(df.source, df.target)))
    N = length(all_nodes)
    node_to_id = Dict(name => i for (i, name) in enumerate(all_nodes))

    g = SimpleGraph(N)
    for row in eachrow(df)
        u = node_to_id[row.source]
        v = node_to_id[row.target]
        u != v && add_edge!(g, u, v)
    end

    # Largest connected component
    components = connected_components(g)
    lcc_nodes = components[argmax(length.(components))]
    g_lcc = induced_subgraph(g, lcc_nodes)[1]
    N_lcc = nv(g_lcc)
    E_lcc = ne(g_lcc)
    k_mean = 2E_lcc / N_lcc
    η = k_mean^2 / N_lcc
    σ_k = std(degree(g_lcc))

    # Clustering coefficient
    tris = 0; trips = 0
    for v in vertices(g_lcc)
        nbrs = neighbors(g_lcc, v)
        d = length(nbrs)
        d < 2 && continue
        trips += d * (d - 1)
        for i in 1:length(nbrs), j in (i+1):length(nbrs)
            has_edge(g_lcc, nbrs[i], nbrs[j]) && (tris += 2)
        end
    end
    C = trips > 0 ? tris / trips : 0.0

    ηc = η_c(N_lcc)
    regime = η > η_c_inf ? "SPHERICAL (above η_c^∞)" :
             η > ηc ? "SPHERICAL (above η_c(N))" :
             η < ηc ? "HYPERBOLIC (below η_c(N))" : "CRITICAL"

    println("─"^60)
    println("  Network : $label")
    println("  File    : $filename")
    println("  N (LCC) : $N_lcc  (total unique nodes: $N)")
    println("  E (LCC) : $E_lcc")
    println("  <k>     : $(round(k_mean, digits=3))")
    println("  σ_k     : $(round(σ_k, digits=3))")
    println("  η = <k>²/N : $(round(η, digits=4))")
    println("  η_c(N)  : $(round(ηc, digits=3))")
    println("  C (clust): $(round(C, digits=4))")
    println("  Regime  : $regime")
    println()
    return (label=label, N=N_lcc, E=E_lcc, k_mean=k_mean, eta=η, eta_c=ηc, C=C, regime=regime)
end

println("\n" * "="^60)
println("  LWOW Network Property Inspection")
println("  (ORC computation is next; this is fast pre-check)")
println("="^60 * "\n")

results = []
push!(results, load_and_inspect("english_edges_FINAL.csv", "SWOW-EN (Human)"))
push!(results, load_and_inspect("lwow_haiku_edges.csv",    "LWOW-Haiku (Claude)"))
push!(results, load_and_inspect("lwow_mistral_edges.csv",  "LWOW-Mistral"))
push!(results, load_and_inspect("lwow_llama3_edges.csv",   "LWOW-Llama3"))

println("="^60)
println("  COMPARISON SUMMARY")
println("="^60)
println("  Network              N        η        C       Regime")
println("  " * "-"^56)
for r in results
    @printf("  %-22s %-8d %-8.4f %-7.4f %s\n", r.label, r.N, r.eta, r.C, r.regime)
end
println()
println("  η_c^∞ = $η_c_inf  (phase boundary)")
println("  Prediction: if η >> η_c(N) → SPHERICAL (LLMs 'over-associate')")
println("              if η ~= η_human → same geometry as humans")
