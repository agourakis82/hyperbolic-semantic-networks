"""
Property-based tests.

Tests mathematical properties and invariants.
"""

using Test
using LightGraphs
using Statistics
using HyperbolicSemanticNetworks

@testset "Property Tests" begin
    @testset "Curvature Bounds" begin
        # All curvature values should be in [-1, 1]
        for size in [10, 20, 50]
            G = SimpleGraph(size)
            # Create various graph structures
            for i in 1:(size-1)
                add_edge!(G, i, i+1)
            end
            if size >= 3
                add_edge!(G, 1, 3)  # Triangle
            end
            
            curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
            
            for kappa in values(curvatures)
                @test -1.0 <= kappa <= 1.0 "Curvature out of bounds: $kappa"
            end
        end
    end
    
    @testset "Clustering Coefficient Bounds" begin
        # Clustering should be in [0, 1]
        for size in [10, 20]
            G = SimpleGraph(size)
            for i in 1:(size-1)
                add_edge!(G, i, i+1)
            end
            
            metrics = network_metrics(G)
            @test 0.0 <= metrics.clustering <= 1.0
        end
    end
    
    @testset "Degree Preservation - Configuration Model" begin
        # Configuration model should preserve total degree
        G = SimpleGraph(10)
        for i in 1:9
            add_edge!(G, i, i+1)
        end
        
        original_degrees = [degree(G, v) for v in vertices(G)]
        total_degree = sum(original_degrees)
        
        nulls = generate_null_models(G, method=:configuration, n_samples=20)
        
        for null in nulls
            null_degrees = [degree(null, v) for v in vertices(null)]
            @test sum(null_degrees) == total_degree "Degree not preserved"
        end
    end
    
    @testset "Bootstrap Confidence Intervals" begin
        # CI lower should be <= mean <= CI upper
        G = SimpleGraph(30)
        for i in 1:29
            add_edge!(G, i, i+1)
        end
        
        function edge_count(g::SimpleGraph)::Float64
            return Float64(ne(g))
        end
        
        result = bootstrap_analysis(G, edge_count, n_samples=100, sample_size=0.8)
        
        @test result.ci_lower <= result.mean <= result.ci_upper
        @test result.std >= 0.0
    end
    
    @testset "Ricci Flow Convergence" begin
        # Ricci flow should either converge or reach max iterations
        G = SimpleGraph(15)
        for i in 1:14
            add_edge!(G, i, i+1)
        end
        
        result = ricci_flow(G, max_iterations=10, alpha=0.5)
        
        @test 0 <= result.iterations <= 10
        @test length(result.trajectory) > 0
        
        # Trajectory should be monotonic in some sense (simplified check)
        if length(result.trajectory) > 1
            @test result.trajectory[1]["iteration"] < result.trajectory[end]["iteration"]
        end
    end
    
    @testset "Probability Measures Sum to 1" begin
        # Internal check: probability measures should sum to 1
        G = SimpleGraph(10)
        for i in 1:9
            add_edge!(G, i, i+1)
        end
        
        # This is an internal property, but we can test indirectly
        # by checking curvature computation completes
        curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
        @test length(curvatures) == ne(G)
        
        # All curvatures should be finite (if probability measures are valid)
        for kappa in values(curvatures)
            @test isfinite(kappa)
        end
    end
end

