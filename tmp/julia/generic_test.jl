using JuMP, Cbc
using DelimitedFiles
using DataFrames, CSV

include("generic_mtz.jl")
include("generic_sf.jl")

instances = [
    ("FIVE", "five_d.txt"),
    ("GR17", "gr17_d.txt"),
    ("FRI26", "fri26_d.txt"),
    ("DANTZIG42", "dantzig42_d.txt")
]

results = DataFrame(
    instance=String[],
    n=Int[],
    method=String[],
    value=Float64[],
    time=Float64[],
    status=String[]
)

for (name, file) in instances
    c = readdlm(file)
    n = size(c,1)

    # MTZ
    res = solve_mtz(c, use_eq2=false)
    push!(results, (name, n, "MTZ", res.value, res.time, string(res.status)))

    res = solve_mtz(c, use_eq2=true)
    push!(results, (name, n, "MTZ+eq2", res.value, res.time, string(res.status)))

    # SF
    res = solve_sf(c, use_eq2=false)
    push!(results, (name, n, "SF", res.value, res.time, string(res.status)))

    res = solve_sf(c, use_eq2=true)
    push!(results, (name, n, "SF+eq2", res.value, res.time, string(res.status)))
end

CSV.write("tsp_results.csv", results)