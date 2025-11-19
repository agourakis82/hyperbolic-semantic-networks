"""
Validation.jl - Data and graph validation

Validation utilities for ensuring data quality and graph structure.
"""

using LightGraphs

"""
    validate_graph(graph::SimpleGraph; check_connected::Bool=true, check_weights::Bool=true)

Validate graph structure.

# Returns
- Named tuple with validation status and errors
"""
function validate_graph(
    graph::SimpleGraph;
    check_connected::Bool = true,
    check_weights::Bool = true
)
    errors = String[]
    warnings = String[]
    
    # Check basic properties
    if nv(graph) == 0
        push!(errors, "Graph has no nodes")
    end
    
    if ne(graph) == 0
        push!(warnings, "Graph has no edges")
    end
    
    # Check connectivity
    if check_connected && nv(graph) > 0
        if !is_connected(graph)
            push!(warnings, "Graph is not connected (multiple components)")
        end
    end
    
    # Check for self-loops (SimpleGraph shouldn't have them, but check)
    for v in vertices(graph)
        if has_edge(graph, v, v)
            push!(errors, "Graph contains self-loop at node $v")
        end
    end
    
    # Validation result
    is_valid = length(errors) == 0
    
    return (
        is_valid = is_valid,
        errors = errors,
        warnings = warnings
    )
end

