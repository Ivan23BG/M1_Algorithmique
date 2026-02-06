def poly_add(A, B, R):
    n = max(len(A), len(B))
    res = [R(0)] * n
    for i in range(n):
        a = A[i] if i < len(A) else 0
        b = B[i] if i < len(B) else 0
        res[i] += a + b
    res = remove_zeroes(res, R)
    return res