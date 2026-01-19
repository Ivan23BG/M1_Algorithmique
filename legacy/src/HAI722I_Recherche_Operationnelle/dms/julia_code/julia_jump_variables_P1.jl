@variable(m, x) # No bounds
@variable(m, x >= lb) # Lower bound only (note: 'lb <= x' is not valid)
@variable(m, lb <= x <= ub) # Both lower and upper bounds
@variable(m, x == fixedval) # Fixed variable
@variable(m, x[1:M, 1:N]) # Un vecteur de variables
@variable(m, x[1:5], Bin) # Un vecteur de variabes binaires