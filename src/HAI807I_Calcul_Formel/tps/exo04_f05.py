rings = [GF(17), ZZ, Integers(100)]
degrees = [10, 100, 1000]

for R in rings:
    # tests degres identiques
    for d in degrees:
        test_operations(R, d, d)
    # tests degres differents
    for i in range(3):
        for j in range(i + 1, 3):
            test_operations(R, degrees[i], degrees[j])