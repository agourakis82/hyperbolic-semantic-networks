"""
ConceptNet.jl - ConceptNet knowledge graph loader

Loads ConceptNet data and constructs semantic graphs.
"""

using LightGraphs
using JSON

"""
    load_conceptnet(filepath::String; language::String="en", relation_types::Vector{String}=["RelatedTo"])

Load ConceptNet knowledge graph.

# Arguments
- `filepath`: Path to ConceptNet JSON file
- `language`: Language code (default: "en")
- `relation_types`: Types of relations to include (default: ["RelatedTo"])

# Returns
- Graph and metadata
"""
function load_conceptnet(
    filepath::String;
    language::String = "en",
    relation_types::Vector{String} = ["RelatedTo"]
)
    if !isfile(filepath)
        throw(ErrorException("ConceptNet file not found: $filepath"))
    end
    
    # Load JSON
    data = JSON.parsefile(filepath)
    
    # Extract edges
    edges = []
    node_set = Set{String}()
    
    for edge in data["edges"]
        if edge["rel"] in relation_types
            source = edge["start"]
            target = edge["end"]
            weight = get(edge, "weight", 1.0)
            
            push!(edges, (source, target, weight))
            push!(node_set, source)
            push!(node_set, target)
        end
    end
    
    # Create graph
    nodes = collect(node_set)
    node_map = Dict(node => i for (i, node) in enumerate(nodes))
    
    G = SimpleGraph(length(nodes))
    edge_weights = Dict{Tuple{Int, Int}, Float64}()
    
    for (source, target, weight) in edges
        u = node_map[source]
        v = node_map[target]
        if u != v
            add_edge!(G, u, v)
            edge_weights[(u, v)] = weight
        end
    end
    
    return (graph=G, weights=edge_weights, node_map=node_map)
end

