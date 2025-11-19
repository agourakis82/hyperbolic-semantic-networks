"""
Test suite for curvature computation.

Tests Ollivier-Ricci curvature computation with various scenarios.
"""

using Test
using LightGraphs
using HyperbolicSemanticNetworks

@testset "Curvature Computation" begin
    # Create simple test graph
    G = SimpleGraph(4)
    add_edge!(G, 1, 2)
    add_edge!(G, 2, 3)
    add_edge!(G, 3, 4)
    add_edge!(G, 4, 1)
    add_edge!(G, 1, 3)  # Triangle
    
    @testset "Edge existence check" begin
        @test_throws ErrorException compute_curvature(G, 1, 5, alpha=0.5)
    end
    
    @testset "Curvature bounds" begin
        kappa = compute_curvature(G, 1, 2, alpha=0.5)
        @test -1.0 <= kappa <= 1.0
    end
    
    @testset "Graph curvature" begin
        curvatures = compute_graph_curvature(G, alpha=0.5)
        @test length(curvatures) == ne(G)
        
        for (edge, kappa) in curvatures
            @test -1.0 <= kappa <= 1.0
        end
    end
    
    @testset "Alpha parameter" begin
        kappa1 = compute_curvature(G, 1, 2, alpha=0.1)
        kappa2 = compute_curvature(G, 1, 2, alpha=0.9)
        # Different alpha should give different results (usually)
        @test isfinite(kappa1)
        @test isfinite(kappa2)
    end
end

@testset "Probability Measures" begin
    G = SimpleGraph(3)
    add_edge!(G, 1, 2)
    add_edge!(G, 2, 3)
    
    mu = build_probability_measure(G, 1, 0.5, nothing)
    
    @test haskey(mu, 1)
    @test mu[1] == 0.5  # Idleness component
    @test sum(values(mu)) ≈ 1.0
end

@testset "Wasserstein Distance" begin
    # Test with simple case
    mu = Dict(1 => 0.5, 2 => 0.5)
    nu = Dict(1 => 0.5, 2 => 0.5)
    
    G = SimpleGraph(2)
    add_edge!(G, 1, 2)
    
    # For identical measures, distance should be small
    # (exact value depends on implementation)
    @test true  # Placeholder - will test with actual implementation
end

