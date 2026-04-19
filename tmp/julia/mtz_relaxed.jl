using JuMP, Cbc, DelimitedFiles

c = readdlm("dantzig42_d.txt")
n = size(c, 1)

model = Model(Cbc.Optimizer)

set_optimizer_attribute(model, "seconds", 120)

@variable(model, x[1:n,1:n], Bin)
@variable(model, y[1:n])

@objective(model, Min, sum(c[i,j]*x[i,j] for i in 1:n, j in 1:n))

# degrés
@constraint(model, [i=1:n], sum(x[i,j] for j in 1:n if j != i) == 1)
@constraint(model, [j=1:n], sum(x[i,j] for i in 1:n if i != j) == 1)

# pas de boucles
@constraint(model, [i=1:n], x[i,i] == 0)

# 🔥 MTZ CORRECT
@constraint(model, [i=2:n, j=2:n; i != j],
    x[i,j]*(n-1) + y[i] - y[j] <= n-2
)

# ordre
@constraint(model, y[1] == 0)
@constraint(model, [i=2:n], 1 <= y[i] <= n-1)

optimize!(model)

println("MTZ value = ", objective_value(model))
println("Status = ", termination_status(model))
println("Time = ", solve_time(model))