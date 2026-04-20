    @constraint(model, [i=1:n, j=1:n; i != j],
        q[i,j] <= (n-1)*x[i,j]
    )

    @constraint(model, sum(q[1,j] for j in 2:n) == n-1)

    @constraint(model, [j=2:n], sum(q[i,j] for i in 1:n if i != j)
        - sum(q[j,k] for k in 1:n if k != j) == 1
    )

    if use_eq2
        @constraint(model, [i=1:n, j=i+1:n], x[i,j] + x[j,i] <= 1)
    end
    optimize!(model)
    return (
        value = has_values(model) ? objective_value(model) : NaN,
        time = solve_time(model), status = termination_status(model)
    )
end