def poly_mult(A, B, R):
    res = [R(0)] * (len(A) + len(B) - 1)
    for i in range(len(A)):
        for j in range(len(B)):
            res[i + j] += A[i] * B[j]
    res = normalise(res, R)
    return res
