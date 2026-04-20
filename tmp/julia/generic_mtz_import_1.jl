function solve_mtz(c; time_limit=300.0, use_eq2=false)
    n = size(c,1)
    model = Model(Cbc.Optimizer)

    set_optimizer_attribute(model, "seconds", time_limit)

    @variable(model, x[1:n,1:n], Bin)
    @variable(model, y[1:n])

    @objective(model, Min, 
        sum(c[i,j]*x[i,j] for i in 1:n, j in 1:n))

    @constraint(model, [i=1:n], 
        sum(x[i,j] for j in 1:n if j != i) == 1)
    @constraint(model, [j=1:n], 
        sum(x[i,j] for i in 1:n if i != j) == 1)


    @constraint(model, [i=1:n], x[i,i] == 0)
