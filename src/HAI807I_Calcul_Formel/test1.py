from sage.all import *

def add_polynomials(f, g):
    """Given f and g two lists representing the coefficients of their respective polynomials,
    calculates the polynomial f + g"""
    
    n_f, n_g = len(f), len(g)
    output = [0] * max(n_f, n_g)
    # Add f
    for i in range(n_f):
        output[i] += f[i]
    # Add g
    for i in range(n_g):
        output[i] += g[i]
    # Normalise by removing overflow zeroes
    n = max(n_f, n_g)
    while output[n - 1] == 0:
        n -= 1
        if n == -1:
            return [0]

    return output[:n]

def multiply_polynomials(f, g):
    """Given f and g two lists representing the coefficients of their respective polynomials,
    calculates the polynomial f * g"""
    
    n_f, n_g = len(f), len(g)
    if n_f > n_g:
        f, g = g, f
        n_f, n_g = n_g, n_f
    output = [0] * (n_f + n_g - 1)
    for i in range(n_f):
        output[i] += f[i] * g[0]
    for i in range(n_f, n_f + n_g - 1):
        output[i] += f[i - n_f + 1] * g[n_g - 1]

    output[n_f - 1] += f[0] * g[n_g - 1]

    for i in range(0, n_f):
        for j in range(1, n_g - 1):
            output[i + j] += f[i] * g[j]
    
    return output
    

f = [2, 2, -8]
g = [1/2, 7, 8]

h = add_polynomials(f, g)
# h = multiply_polynomials(f, g)
print(h)
