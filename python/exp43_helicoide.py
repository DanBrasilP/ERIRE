from mpmath import mp, sin, cos, sqrt, fsum
import numpy as np

# Configurações
mp.dps = 25  # precisão estendida
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
            self.a*other.a - self.b*other.b - self.c*other.c - self.d*other.d,
            self.a*other.b + self.b*other.a + self.c*other.d - self.d*other.c,
            self.a*other.c - self.b*other.d + self.c*other.a + self.d*other.b,
            self.a*other.d + self.b*other.c - self.c*other.b + self.d*other.a
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

# Projeção quaternária helicoidal
def modo_quaternion(n):
    return Quaternion(0, n * OMEGA, 0, 0).exp()

# Projeção conjugada: hélice quaternária + geometria toroidal
def modo_totalidade_conjugado(n, R=1.0, r=0.3):
    q_plus = modo_quaternion(n)
    q_minus = Quaternion(0, -n * OMEGA, 0, 0).exp()

    # Coordenadas toroidais
    theta = OMEGA * n
    phi = (OMEGA / 2) * n
    x = (R + r * cos(phi)) * cos(theta)
    y = (R + r * cos(phi)) * sin(theta)
    z = r * sin(phi)

    energia_espaco = sqrt(x**2 + y**2 + z**2)
    energia_quat = sqrt(q_plus.norm()**2 + q_minus.norm()**2)

    return energia_espaco * energia_quat

def eh_modo_fundamental_totalidade(n, calculados):
    energia_n = modo_totalidade_conjugado(n)
    for a in calculados:
        if a < n and n % a == 0:
            b = n // a
            energia_ab = modo_totalidade_conjugado(a) * modo_totalidade_conjugado(b)
            if abs(energia_ab - energia_n) < EPSILON:
                return False
    return True

# Geração da amostragem logarítmica
def gerar_amostragem_log(min_exp, max_exp, base=2):
    return sorted(set([int(mp.floor(base ** x)) for x in np.linspace(min_exp, max_exp, 30)]))

amostragem_logaritmica = gerar_amostragem_log(4, 12.3)

# Teste sobre a amostragem
modos_fundamentais_totalidade = []
for n in amostragem_logaritmica:
    if n >= 2 and eh_modo_fundamental_totalidade(n, modos_fundamentais_totalidade):
        modos_fundamentais_totalidade.append(n)

print("Modos fundamentais coerenciais no plano da totalidade:")
print(modos_fundamentais_totalidade)

# Vamos agora explorar uma visualização integrada da coerência vetorial nos domínios esférico, toroidal e helicoidal.
# Isso visa representar a ideia ontológica por trás da resolução conjunta (Poincaré, Hodge e estrutura geral da ERIЯƎ).

import matplotlib.pyplot as plt
import numpy as np

# Coordenadas polares para o domínio esférico (coerência máxima)
theta = np.linspace(0, 2 * np.pi, 500)
r_esfera = np.ones_like(theta)

# Coordenadas para o domínio toroidal (rotação pura)
r_toro = 1 + 0.3 * np.sin(5 * theta)

# Coordenadas para domínio helicoidal projetado
z = np.linspace(-2, 2, 500)
x_helicoide = np.cos(3 * z) * (1 + 0.2 * np.sin(5 * z))
y_helicoide = np.sin(3 * z) * (1 + 0.2 * np.sin(5 * z))

# Plot 1: Domínio esférico (coerência plena)
plt.figure(figsize=(6, 6))
plt.polar(theta, r_esfera, label="S³ – Domínio α (Esfera)", linewidth=2)
plt.title("Domínio de Coerência Máxima (Esfera)")
plt.legend()
plt.grid(True)
plt.show()

# Plot 2: Domínio toroidal (fluxo rotacional)
plt.figure(figsize=(6, 6))
plt.polar(theta, r_toro, label="*∞ – Domínio Toroidal", linewidth=2)
plt.title("Domínio de Fluxo Infinito (Toro)")
plt.legend()
plt.grid(True)
plt.show()

# Plot 3: Domínio helicoidal projetado (manifestação ressonante)
plt.figure(figsize=(6, 6))
plt.plot(x_helicoide, y_helicoide, label="τ – Domínio Helicoidal", linewidth=2)
plt.title("Plano de Projeção Coerencial (Helicoide)")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()
