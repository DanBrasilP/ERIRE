from mpmath import mp, mpf, log

mp.dps = 150

def omega_esferico(n):
    return 2 * mp.pi / n

def k_toroidal(n):
    if n <= 2:
        return mpf(1)
    return n / log(n)

def pi_equilibrio(n):
    omega_e = omega_esferico(n)
    k_t = k_toroidal(n)
    C = log(n)  # fator coerencial que anula log(n) no denominador final
    return (C * k_t * omega_e) / 2

valores_n = [1000, 3000, 5000, 7000, 10000, 20000]

print("Aproximações de π com fator de equilíbrio coerencial (C = log(n)):\n")
for n in valores_n:
    pi_aproximado = pi_equilibrio(n)
    erro = mp.fabs(mp.pi - pi_aproximado)
    print(f"n = {n}")
    print(f"π aproximado = {pi_aproximado}")
    print(f"Erro absoluto = {erro}\n")
