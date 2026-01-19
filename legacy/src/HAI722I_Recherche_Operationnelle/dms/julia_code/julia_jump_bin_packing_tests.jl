# Install required packages
using Pkg
# Pkg.add("JuMP")
# Pkg.add("Cbc")
# Pkg.add("Glob")
# Pkg.add("CSV")
# Pkg.add("DataFrames")
# Pkg.add("Printf")

# Load required packages
using JuMP
using Cbc
using Glob
using CSV, DataFrames, Printf


function build_P1(n, c, weights; m=n)
    model = Model(Cbc.Optimizer)
    # Stop printing in terminal
    # set_silent(model)

    @variable(model, x[1:n, 1:m], Bin)
    @variable(model, y[1:m], Bin)

    @objective(model, Min, sum(y[j] for j in 1:m))

    # Each item exactly in one bin
    @constraint(model, [i=1:n], sum(x[i, j] for j=1:m) == 1)

    # bin capacities
    @constraint(model, [j=1:m], sum(weights[i] * x[i,j] for i=1:n) <= c)

    @constraint(model, [i=1:n, j=1:m], x[i,j] <= y[j])

    return model
end

function build_P2(n, c, weights; m=n)
    model = Model(Cbc.Optimizer)
    # Stop printing in terminal
    # set_silent(model)

    @variable(model, x[1:n, 1:m], Bin)
    @variable(model, y[1:m], Bin)

    @objective(model, Min, sum(y[j] for j in 1:m))

    # Each item exactly in one bin
    @constraint(model, [i=1:n], sum(x[i, j] for j=1:m) == 1)

    # bin capacities
    @constraint(model, [j=1:m], sum(weights[i] * x[i,j] for i=1:n) <= c * y[j])

    return model
end

function read_bpplib_instance(path)
    data = readlines(path)
    # First line contains n
    n = parse(Int, data[1])
    # Second line contains capacity
    c = parse(Int, data[2])

    # Collect all remaining numbers, on the n following lines
    weights = []
    for line in data[3:end]
        append!(weights, parse.(Int, split(line)))
    end

    if length(weights) != n
        error("Error: expected $n weights but got $(length(weights))")
    end

    return n, c, weights
end

function lp_relax_value(model)
    relax_integrality(model)
    optimize!(model)
    return objective_value(model)
end

function solve_relaxations_for_instances(instance_paths)
    results = Dict()

    for path in instance_paths
        n, c, weights = read_bpplib_instance(path)

        model_P1 = build_P1(n, c, weights)
        model_P2 = build_P2(n, c, weights)

        optimize!(model_P1)
        optimize!(model_P2)

        results[path] = (objective_value(model_P1), objective_value(model_P2))
    end

    return results
end


function generate_falkenauer_paths(base_dir="../instances/Falkenauer")
    T_sizes = [60, 120, 249, 501]
    U_sizes = [120, 250, 500, 1000]

    paths = String[]

    # T instances
    for s in T_sizes
        for i in 0:19
            filename = @sprintf("Falkenauer_t%d_%02d.txt", s, i)
            push!(paths, joinpath(base_dir, filename))
        end
    end

    # U instances
    for s in U_sizes
        for i in 0:19
            filename = @sprintf("Falkenauer_u%d_%02d.txt", s, i)
            push!(paths, joinpath(base_dir, filename))
        end
    end

    return paths
end

function generate_scholl_paths(base_dir="../instances/Scholl")
    return glob("*.txt", base_dir)
end

function generate_small_falkenauer_set(base_dir="../instances/Falkenauer")
    sizes = [60]
    paths = String[]

    for s in sizes
        for i in 0:2
            filename_t = @sprintf("Falkenauer_t%d_%02d.txt", s, i)
            # filename_u = @sprintf("Falkenauer_u%d_%02d.txt", s, i)
            push!(paths, joinpath(base_dir, filename_t))
            # push!(paths, joinpath(base_dir, filename_u))
        end
    end

    return paths
end

function generate_small_scholl_set(base_dir="../instances/Scholl")
    paths = String[]
    filename_1 = @sprintf("N1C1W1_A")
    filename_2 = @sprintf("N1C1W1_B")
    push!(paths, joinpath(base_dir, filename_1))
    push!(paths, joinpath(base_dir, filename_2))

    return paths
end

function get_all_instance_paths()
    # falk_paths = generate_falkenauer_paths()
    # scholl_paths = generate_scholl_paths()
    falk_paths = generate_small_falkenauer_set()
    scholl_paths = generate_small_scholl_set()
    return vcat(falk_paths, scholl_paths)
end

function save_results(results, filename="lp_relax_results.csv")
    df = DataFrame(Path = String[], LP_P1 = Float64[], LP_P2 = Float64[])

    for (path, (lp1, lp2)) in results
        push!(df, (path, lp1, lp2))
    end

    CSV.write(filename, df)
end


# Main execution
all_paths = get_all_instance_paths()

results = solve_relaxations_for_instances(all_paths)

save_results(results)


# instance_paths = ["path/to/instance1.txt", "path/to/instance2.txt"]
# results = solve_relaxations_for_instances(instance_paths)
