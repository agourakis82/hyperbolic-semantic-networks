"""
PHASE TRANSITION EXPERIMENT - Pure Julia (N=100 Reference)
Matches Sounio k-values for direct comparison.

Uses Sinkhorn algorithm: epsilon=0.01, max_iter=1000, tol=1e-6
Computes ALL edges (no limiting).
"""

using Graphs
using Statistics
using Random
using JSON
using Printf
using LinearAlgebra

"""
Compute Wasserstein-1 distance using Sinkhorn algorithm.
"""
function sinkhorn_wasserstein(mu::Vector{Float64}, nu::Vector{Float64},
                              C::Matrix{Float64}; epsilon::Float64=0.01,
                              max_iter::Int=1000, tol::Float64=1e-6)::Float64
    n = length(mu)

    # Initialize
    K = exp.(-C / epsilon)
    u = ones(n)
    v = ones(n)

    for iter in 1:max_iter
        u_old = copy(u)

        # Update u and v
        u = mu ./ (K * v)
        v = nu ./ (K' * u)

        # Replace NaN/Inf with 1.0
        u = map(x -> isfinite(x) ? x : 1.0, u)
        v = map(x -> isfinite(x) ? x : 1.0, v)

        # Check convergence
        if iter % 10 == 0
            if norm(u - u_old, 1) < tol
                break
            end
        end
    end

    # Compute transport matrix
    P = Diagonal(u) * K * Diagonal(v)

    # Compute distance
    W1 = sum(P .* C)

    return W1
end

"""
Compute Ollivier-Ricci curvature for an edge.
"""
function compute_edge_curvature(g::SimpleGraph, u::Int, v::Int; alpha::Float64=0.5)::Float64
    # Build probability measures
    mu_u = Dict{Int, Float64}()
    mu_v = Dict{Int, Float64}()

    # Idleness
    mu_u[u] = alpha
    mu_v[v] = alpha

    # Neighbors
    neighbors_u = neighbors(g, u)
    neighbors_v = neighbors(g, v)

    if length(neighbors_u) > 0
        for z in neighbors_u
            mu_u[z] = get(mu_u, z, 0.0) + (1 - alpha) / length(neighbors_u)
        end
    end

    if length(neighbors_v) > 0
        for z in neighbors_v
            mu_v[z] = get(mu_v, z, 0.0) + (1 - alpha) / length(neighbors_v)
        end
    end

    # Get all nodes in support
    all_nodes = sort(unique(vcat(collect(keys(mu_u)), collect(keys(mu_v)))))
    n = length(all_nodes)
    node_to_idx = Dict(node => i for (i, node) in enumerate(all_nodes))

    # Build probability vectors
    mu_vec = zeros(n)
    nu_vec = zeros(n)

    for (node, prob) in mu_u
        mu_vec[node_to_idx[node]] = prob
    end

    for (node, prob) in mu_v
        nu_vec[node_to_idx[node]] = prob
    end

    # Build cost matrix (shortest path distances)
    C = zeros(n, n)
    for i in 1:n
        path_lengths = gdistances(g, all_nodes[i])
        for j in 1:n
            C[i, j] = Float64(path_lengths[all_nodes[j]])
        end
    end

    # Compute Wasserstein-1 distance
    W1 = sinkhorn_wasserstein(mu_vec, nu_vec, C)

    # Curvature
    d_uv = 1.0
    kappa = 1.0 - W1 / d_uv

    return kappa
end

"""
Compute curvature for all edges (with progress tracking).
"""
function compute_graph_curvature(g::SimpleGraph; alpha::Float64=0.5,
                                parallel::Bool=true)::Dict{Tuple{Int,Int}, Float64}
    curvatures = Dict{Tuple{Int,Int}, Float64}()
    edges_list = collect(edges(g))
    n_edges = length(edges_list)

    if parallel && Threads.nthreads() > 1
        edge_pairs = Vector{Tuple{Int,Int}}(undef, n_edges)
        kappa_values = Vector{Float64}(undef, n_edges)

        Threads.@threads for i in 1:n_edges
            edge = edges_list[i]
            u_val = src(edge)
            v_val = dst(edge)
            edge_pairs[i] = (u_val, v_val)
            kappa_values[i] = compute_edge_curvature(g, u_val, v_val; alpha=alpha)

            # Progress
            if i % 100 == 0
                @printf("    Progress: %d/%d edges (%.1f%%)\n", i, n_edges, 100*i/n_edges)
                flush(stdout)
            end
        end

        for i in 1:n_edges
            curvatures[edge_pairs[i]] = kappa_values[i]
        end
    else
        for (i, edge) in enumerate(edges_list)
            u_val = src(edge)
            v_val = dst(edge)
            curvatures[(u_val, v_val)] = compute_edge_curvature(g, u_val, v_val; alpha=alpha)

            if i % 100 == 0
                @printf("    Progress: %d/%d edges (%.1f%%)\n", i, n_edges, 100*i/n_edges)
                flush(stdout)
            end
        end
    end

    return curvatures
end

"""
Create random regular graph.
"""
function create_random_regular(N::Int, k::Int)::SimpleGraph
    if N * k % 2 != 0
        k += 1
    end

    # Configuration model
    stubs = Int[]
    for node in 1:N
        append!(stubs, fill(node, k))
    end

    Random.seed!(42 + k)  # Different seed for each k
    shuffle!(stubs)

    g = SimpleGraph(N)

    for i in 1:2:length(stubs)-1
        u_val = stubs[i]
        v_val = stubs[i+1]
        if u_val != v_val && !has_edge(g, u_val, v_val)
            add_edge!(g, u_val, v_val)
        end
    end

    # Get LCC
    ccs = connected_components(g)
    if length(ccs) > 1
        largest_cc = ccs[argmax(length.(ccs))]
        g = induced_subgraph(g, largest_cc)[1]
    end

    return g
end

"""
Run experiment at N=100.
"""
function run_experiment()
    println("="^70)
    println("PHASE TRANSITION - Julia N=100 Reference")
    println("Sinkhorn: epsilon=0.01, max_iter=1000, tol=1e-6")
    println("="^70)
    println()
    println("Using ", Threads.nthreads(), " thread(s)")
    println()

    N = 100
    k_values = [2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40]

    k_critical = Int(round(sqrt(2.5 * N)))

    println("Fixed network size: N = $N")
    println("Testing degrees: k in ", k_values)
    println("Critical prediction: Transition near k = sqrt(2.5*N) = $k_critical")
    println()

    results = []

    for k in k_values
        println("\n", "="^70)
        println("Testing k = $k")
        println("="^70)

        ratio = k^2 / N
        @printf("  k^2/N = %d^2/%d = %.3f\n", k, N, ratio)

        if ratio < 2.0
            predicted = "HYPERBOLIC"
        elseif ratio < 3.5
            predicted = "TRANSITION"
        else
            predicted = "SPHERICAL"
        end
        println("  Predicted: $predicted")

        println("  Creating random $k-regular graph...")
        flush(stdout)
        g = create_random_regular(N, k)

        n_actual = nv(g)
        e_actual = ne(g)
        k_actual = 2 * e_actual / n_actual

        @printf("  Created: N=%d, E=%d, <k>=%.2f\n", n_actual, e_actual, k_actual)

        println("  Computing Ollivier-Ricci curvature (ALL edges)...")
        flush(stdout)

        start_time = time()
        curvatures = compute_graph_curvature(g; alpha=0.5, parallel=true)
        elapsed = time() - start_time

        kappa_values = collect(values(curvatures))
        kappa_mean = mean(kappa_values)
        kappa_std = std(kappa_values)
        kappa_median = median(kappa_values)
        kappa_min = minimum(kappa_values)
        kappa_max = maximum(kappa_values)

        @printf("  Time: %.1f seconds\n", elapsed)

        if kappa_mean < -0.05
            actual = "HYPERBOLIC"
        elseif kappa_mean > 0.05
            actual = "SPHERICAL"
        else
            actual = "EUCLIDEAN/TRANSITION"
        end

        @printf("  Result: kappa = %.6f +/- %.6f  [%s]\n", kappa_mean, kappa_std, actual)

        push!(results, Dict(
            "k_target" => k,
            "k_actual" => k_actual,
            "N" => n_actual,
            "E" => e_actual,
            "ratio" => ratio,
            "kappa_mean" => kappa_mean,
            "kappa_std" => kappa_std,
            "kappa_median" => kappa_median,
            "kappa_min" => kappa_min,
            "kappa_max" => kappa_max,
            "geometry" => actual,
            "computation_time" => elapsed
        ))

        flush(stdout)
    end

    # Save
    output_dir = "results/experiments"
    mkpath(output_dir)

    output_file = joinpath(output_dir, "phase_transition_julia_n100.json")

    output_data = Dict(
        "experiment" => "phase_transition_n100",
        "description" => "N=100 reference for Sounio comparison",
        "sinkhorn" => Dict("epsilon" => 0.01, "max_iter" => 1000, "tol" => 1e-6),
        "alpha" => 0.5,
        "N_fixed" => N,
        "k_critical" => k_critical,
        "n_threads" => Threads.nthreads(),
        "results" => results
    )

    open(output_file, "w") do f
        JSON.print(f, output_data, 2)
    end

    println("\n", "="^70)
    println("RESULTS SAVED: $output_file")
    println("="^70)

    # Summary table
    println("\nk\tratio\tkappa_mean\tgeometry")
    for r in sort(results, by=r -> r["k_target"])
        @printf("%d\t%.2f\t%.6f\t%s\n", r["k_target"], r["ratio"], r["kappa_mean"], r["geometry"])
    end
end

# Run
if abspath(PROGRAM_FILE) == @__FILE__
    run_experiment()
end
