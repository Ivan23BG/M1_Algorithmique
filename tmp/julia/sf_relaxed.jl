using JuMP, Cbc, DelimitedFiles

c = readdlm("dantzig42_d.txt")
n = size(c, 1)

model = Model(Cbc.Optimizer)

set_optimizer_attribute(model, "seconds", 120)

@variable(model, 0 <= x[1:n,1:n] <= 1, Bin)
@variable(model, 0 <= q[1:n,1:n] <= n-1)

@objective(model, Min, sum(c[i,j]*x[i,j] for i in 1:n, j in 1:n))

# degrés
@constraint(model, [i=1:n], sum(x[i,j] for j in 1:n if j != i) == 1)
@constraint(model, [j=1:n], sum(x[i,j] for i in 1:n if i != j) == 1)

# pas de boucles
@constraint(model, [i=1:n], x[i,i] == 0)
@constraint(model, [i=1:n], q[i,i] == 0)

# lien flux
@constraint(model, [i=1:n, j=1:n; i != j],
    q[i,j] <= (n-1)*x[i,j]
)

# source
@constraint(model, sum(q[1,j] for j in 2:n) == n-1)

# conservation
@constraint(model, [j=2:n],
    sum(q[i,j] for i in 1:n if i != j)
    - sum(q[j,k] for k in 1:n if k != j) == 1
)

# inegalite 2
@constraint(model, [i=1:n, j=i+1:n],
    x[i,j] + x[j,i] <= 1
)

optimize!(model)

println("SF value = ", objective_value(model))
println("Status = ", termination_status(model))
println("Time = ", solve_time(model))