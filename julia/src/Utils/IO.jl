"""
IO.jl - File I/O utilities

Utilities for reading and writing data files.
"""

using JSON
using CSV
using DataFrames

"""
Save results to JSON file.
"""
function save_results(results::Dict, filepath::String)
    open(filepath, "w") do f
        JSON.print(f, results, 2)
    end
end

"""
Load results from JSON file.
"""
function load_results(filepath::String)
    return JSON.parsefile(filepath)
end

"""
Save graph to CSV edge list.
"""
function save_graph_edgelist(graph, weights, filepath::String)
    edges = []
    for (u, v) in edges(graph)
        w = get(weights, (u, v), 1.0)
        push!(edges, (source=u, target=v, weight=w))
    end
    
    df = DataFrame(edges)
    CSV.write(filepath, df)
end

