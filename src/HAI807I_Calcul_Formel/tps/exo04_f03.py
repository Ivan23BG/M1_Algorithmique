def normalise(L, R):
    L = list(L)
    while len(L) > 0 and L[-1] == R(0):
        L.pop()
    return L