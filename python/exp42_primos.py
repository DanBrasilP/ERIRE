from mpmath import mp, sin, cos, sqrt, fsum

# Configuração de precisão
mp.dps = 25
OMEGA = 2 * mp.pi / 10
EPSILON = mp.mpf("1e-6")

# Classe Quaternion
class Quaternion:
    def __init__(self, a, b, c, d):
        self.a = mp.mpf(a)
        self.b = mp.mpf(b)
        self.c = mp.mpf(c)
        self.d = mp.mpf(d)

    def __mul__(self, other):
        return Quaternion(
            self.a * other.a - self.b * other.b - self.c * other.c - self.d * other.d,
            self.a * other.b + self.b * other.a + self.c * other.d - self.d * other.c,
            self.a * other.c - self.b * other.d + self.c * other.a + self.d * other.b,
            self.a * other.d + self.b * other.c - self.c * other.b + self.d * other.a
        )

    def exp(self):
        v_norm = sqrt(self.b**2 + self.c**2 + self.d**2)
        scalar_part = mp.exp(self.a) * cos(v_norm)
        if v_norm == 0:
            return Quaternion(scalar_part, 0, 0, 0)
        coeff = mp.exp(self.a) * sin(v_norm) / v_norm
        return Quaternion(
            scalar_part,
            coeff * self.b,
            coeff * self.c,
            coeff * self.d
        )

    def norm(self):
        return sqrt(self.a**2 + self.b**2 + self.c**2 + self.d**2)

# Funções do modelo
def modo_acoplado_completo(n):
    q_plus = Quaternion(0, n * OMEGA, 0, 0).exp()
    q_minus = Quaternion(0, -n * OMEGA, 0, 0).exp()
    return q_plus, q_minus

def energia_modo(q1, q2):
    return fsum([
        q1.a**2 + q1.b**2 + q1.c**2 + q1.d**2,
        q2.a**2 + q2.b**2 + q2.c**2 + q2.d**2
    ])

def modo_ressonante_acoplado_quat(n):
    q_plus, q_minus = modo_acoplado_completo(n)
    return sqrt(energia_modo(q_plus, q_minus))

def eh_modo_fundamental_acoplado_completo(n, calculados):
    energia_n = modo_ressonante_acoplado_quat(n)
    for a in calculados:
        if a < n and n % a == 0:
            b = n // a
            q1a, q2a = modo_acoplado_completo(a)
            q1b, q2b = modo_acoplado_completo(b)
            q1ab = q1a * q1b
            q2ab = q2a * q2b
            energia_ab = sqrt(energia_modo(q1ab, q2ab))
            rel_error = abs(energia_ab - energia_n) / energia_n if energia_n != 0 else float('inf')
            if rel_error < EPSILON:
                return False
    return True

# Execução principal com exibição
modos_fundamentais_quat_completo = []

print("\n--- Modos Fundamentais Coerenciais (Modelo Quaternário - Hélice Dupla) ---")
for n in range(2, 101):
    if eh_modo_fundamental_acoplado_completo(n, modos_fundamentais_quat_completo):
        energia = modo_ressonante_acoplado_quat(n)
        modos_fundamentais_quat_completo.append(n)
        print(f"n = {n:3d} | Energia coerencial = {float(energia):.15f}")

print(f"\nTotal de modos fundamentais encontrados: {len(modos_fundamentais_quat_completo)}")
print("Lista final:")
print(modos_fundamentais_quat_completo)

print("\nImplementação simplificada concluída com sucesso, com precisão para `n ∈ [2, 100].")
print("Critério de primalidade estrutural baseado em acoplamento quaternário rotacional aplicado.")
