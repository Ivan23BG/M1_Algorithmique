println("Objective is: ", objective_value(m))
println("Solve time = ", solve_time(m))
println("Solution is:")
for i = 1:5
    print("x[$i] = ", value(x[i]))
    println(", p[$i]/w[$i] = ", profit[i]/weight[i])
end