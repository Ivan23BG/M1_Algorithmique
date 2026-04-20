using JuMP, Cbc, DelimitedFiles, DataFrames, CSV

function solve_mtz(c; time_limit=300.0, use_eq2=false)
    n = size(c,1)
    model = Model(Cbc.Optimizer)

    set_optimizer_attribute(model, "seconds", time_limit)

    @variable(model, x[1:n,1:n], Bin)
    @variable(model, y[1:n])

    @objective(model, Min, sum(c[i,j]*x[i,j] for i in 1:n, j in 1:n))

    # degrés
    @constraint(model, [i=1:n], sum(x[i,j] for j in 1:n if j != i) == 1)
    @constraint(model, [j=1:n], sum(x[i,j] for i in 1:n if i != j) == 1)

    # pas de boucles
    @constraint(model, [i=1:n], x[i,i] == 0)

    # MTZ (sans le noeud 1)
    @constraint(model, [i=2:n, j=2:n; i != j],
        x[i,j]*(n-1) + y[i] - y[j] <= n-2
    )

    @constraint(model, y[1] == 0)
    @constraint(model, [i=2:n], 1 <= y[i] <= n-1)

    # eq2 optionnelle
    if use_eq2
        @constraint(model, [i=1:n, j=i+1:n], x[i,j] + x[j,i] <= 1)
    end

    optimize!(model)

    return (
        value = has_values(model) ? objective_value(model) : NaN,
        time = solve_time(model),
        status = termination_status(model)
    )
end