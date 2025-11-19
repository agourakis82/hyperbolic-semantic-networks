"""
Test suite for preprocessing modules.

Tests data loading and graph construction.
"""

using Test
using HyperbolicSemanticNetworks

@testset "SWOW Loader" begin
    # Create test CSV file
    test_file = tempname() * ".csv"
    
    # Write test data
    open(test_file, "w") do f
        println(f, "source,target,weight")
        println(f, "word1,word2,0.5")
        println(f, "word2,word3,0.3")
        println(f, "word1,word3,0.2")
    end
    
    try
        result = load_swow(test_file, language="test", min_weight=0.0)
        
        @test haskey(result, :graph)
        @test haskey(result, :weights)
        @test haskey(result, :node_map)
        
        G = result.graph
        @test nv(G) == 3
        @test ne(G) >= 2  # At least some edges
        
        # Cleanup
    finally
        rm(test_file, force=true)
    end
end

@testset "Graph Validation" begin
    using LightGraphs
    
    # Valid graph
    G1 = SimpleGraph(4)
    add_edge!(G1, 1, 2)
    add_edge!(G1, 2, 3)
    add_edge!(G1, 3, 4)
    
    result1 = validate_graph(G1)
    @test result1.is_valid == true
    @test isempty(result1.errors)
    
    # Empty graph (warning, not error)
    G2 = SimpleGraph(0)
    result2 = validate_graph(G2, check_connected=false)
    @test !isempty(result2.warnings) || !result2.is_valid
end

@testset "Network Metrics" begin
    using LightGraphs
    
    # Create test graph
    G = SimpleGraph(5)
    add_edge!(G, 1, 2)
    add_edge!(G, 2, 3)
    add_edge!(G, 3, 4)
    add_edge!(G, 4, 5)
    add_edge!(G, 5, 1)
    add_edge!(G, 1, 3)  # Triangle
    
    metrics = network_metrics(G)
    
    @test metrics.n_nodes == 5
    @test metrics.n_edges == 6
    @test 0.0 <= metrics.clustering <= 1.0
    @test metrics.degree_mean >= 0.0
    @test metrics.degree_std >= 0.0
end

