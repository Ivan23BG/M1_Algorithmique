using JuMP, Cbc

# a = vector of entry-to-storage pallet counts
# b = vector of storage-to-exit pallet counts
# t = m x n matrix of travel times
function solve_conveyor_assignment(a, b, t)
    m = length(a)
    n = length(b)
    model = Model(Cbc.Optimizer)
    set_silent(model)  # avoid printing too much

    # Decision variables: x[i,j] = number of pallets assigned from entry i to exit j
    @variable(model, x[1:m, 1:n] >= 0, Int)

    # Each entry pallet count is satisfied
    @constraint(model, [i=1:m], sum(x[i,j] for j=1:n) == a[i])

    # Each exit pallet count is satisfied
    @constraint(model, [j=1:n], sum(x[i,j] for i=1:m) == b[j])

    # Objective: minimize total travel time
    @objective(model, Min, sum(t[i,j] * x[i,j] for i=1:m, j=1:n))

    optimize!(model)

    return model, value.(x), objective_value(model)
end

# exemple
a = [2, 3]         # 2 pallets for storage 1, 3 pallets for storage 2
b = [1, 4]         # 1 pallet to exit 1, 4 pallets to exit 2
t = [3 5;          # travel times from storage to exit
     2 1]

model, assignment, total_time = solve_conveyor_assignment(a, b, t)

println("Assignment matrix:")
println(assignment)
println("Total transport time: $total_time")
