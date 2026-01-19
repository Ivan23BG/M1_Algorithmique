function add_cover_cuts!(model, x, y, weights, c; max_subset_size=4)
    n = length(weights)
    m = length(y)
    for k in 2:max_subset_size
        for C in combinations(1:n, k)
            if sum(weights[i] for i in C) > c
                for j in 1:m
                    @constraint(model, sum(x[i,j] for i in C) <= 
                    (length(C)-1)*y[j])
                end
            end
        end
    end
end
