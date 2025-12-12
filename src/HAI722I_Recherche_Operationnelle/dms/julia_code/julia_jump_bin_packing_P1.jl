# Install required packages
using Pkg
Pkg.add("JuMP")
Pkg.add("Cbc")

# Load required packages
using JuMP
using Cbc

# Problem modeling for P1
# model to model
# Z = max 4x + 5y
# 2x+y <= 800
# x+2y <= 700
# y <= 300
# x,y >= 0
model = Model(Cbc.Optimizer)
@variable(model, x >= 0)
@variable(model, y >= 0)
@objective(model, Max, 4x + 5y)
@constraint(model, 2x + y <= 800)
@constraint(model, x + 2y <= 700)
@constraint(model, y <= 300)

optimize!(model)

# Print results
println("Objective is: ", objective_value(model))
println("Solve time = ", solve_time(model))
println("Solution is:")
println("x = ", value(x))
println("y = ", value(y))