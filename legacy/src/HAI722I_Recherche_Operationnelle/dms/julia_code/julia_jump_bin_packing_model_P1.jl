function solve_P1(n, c, weights; m=n)
    model = Model(Cbc.Optimizer)

    @variable(model, x[1:n, 1:m], Bin)
    @variable(model, y[1:m], Bin)

    @objective(model, Min, sum(y[j] for j in 1:m))

    # Each item exactly in one bin
    @constraint(model, [i=1:n], sum(x[i, j] for j=1:m) == 1)

    # bin capacities
    @constraint(model, [j=1:m], sum(weights[i] * x[i,j] for i=1:n) <= c)

    @constraint(model, [i=1:n, j=1:m], x[i,j] <= y[j])

    optimize!(model)

    return model
end
