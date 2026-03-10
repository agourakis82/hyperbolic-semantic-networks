"""
BA Finite-Size Scaling: run run_ba_comparison for N=200, 500, 1000.

Usage:
    julia --project=julia -t8 julia/scripts/run_ba_scaling.jl           # all N
    julia --project=julia -t8 julia/scripts/run_ba_scaling.jl --N 500  # single N
"""

include("run_ba_comparison.jl")

function main()
    N_arg = nothing
    for (i, arg) in enumerate(ARGS)
        if arg == "--N" && i < length(ARGS)
            N_arg = parse(Int, ARGS[i+1])
        end
    end

    if N_arg !== nothing
        println("Running BA comparison for N=$N_arg")
        run_ba_comparison(N=N_arg)
    else
        for N in [200, 500, 1000]
            println("\n", "="^70)
            println("STARTING N=$N")
            println("="^70)
            run_ba_comparison(N=N)
        end
    end
end

main()
