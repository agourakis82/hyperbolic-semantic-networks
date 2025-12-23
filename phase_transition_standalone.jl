"""
PHASE TRANSITION EXPERIMENT - Standalone Version
Test the hypothesis: κ changes sign when ⟨k⟩² ≈ N

This uses the existing Rust FFI backend for fast Wasserstein computation.
"""

using Graphs
using Statistics
using Random
using JSON
using Printf

# Load Rust FFI library
const LIBCURVATURE = joinpath(@__DIR__, "rust/target/release/libhyperbolic_curvature.so")

if !isfile(LIBCURVATURE)
    println("⚠️  Rust library not found. Building...")
    run(`cargo build --release --manifest-path rust/curvature/Cargo.toml`)
end

# FFI functions
function compute_wasserstein1_ffi(mu::Vector{Float64}, nu::Vector{Float64},
                                   cost_matrix::Vector{Float64}, n::Int)::Float64
    return ccall((:compute_wasserstein1, LIBCURVATURE), Float64,
                 (Ptr{Float64}, Ptr{Float64}, Ptr{Float64}, Csize_t, Float64, Csize_t),
                 mu, nu, cost_matrix, n, 0.01, 1000)
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
    cost = zeros(n * n)
    for i in 1:n
        for j in 1:n
            node_i = all_nodes[i]
            node_j = all_nodes[j]

            if node_i == node_j
                cost[(i-1)*n + j] = 0.0
            else
                # Use BFS for shortest path
                path = gdistances(g, node_i)
                cost[(i-1)*n + j] = Float64(path[node_j])
            end
        end
    end

    # Compute Wasserstein-1 distance
    W1 = compute_wasserstein1_ffi(mu_vec, nu_vec, cost, n)

    # Curvature
    d_uv = 1.0
    kappa = 1.0 - W1 / d_uv

    return kappa
end

"""
Compute curvature for all edges.
"""
function compute_graph_curvature(g::SimpleGraph; alpha::Float64=0.5, parallel::Bool=true)::Dict{Tuple{Int,Int}, Float64}
    curvatures = Dict{Tuple{Int,Int}, Float64}()
    edges_list = collect(edges(g))

    if parallel && Threads.nthreads() > 1
        n_edges = length(edges_list)
        edge_pairs = Vector{Tuple{Int,Int}}(undef, n_edges)
        kappa_values = Vector{Float64}(undef, n_edges)

        Threads.@threads for i in 1:n_edges
            edge = edges_list[i]
            u_val = src(edge)
            v_val = dst(edge)
            edge_pairs[i] = (u_val, v_val)
            kappa_values[i] = compute_edge_curvature(g, u_val, v_val; alpha=alpha)
        end

        for i in 1:n_edges
            curvatures[edge_pairs[i]] = kappa_values[i]
        end
    else
        for edge in edges_list
            u_val = src(edge)
            v_val = dst(edge)
            curvatures[(u_val, v_val)] = compute_edge_curvature(g, u_val, v_val; alpha=alpha)
        end
    end

    return curvatures
end

"""
Create random regular graph with given degree k.
"""
function create_random_regular(N::Int, k::Int)::SimpleGraph
    # Ensure Nk is even
    if N * k % 2 != 0
        k += 1
    end

    # Configuration model: create stubs
    stubs = Int[]
    for node in 1:N
        append!(stubs, fill(node, k))
    end

    # Shuffle
    Random.seed!(42)
    shuffle!(stubs)

    # Create graph
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
        largest_cc = maximum(ccs; key=length)
        g = induced_subgraph(g, largest_cc)[1]
    end

    return g
end

"""
Run phase transition experiment.
"""
function run_experiment()
    println("="^70)
    println("PHASE TRANSITION EXPERIMENT - Julia/Rust")
    println("="^70)
    println()
    println("Using ", Threads.nthreads(), " threads")
    println()

    # Parameters
    N = 500
    k_values = [2, 3, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 60]

    k_critical = Int(round(sqrt(N)))

    println("Fixed network size: N = $N")
    println("Testing degrees: k ∈ ", k_values)
    println("Critical prediction: Transition near k ≈ √N = $k_critical")
    println("  (where ⟨k⟩²/N ≈ 1)")
    println()

    results = []

    for k in k_values
        println("\n", "="^70)
        println("Testing ⟨k⟩ = $k")
        println("="^70)

        # Compute critical ratio
        ratio = k^2 / N
        @printf("  ⟨k⟩²/N = %d²/%d = %.3f\n", k, N, ratio)

        # Predict geometry
        if ratio < 0.5
            predicted = "HYPERBOLIC (κ < 0)"
        elseif ratio < 2.0
            predicted = "TRANSITION (κ ≈ 0)"
        else
            predicted = "SPHERICAL (κ > 0)"
        end
        println("  Predicted: $predicted")

        # Create graph
        println("  Creating random $k-regular graph...")
        flush(stdout)
        g = create_random_regular(N, k)

        n_actual = nv(g)
        e_actual = ne(g)
        k_actual = 2 * e_actual / n_actual

        @printf("  Created: N=%d, E=%d, ⟨k⟩=%.2f\n", n_actual, e_actual, k_actual)

        # Compute curvature
        println("  Computing Ollivier-Ricci curvature...")
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

        @printf("  Computation time: %.1f seconds\n", elapsed)

        # Determine geometry
        if kappa_mean < -0.05
            actual = "HYPERBOLIC"
            symbol = "🔴"
        elseif kappa_mean > 0.05
            actual = "SPHERICAL"
            symbol = "🔵"
        else
            actual = "EUCLIDEAN/TRANSITION"
            symbol = "⚪"
        end

        @printf("  Result: κ = %.4f ± %.4f\n", kappa_mean, kappa_std)
        println("  $symbol $actual")

        # Check prediction
        match = (
            (ratio < 0.5 && kappa_mean < -0.05) ||
            (ratio > 2.0 && kappa_mean > 0.05) ||
            (0.5 <= ratio <= 2.0 && abs(kappa_mean) <= 0.05)
        )

        if match
            println("  ✅ Prediction CORRECT")
        else
            println("  ⚠️  Prediction MISMATCH")
        end

        # Store results
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
            "prediction_match" => match,
            "computation_time" => elapsed
        ))

        flush(stdout)
    end

    # Save results
    output_dir = "results/experiments"
    mkpath(output_dir)

    output_file = joinpath(output_dir, "phase_transition_julia_rust.json")

    output_data = Dict(
        "experiment" => "phase_transition",
        "hypothesis" => "Transition at k²/N ≈ 1",
        "N_fixed" => N,
        "k_critical" => k_critical,
        "n_threads" => Threads.nthreads(),
        "results" => results
    )

    open(output_file, "w") do f
        JSON.print(f, output_data, 2)
    end

    println("\n", "="^70)
    println("RESULTS SAVED")
    println("="^70)
    println("File: $output_file")

    # Analysis
    analyze_results(results, N)

    return results
end

function analyze_results(results, N)
    println("\n", "="^70)
    println("ANALYSIS")
    println("="^70)

    # Count geometries
    n_hyperbolic = count(r -> r["kappa_mean"] < -0.05, results)
    n_euclidean = count(r -> abs(r["kappa_mean"]) <= 0.05, results)
    n_spherical = count(r -> r["kappa_mean"] > 0.05, results)

    println("\nGeometry distribution:")
    println("  Hyperbolic: $n_hyperbolic/$(length(results))")
    println("  Euclidean:  $n_euclidean/$(length(results))")
    println("  Spherical:  $n_spherical/$(length(results))")

    # Find transition point
    println("\nFinding transition point...")

    sorted_results = sort(results, by=r -> r["k_actual"])

    transition_k = nothing
    for i in 1:(length(sorted_results)-1)
        k1 = sorted_results[i]["k_actual"]
        k2 = sorted_results[i+1]["k_actual"]
        kappa1 = sorted_results[i]["kappa_mean"]
        kappa2 = sorted_results[i+1]["kappa_mean"]

        if kappa1 < 0 && kappa2 > 0
            transition_k = k1 + (k2 - k1) * abs(kappa1) / (abs(kappa1) + abs(kappa2))
            @printf("  Transition between ⟨k⟩=%.1f and ⟨k⟩=%.1f\n", k1, k2)
            @printf("  Estimated: ⟨k⟩ ≈ %.1f\n", transition_k)
            break
        end
    end

    if transition_k !== nothing
        transition_ratio = transition_k^2 / N
        @printf("  Ratio at transition: ⟨k⟩²/N ≈ %.2f\n", transition_ratio)

        if 0.5 <= transition_ratio <= 2.0
            println("  ✅ HYPOTHESIS CONFIRMED: Transition near ⟨k⟩²/N ≈ 1")
        else
            println("  ⚠️  HYPOTHESIS NEEDS REVISION")
        end
    end

    # Accuracy
    n_correct = count(r -> r["prediction_match"], results)
    accuracy = n_correct / length(results) * 100

    @printf("\nPrediction accuracy: %d/%d (%.1f%%)\n",
            n_correct, length(results), accuracy)

    # Performance
    total_time = sum(r["computation_time"] for r in results)
    @printf("\nTotal computation time: %.1f seconds\n", total_time)

    println("\n", "="^70)
    println("EXPERIMENT COMPLETE! ✅")
    println("="^70)
end

# Run
if abspath(PROGRAM_FILE) == @__FILE__
    run_experiment()
end
