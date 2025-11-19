"""
SWOW.jl - Small World of Words data loader

Loads and preprocesses SWOW association data.
"""

using LightGraphs
using DataFrames
using CSV

"""
    load_swow(filepath::String; language::String="english", max_nodes::Union{Int, Nothing}=nothing, min_weight::Float64=0.0)

Load SWOW association data from CSV file.

# Arguments
- `filepath`: Path to SWOW CSV file
- `language`: Language code (optional, default: "english")
- `max_nodes`: Maximum nodes to load (optional)
- `min_weight`: Minimum edge weight threshold (default: 0.0)

# Returns
- `SimpleGraph` with edge weights stored in metadata

# Throws
- `DataLoadError` if file not found or invalid format
"""
function load_swow(
    filepath::String;
    language::String = "english",
    max_nodes::Union{Int, Nothing} = nothing,
    min_weight::Float64 = 0.0
)
    # Check file exists
    if !isfile(filepath)
        throw(ErrorException("SWOW file not found: $filepath"))
    end
    
    # Load CSV
    df = CSV.read(filepath, DataFrame)
    
    # Validate required columns
    required_cols = ["source", "target", "weight"]
    for col in required_cols
        if !(col in names(df))
            throw(ErrorException("Missing required column: $col"))
        end
    end
    
    # Filter by weight
    if min_weight > 0.0
        df = filter(row -> row.weight >= min_weight, df)
    end
    
    # Get unique nodes
    all_nodes = unique(vcat(df.source, df.target))
    
    # Limit nodes if specified
    if max_nodes !== nothing && length(all_nodes) > max_nodes
        # Sort by frequency and take top N
        node_counts = countmap(vcat(df.source, df.target))
        top_nodes = sort(collect(keys(node_counts)), by=x->node_counts[x], rev=true)[1:max_nodes]
        df = filter(row -> row.source in top_nodes && row.target in top_nodes, df)
        all_nodes = top_nodes
    end
    
    # Create graph
    G = SimpleGraph(length(all_nodes))
    
    # Create node mapping
    node_map = Dict(node => i for (i, node) in enumerate(all_nodes))
    
    # Add edges with weights
    edge_weights = Dict{Tuple{Int, Int}, Float64}()
    for row in eachrow(df)
        u = node_map[row.source]
        v = node_map[row.target]
        if u != v
            add_edge!(G, u, v)
            edge_weights[(u, v)] = row.weight
        end
    end
    
    # Store metadata
    # Note: LightGraphs doesn't natively support edge weights in SimpleGraph
    # We'll need to use MetaGraphs or store weights separately
    # For now, return graph and weights separately
    
    return (graph=G, weights=edge_weights, node_map=node_map)
end

# Helper function
function countmap(v::Vector)
    counts = Dict{eltype(v), Int}()
    for x in v
        counts[x] = get(counts, x, 0) + 1
    end
    return counts
end

