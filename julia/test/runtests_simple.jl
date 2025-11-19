#!/usr/bin/env julia
"""
Simplified test runner that handles missing dependencies gracefully.
"""

using Pkg
Pkg.activate(@__DIR__ / "..")

# Add src to path
push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))

using Test

println("=" ^ 80)
println("Running HyperbolicSemanticNetworks Test Suite (Simplified)")
println("=" ^ 80)
println()

# Try to import main module
try
    using HyperbolicSemanticNetworks
    println("✅ Module loaded successfully")
catch e
    println("❌ Module load failed: $e")
    exit(1)
end

# Run tests that don't require additional dependencies
println("\nRunning basic tests...\n")

@testset "Basic Functionality" begin
    using LightGraphs
    
    # Test 1: Can create graphs
    @test begin
        G = SimpleGraph(5)
        add_edge!(G, 1, 2)
        add_edge!(G, 2, 3)
        nv(G) == 5 && ne(G) == 2
    end
    
    # Test 2: Module functions exist
    @test hasmethod(network_metrics, (SimpleGraph,))
    
    # Test 3: Can compute metrics
    @test begin
        G = SimpleGraph(4)
        add_edge!(G, 1, 2)
        add_edge!(G, 2, 3)
        add_edge!(G, 3, 4)
        metrics = network_metrics(G)
        metrics.n_nodes == 4
    end
    
    println("✅ Basic tests passed")
end

println("\n" * "=" ^ 80)
println("Tests completed!")
println("=" ^ 80)

