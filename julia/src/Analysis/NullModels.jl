"""
NullModels.jl - Null model generation

Configuration model and triadic-rewire null models.
Uses Rust backend for parallel generation.
"""

using Graphs  # Replaces deprecated LightGraphs
using Statistics
using Random

# TODO: Add FFI bindings to Rust null_models library
# For now, use Julia implementation

"""
    generate_null_models(graph::SimpleGraph; method::Symbol=:configuration, n_samples::Int=1000, parallel::Bool=true)

Generate null model networks.

# Arguments
- `graph`: Input graph
- `method`: `:configuration` or `:triadic_rewire`
- `n_samples`: Number of null model replicates
- `parallel`: Use parallel generation

# Returns
- Vector of null model graphs
"""
function generate_null_models(
    graph::SimpleGraph;
    method::Symbol = :configuration,
    n_samples::Int = 1000,
    parallel::Bool = true
)
    if method == :configuration
        return generate_configuration_models(graph, n_samples, parallel)
    elseif method == :triadic_rewire
        return generate_triadic_rewire_models(graph, n_samples, parallel)
    else
        throw(ErrorException("Unknown method: $method. Use :configuration or :triadic_rewire"))
    end
end

"""
Generate configuration model null networks.

Preserves degree sequence, randomizes edges.
"""
function generate_configuration_models(
    graph::SimpleGraph,
    n_samples::Int,
    parallel::Bool
)
    # Get degree sequence
    degrees = [degree(graph, v) for v in vertices(graph)]

    if parallel && Threads.nthreads() > 1
        # Parallel generation using multi-threading
        null_models = Vector{SimpleGraph}(undef, n_samples)

        Threads.@threads for i in 1:n_samples
            null_models[i] = sample_configuration_model(degrees)
        end

        return null_models
    else
        # Serial generation
        null_models = Vector{SimpleGraph}()

        for _ in 1:n_samples
            null_graph = sample_configuration_model(degrees)
            push!(null_models, null_graph)
        end

        return null_models
    end
end

"""
Sample a single configuration model network.
"""
function sample_configuration_model(degrees::Vector{Int})::SimpleGraph
    MAX_ATTEMPTS = 200

    for _ in 1:MAX_ATTEMPTS
        G = try_simple_pairing(degrees)
        if G !== nothing
            return G
        end
    end

    # Fallback: sequence not realized as a simple graph within the
    # attempt budget. Return the node set without edges rather than a
    # graph that silently violates the degree sequence.
    return SimpleGraph(length(degrees))
end

"""
One attempt at pairing stubs into a simple graph.

The naive configuration model rejects self-loops and duplicate edges,
which silently breaks the degree sequence. Here any collision aborts
the attempt so the caller can reshuffle and retry, preserving the
degree sequence exactly whenever it is graphical enough to be realized
within the attempt budget.
"""
function try_simple_pairing(degrees::Vector{Int})::Union{SimpleGraph, Nothing}
    # Create stubs (half-edges)
    stubs = Int[]
    for (node_id, deg) in enumerate(degrees)
        for _ in 1:deg
            push!(stubs, node_id)
        end
    end

    # Odd number of stubs can never pair
    if isodd(length(stubs))
        return nothing
    end

    # Shuffle stubs
    shuffle!(stubs)

    # Create graph
    n = length(degrees)
    G = SimpleGraph(n)

    # Pair stubs to form edges; abort on self-loop or duplicate
    for i in 1:2:length(stubs)
        u = stubs[i]
        v = stubs[i + 1]
        if u == v || has_edge(G, u, v)
            return nothing
        end
        add_edge!(G, u, v)
    end

    return G
end

"""
Generate triadic-rewire null networks.

Preserves triangle counts, randomizes other edges.
"""
function generate_triadic_rewire_models(
    graph::SimpleGraph,
    n_samples::Int,
    parallel::Bool
)
    # TODO: Implement proper triadic-rewire or connect to Rust FFI
    # For now, return copies (placeholder)

    if parallel && Threads.nthreads() > 1
        # Parallel generation
        null_models = Vector{SimpleGraph}(undef, n_samples)

        Threads.@threads for i in 1:n_samples
            # Placeholder: return copy of original
            # Full implementation will preserve triangles and rewire other edges
            null_models[i] = copy(graph)
        end

        return null_models
    else
        # Serial generation
        null_models = Vector{SimpleGraph}()

        for _ in 1:n_samples
            # Placeholder: return copy of original
            push!(null_models, copy(graph))
        end

        return null_models
    end
end

"""
Compute statistics comparing real graph to null models.

# Returns
- Named tuple with mean, std, p-value, effect size
"""
function compare_with_nulls(
    real_value::Float64,
    null_values::Vector{Float64}
)
    null_mean = mean(null_values)
    null_std = std(null_values)
    
    # Effect size (difference)
    effect_size = real_value - null_mean
    
    # Monte Carlo p-value (one-tailed)
    p_value = sum(null_values .>= real_value) / length(null_values)
    
    # Standardized effect (z-score)
    if null_std > 0
        z_score = effect_size / null_std
    else
        z_score = 0.0
    end
    
    return (
        real_value = real_value,
        null_mean = null_mean,
        null_std = null_std,
        effect_size = effect_size,
        z_score = z_score,
        p_value = p_value
    )
end
