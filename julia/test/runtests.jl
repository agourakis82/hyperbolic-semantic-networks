"""
Main test runner for HyperbolicSemanticNetworks.jl

Run with: julia --project=. test/runtests.jl
"""

using Pkg
Pkg.activate(@__DIR__)

# Add parent directory to path
push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))

using Test

# Run all test suites
println("=" ^ 80)
println("Running HyperbolicSemanticNetworks Test Suite")
println("=" ^ 80)
println()

@testset "HyperbolicSemanticNetworks" begin
    include("test_preprocessing.jl")
    include("test_curvature.jl")
    include("test_analysis.jl")
    include("test_integration.jl")
    include("test_regression.jl")
    include("test_properties.jl")
    # Performance tests are optional (require BenchmarkTools)
    try
        using BenchmarkTools
        include("test_performance.jl")
    catch
        @warn "BenchmarkTools not available, skipping performance tests"
    end
end

println()
println("=" ^ 80)
println("All tests completed!")
println("=" ^ 80)

