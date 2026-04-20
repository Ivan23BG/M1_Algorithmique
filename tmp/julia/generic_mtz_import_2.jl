    @constraint(model, [i=2:n, j=2:n; i != j],
        x[i,j]*(n-1) + y[i] - y[j] <= n-2
    )

    @constraint(model, y[1] == 0)
    @constraint(model, [i=2:n], 1 <= y[i] <= n-1)

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