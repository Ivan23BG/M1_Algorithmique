using JuMP, Cbc, DelimitedFiles, DataFrames, CSV

include("generic_mtz.jl")
include("generic_sf.jl")

# Chargement ATT48
c = readdlm("att48_d.txt")
n = size(c,1)

optimum = 33523

time_limits = [60.0, 300.0, 600.0]

methods = [
    ("MTZ", false),
    ("MTZ+eq2", true),
    ("SF", false),
    ("SF+eq2", true)
]

results = DataFrame(
    method=String[],
    time_limit=Float64[],
    value=Float64[],
    gap=Float64[]
)

for (method_name, use_eq2) in methods
    for T in time_limits

        if occursin("MTZ", method_name)
            res = solve_mtz(c, time_limit=T, use_eq2=use_eq2)
        else
            res = solve_sf(c, time_limit=T, use_eq2=use_eq2)
        end

        val = res.value
        gap = isnan(val) ? NaN : (val - optimum)/optimum

        push!(results, (method_name, T, val, gap))

        println("Done: $method_name with T=$T → value=$val")
    end
end

CSV.write("att48_results.csv", results)