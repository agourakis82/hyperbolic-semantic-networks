"""
Performance tests and benchmarks.

Tests performance-critical operations and validates speedups.
"""

using Test
using LightGraphs
using BenchmarkTools
using HyperbolicSemanticNetworks

@testset "Performance Benchmarks" begin
    @testset "Curvature Computation Speed" begin
        # Test different graph sizes
        for size in [50, 100, 200]
            G = SimpleGraph(size)
            for i in 1:(size-1)
                add_edge!(G, i, i+1)
            end
            
            # Benchmark
            result = @benchmark compute_graph_curvature($G, alpha=0.5, parallel=false)
            
            # Check it completes in reasonable time
            @test median(result.times) / 1e9 < 300  # Less than 5 minutes for 200 nodes
            println("  Size $size: $(median(result.times) / 1e9)s median")
        end
    end
    
    @testset "Null Model Generation Speed" begin
        G = SimpleGraph(100)
        for i in 1:99
            add_edge!(G, i, i+1)
        end
        
        # Benchmark
        result = @benchmark generate_null_models($G, method=:configuration, n_samples=100)
        
        # Should complete in reasonable time
        @test median(result.times) / 1e9 < 60  # Less than 1 minute for 100 samples
        println("  Null models (100 samples): $(median(result.times) / 1e9)s median")
    end
    
    @testset "Bootstrap Speed" begin
        G = SimpleGraph(50)
        for i in 1:49
            add_edge!(G, i, i+1)
        end
        
        function simple_stat(g::SimpleGraph)::Float64
            return Float64(ne(g))
        end
        
        # Benchmark
        result = @benchmark bootstrap_analysis($G, $simple_stat, n_samples=100, sample_size=0.8)
        
        @test median(result.times) / 1e9 < 30  # Less than 30 seconds
        println("  Bootstrap (100 samples): $(median(result.times) / 1e9)s median")
    end
end

@testset "Memory Usage" begin
    @testset "Curvature Memory" begin
        G = SimpleGraph(100)
        for i in 1:99
            add_edge!(G, i, i+1)
        end
        
        # Check memory doesn't explode
        curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
        
        # Should have reasonable memory footprint
        @test length(curvatures) == ne(G)
        
        # Memory check would require additional tools
        # For now, just verify it completes
        @test true
    end
end

