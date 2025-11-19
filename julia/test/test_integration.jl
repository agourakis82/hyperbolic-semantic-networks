"""
Integration tests for full pipeline.

Tests complete workflows from data loading to analysis.
"""

using Test
using LightGraphs
using HyperbolicSemanticNetworks

@testset "Full Pipeline Integration" begin
    @testset "Load → Curvature → Analysis" begin
        # Create synthetic test data
        test_file = tempname() * ".csv"
        
        open(test_file, "w") do f
            println(f, "source,target,weight")
            for i in 1:10
                for j in (i+1):min(i+3, 10)
                    println(f, "word$i,word$j,0.5")
                end
            end
        end
        
        try
            # Load data
            result = load_swow(test_file, language="test", min_weight=0.0)
            G = result.graph
            
            @test nv(G) > 0
            @test ne(G) > 0
            
            # Compute curvature
            curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
            @test length(curvatures) == ne(G)
            
            # Compute metrics
            metrics = network_metrics(G)
            @test metrics.n_nodes == nv(G)
            @test metrics.n_edges == ne(G)
            
            # Bootstrap analysis
            function mean_curvature_stat(g::SimpleGraph)::Float64
                c = compute_graph_curvature(g, alpha=0.5, parallel=false)
                return mean(collect(values(c)))
            end
            
            bootstrap_result = bootstrap_analysis(G, mean_curvature_stat, n_samples=50, sample_size=0.8)
            @test bootstrap_result.mean isa Float64
            @test isfinite(bootstrap_result.mean)
            
        finally
            rm(test_file, force=true)
        end
    end
    
    @testset "Null Model Comparison" begin
        # Create test graph
        G = SimpleGraph(10)
        for i in 1:9
            add_edge!(G, i, i+1)
        end
        
        # Compute real curvature
        real_curvatures = compute_graph_curvature(G, alpha=0.5, parallel=false)
        real_kappa = mean(collect(values(real_curvatures)))
        
        # Generate null models
        nulls = generate_null_models(G, method=:configuration, n_samples=20)
        
        # Compute null curvatures
        null_kappas = Float64[]
        for null in nulls
            null_c = compute_graph_curvature(null, alpha=0.5, parallel=false)
            push!(null_kappas, mean(collect(values(null_c))))
        end
        
        # Compare
        comparison = compare_with_nulls(real_kappa, null_kappas)
        
        @test comparison.real_value == real_kappa
        @test comparison.null_mean isa Float64
        @test 0.0 <= comparison.p_value <= 1.0
    end
end

