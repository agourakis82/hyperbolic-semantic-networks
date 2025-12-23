m"""
PHASE TRANSITION EXPERIMENT
Test the hypothesis: κ changes sign when ⟨k⟩² ≈ N

This will systematically vary ⟨k⟩ at fixed N and measure curvature.
"""

using Graphs
using Statistics
using Random
using JSON
using Printf

# Add parent directory to load path
push!(LOAD_PATH, joinpath(@__DIR__, ".."))

using HyperbolicSemanticNetworks
using HyperbolicSemanticNetworks.Curvature

"""
Create random regular graph with given degree k.
"""
function create_random_regular(N::Int, k::Int)::SimpleGraph
    # Ensure Nk is even
    if N * k % 2 != 0
        k += 1
    end

    # Use configuration model
    degree_sequence = fill(k, N)

    # Create stubs
    stubs = Int[]
    for (node, deg) in enumerate(degree_sequence)
        append!(stubs, fill(node, deg))
    end

    # Shuffle and pair
    Random.seed!(42)
    shuffle!(stubs)

    # Create graph
    g = SimpleGraph(N)

    for i in 1:2:length(stubs)-1
        u, v = stubs[i], stubs[i+1]
        if u != v && !has_edge(g, u, v)
            add_edge!(g, u, v)
        end
    end

    # Get LCC
    ccs = connected_components(g)
    largest_cc = maximum(ccs, key=length)
    g_lcc = induced_subgraph(g, largest_cc)[1]

    return g_lcc
end

"""
Compute network statistics.
"""
function compute_network_stats(g::SimpleGraph)
    N = nv(g)
    E = ne(g)
    avg_degree = 2 * E / N

    return (
        N = N,
        E = E,
        avg_degree = avg_degree,
        ratio = avg_degree^2 / N
    )
end

"""
Run phase transition experiment.
"""
function run_experiment()
    println("="^70)
    println("PHASE TRANSITION EXPERIMENT - Julia Implementation")
    println("="^70)
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
        g = create_random_regular(N, k)

        stats = compute_network_stats(g)
        @printf("  Created: N=%d, E=%d, ⟨k⟩=%.2f\n",
                stats.N, stats.E, stats.avg_degree)

        # Compute curvature
        println("  Computing Ollivier-Ricci curvature...")
        flush(stdout)

        curvatures = compute_graph_curvature(g, alpha=0.5, parallel=true)

        kappa_values = collect(values(curvatures))
        kappa_mean = mean(kappa_values)
        kappa_std = std(kappa_values)
        kappa_median = median(kappa_values)
        kappa_min = minimum(kappa_values)
        kappa_max = maximum(kappa_values)

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
            "k_actual" => stats.avg_degree,
            "N" => stats.N,
            "E" => stats.E,
            "ratio" => stats.ratio,
            "kappa_mean" => kappa_mean,
            "kappa_std" => kappa_std,
            "kappa_median" => kappa_median,
            "kappa_min" => kappa_min,
            "kappa_max" => kappa_max,
            "geometry" => actual,
            "prediction_match" => match
        ))

        flush(stdout)
    end

    # Save results
    output_dir = joinpath(@__DIR__, "../../results/experiments")
    mkpath(output_dir)

    output_file = joinpath(output_dir, "phase_transition_experiment_julia.json")

    output_data = Dict(
        "experiment" => "phase_transition",
        "hypothesis" => "Transition at k²/N ≈ 1",
        "N_fixed" => N,
        "k_critical" => k_critical,
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
            # Linear interpolation
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

    println("\n", "="^70)
    println("EXPERIMENT COMPLETE! ✅")
    println("="^70)

    return results
end

# Run experiment
if abspath(PROGRAM_FILE) == @__FILE__
    results = run_experiment()
end
