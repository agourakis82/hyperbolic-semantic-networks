"""
Main test runner for HyperbolicSemanticNetworks.jl

Run with: julia --project=. test/runtests.jl
"""

# Environment setup.
# Under `Pkg.test()`, the sandbox already contains the package and the
# test/Project.toml deps — and `Pkg` itself is not in the load path there,
# so `using Pkg` throws. Re-activating @__DIR__ in that sandbox would also
# DROP the parent package from the environment. Only activate the test
# project when the package is not already resolvable (direct runs).
try
    using Pkg
    if Base.find_package("HyperbolicSemanticNetworks") === nothing
        Pkg.activate(@__DIR__)
        push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
    end
catch
    # Pkg unavailable (Pkg.test sandbox): environment is already correct.
    push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
end

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

