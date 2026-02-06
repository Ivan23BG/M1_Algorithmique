def list_to_poly(L, R):
    # cree le polynome associe a une liste
    x = R['x'].gen()
    return sum(L[i] * x^i for i in range(len(L)))

def random_poly_list(deg, R):
    return [R.random_element() for _ in range(deg + 1)]

def test_operations(R, deg1, deg2):
    A = random_poly_list(deg1, R)
    B = random_poly_list(deg2, R)

    PR = PolynomialRing(R, 'x')

    PA = list_to_poly(A, PR)
    PB = list_to_poly(B, PR)

    C_add = poly_add(A, B, R)
    C_mul = poly_mult(A, B, R)

    try:
        assert list_to_poly(C_add, PR) == PA + PB
        assert list_to_poly(C_mul, PR) == PA * PB
    except AssertionError:
        print(f"Erreur pour degres {deg1} et {deg2} sur {R}")
        print(f"A = {PA}, B = {PB}")
        print(f"A + B = {PA + PB}, calcule: {list_to_poly(C_add, PR)}")
        print(f"A * B = {PA * PB}, calcule: {list_to_poly(C_mul, PR)}")
        raise

    print(f"Test reussi pour degres {deg1} et {deg2} sur {R}")