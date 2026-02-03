def karatsuba_list(a, b, R):
    a = [R(x) for x in a]
    b = [R(x) for x in b]

    if not a or not b:
        return []

    # cas de base
    if len(a) == 1:
        return [a[0] * bi for bi in b]

    if len(b) == 1:
        return [b[0] * ai for ai in a]

    n = max(len(a), len(b))
    m = n // 2

    a += [R(0)] * (n - len(a))
    b += [R(0)] * (n - len(b))

    a0, a1 = a[:m], a[m:]
    b0, b1 = b[:m], b[m:]

    z0 = karatsuba_list(a0, b0, R)
    z2 = karatsuba_list(a1, b1, R)

    a0a1 = [a0[i] + a1[i] for i in range(len(a1))]
    b0b1 = [b0[i] + b1[i] for i in range(len(b1))]

    z1 = karatsuba_list(a0a1, b0b1, R)

    # on met tout a la meme taille
    L = max(len(z0), len(z1), len(z2))
    z0 += [R(0)] * (L - len(z0))
    z1 += [R(0)] * (L - len(z1))
    z2 += [R(0)] * (L - len(z2))

    for i in range(L):
        z1[i] -= z0[i] + z2[i]

    # fusion des resultats
    result = [R(0)] * (2 * n)

    for i, v in enumerate(z0):
        result[i] += v

    for i, v in enumerate(z1):
        result[i + m] += v

    for i, v in enumerate(z2):
        result[i + 2*m] += v

    # Trim trailing zeros
    while result and result[-1] == R(0):
        result.pop()

    return result
