# using Pkg
# Pkg.add("JuMP")
# Pkg.add("Cbc")
# Pkg.add("Printf")
# Pkg.add("DataFrames")
# Pkg.add("CSV")
# Pkg.add("Dates")

using JuMP
using Cbc
using Printf
using DataFrames
using CSV
using Dates


function build_klee_minty_model(n)
    model = Model(Cbc.Optimizer)
    set_silent(model)  # no terminal printing

    @variable(model, x[1:n] >= 0)

    # Constraints:
    for i in 1:n
        if i == 1
            @constraint(model, x[1] <= 1)
        else
            @constraint(model, 2*sum(10^(i-j)*x[j] for j in 1:i-1) + x[i] 
            <= 100^(i-1))
        end
    end

    # Objective:
    @objective(model, Max, sum(10^(n-j) * x[j] for j in 1:n))

    return model, x
end


function solve_klee_minty(n)
    model, x = build_klee_minty_model(n)
    start_time = now()
    optimize!(model)
    end_time = now()
    elapsed = end_time - start_time

    # Retrieve solution
    x_val = value.(x)
    obj_val = objective_value(model)
    return x_val, obj_val, elapsed
end


function run_tests(ns; max_time_sec=60)
    results = DataFrame(n=Int[], obj=Float64[], time_sec=Float64[])

    for n in ns
        println("Solving n = $n ...")
        try
            x_val, obj_val, elapsed = solve_klee_minty(n)
            elapsed_sec = Dates.value(elapsed)/1e9
            if elapsed_sec > max_time_sec
                println("  Exceeded max time of $max_time_sec seconds, 
                skipping further large n")
                break
            end
            push!(results, (n, obj_val, elapsed_sec))
            println(@sprintf("  Obj = %.4f, Time = %.3f sec", 
            obj_val, elapsed_sec))
        catch e
            println("  Error solving n=$n: $e")
        end
    end
    return results
end


# Test sizes
ns = [5, 10, 15, 20]#, 30, 50, 100, 150, 200, 250]
results = run_tests(ns)
CSV.write("klee_minty_results.csv", results)

println("\nAll results saved to klee_minty_results.csv")
println(results)
