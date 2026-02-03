R = GF(5)

a = (1, 2, 3)
b = (2, 1)

# on trouve la premiere puissance de 2 au dessus
n = 1 << (max(len(a), len(b)) - 1).bit_length()

# et on rajoute des zeros jusqu'a l'atteindre
a_two_pow = list(a) + [R(0)] * (n - len(a))
b_two_pow = list(b) + [R(0)] * (n - len(b))

karatsuba_list(a_two_pow, b_two_pow, R)
