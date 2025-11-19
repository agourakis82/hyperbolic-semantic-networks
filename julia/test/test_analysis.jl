"""
Test suite for analysis modules.

Tests null models, bootstrap, and Ricci flow.
"""

using Test
using LightGraphs
using HyperbolicSemanticNetworks

@testset "Null Models" begin
    # Create test graph
    G = SimpleGraph(5)
    add_edge!(G, 1, 2)
    add_edge!(G, 2, 3)
    add_edge!(G, 3, 4)
    add_edge!(G, 4, 5)
    add_edge!(G, 5, 1)
    
    @testset "Configuration model" begin
        nulls = generate_null_models(G, method=:configuration, n_samples=10)
        
        @test length(nulls) == 10
        
        # Check degree preservation (approximately)
        original_degrees = sort([degree(G, v) for v in vertices(G)])
        for null in nulls
            null_degrees = sort([degree(null, v) for v in vertices(null)])
            @test sum(null_degrees) == sum(original_degrees)  # Total degree preserved
        end
    end
    
    @testset "Triadic-rewire" begin
        nulls = generate_null_models(G, method=:triadic_rewire, n_samples=5)
        @test length(nulls) == 5
    end
end

@testset "Bootstrap Analysis" begin
    G = SimpleGraph(20)
    for i in 1:19
        add_edge!(G, i, i+1)
    end
    
    # Simple statistic: number of edges
    function edge_count(g::SimpleGraph)::Float64
        return Float64(ne(g))
    end
    
    result = bootstrap_analysis(G, edge_count, n_samples=100, sample_size=0.8)
    
    @test haskey(result, :mean)
    @test haskey(result, :std)
    @test haskey(result, :ci_lower)
    @test haskey(result, :ci_upper)
    @test result.ci_lower <= result.mean <= result.ci_upper
end

@testset "Ricci Flow" begin
    G = SimpleGraph(10)
    for i in 1:9
        add_edge!(G, i, i+1)
    end
    add_edge!(G, 1, 10)  # Close the cycle
    
    result = ricci_flow(G, max_iterations=5, alpha=0.5)
    
    @test haskey(result, :trajectory)
    @test haskey(result, :converged)
    @test haskey(result, :iterations)
    @test length(result.trajectory) > 0
    @test result.iterations >= 0
end

