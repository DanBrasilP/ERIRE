import numpy as np
import matplotlib.pyplot as plt
from ERIRE import ERIRE

# Constantes
q_e = 1.602176634e-19
lambda_R = 1.06e-10        # Comprimento rotacional
k_e = 8.987551787e9
a_0 = 5.29e-11              # Raio de Bohr
n_levels = 5

# Inicializa estados com defasagem (para coerência não trivial)
elétron = ERIRE(np.exp(1j * np.pi/4), symbolic=False)
próton  = ERIRE(np.exp(-1j * np.pi/3), symbolic=False)

# Bohr
def r_n_bohr(n): return n**2 * a_0
def E_bohr(n): return -13.6 / n**2

print("\n=== Caso 1 - Baixa Coerência - Comparação ERIЯƎ (com ERIRE) vs Bohr ===")
print(f"{'n':>2} {'r_ERIRE (nm_R)':>12} {'U_ERIRE (eV_R)':>14} {'r2_ERIRE (nm)':>12} {'U2_ERIRE (eV)':>14} {'r_Bohr (nm)':>12} {'E_Bohr (eV)':>12} {'|Z_total|':>10}")
print(f"{'':>2} {'Radial':>12} {'Radial':>14} {'Linear Dinamico':>12} {'Linear Dinamico':>14} {'Linear':>10} {'Linear':>12} {'':>10}")
print("-" * 75)

for n in range(1, n_levels + 1):
    r = n * (lambda_R / 2)                         # Raio ERIRE
    escala = a_0 / (lambda_R / 2)
    r2 = n**2 * (lambda_R / 2) * escala
    m = (2 * np.pi * r) / lambda_R                 # Parâmetro rotacional
    Ze = elétron.eire(elétron.z, m)
    Zp = próton.eire(próton.z, -m)
    Z = Ze * Zp
    z_native = complex(Z.real, Z.imag)
    acoplamento = abs(z_native)

    F = -k_e * q_e**2 / r**2 * acoplamento
    U = -k_e * q_e**2 / r * acoplamento
    U_ev = U / q_e
    U2_ev = U_ev / (2 * n)

    r_bohr = r_n_bohr(n)
    E_b = E_bohr(n)

    print(f"{n:>2} {r*1e9:12.3f} {U_ev:14.2f} {r2*1e9:12.3f} {U2_ev:14.2f} {r_bohr*1e9:12.3f} {E_b:12.2f} {acoplamento:10.6f}")    

# Dados que você já tem em execução:
n_vals = [1, 2, 3, 4, 5]
r_erire = np.array([n * (1.06e-10 / 2) for n in n_vals]) * 1e9  # nm
r_bohr = np.array([n**2 * 5.29e-11 for n in n_vals]) * 1e9     # nm
U_erire = np.array([-0.09, -0.00, -0.00, -0.00, -0.00])
E_bohr = np.array([-13.6 / n**2 for n in n_vals])

# Gráfico comparativo de energia
plt.figure(figsize=(10, 6))
plt.plot(n_vals, E_bohr, 'o--', label='Energia Bohr (eV)', color='gray')
plt.plot(n_vals, U_erire, 's-', label='Energia ERIЯƎ (eV)', color='blue')
plt.title(" Caso 1 - Baixa Coerência - Comparação Energética: ERIЯƎ vs Bohr")
plt.xlabel("Nível Quântico n")
plt.ylabel("Energia (eV)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfico comparativo de raio
plt.figure(figsize=(10, 6))
plt.plot(n_vals, r_bohr, 'o--', label='Raio Bohr (nm)', color='gray')
plt.plot(n_vals, r_erire, 's-', label='Raio ERIЯƎ (nm)', color='green')
plt.title(" Caso 1 - Baixa Coerência - Comparação de Raio: ERIЯƎ vs Bohr")
plt.xlabel("Nível Quântico n")
plt.ylabel("Raio (nm)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# =================================================================

# Inicializa estados com defasagem (para coerência não trivial)
elétron = ERIRE(1 + 0j, symbolic=False)
próton  = ERIRE(1 - 0j, symbolic=False)

# Bohr
def r_n_bohr(n): return n**2 * a_0
def E_bohr(n): return -13.6 / n**2

print("\n=== Caso 2 - Coerência Máxima - Comparação ERIЯƎ (com ERIRE) vs Bohr ===")
print(f"{'n':>2} {'r_ERIRE (nm_R)':>12} {'U_ERIRE (eV_R)':>14} {'r2_ERIRE (nm)':>12} {'U2_ERIRE (eV)':>14} {'r_Bohr (nm)':>12} {'E_Bohr (eV)':>12} {'|Z_total|':>10}")
print(f"{'':>2} {'Radial':>12} {'Radial':>14} {'Linear Dinamico':>12} {'Linear Dinamico':>14} {'Linear':>10} {'Linear':>12} {'':>10}")
print("-" * 75)

for n in range(1, n_levels + 1):
    r = n * (lambda_R / 2)                         # Raio ERIRE
    escala = a_0 / (lambda_R / 2)
    r2 = n**2 * (lambda_R / 2) * escala
    m = (2 * np.pi * r) / lambda_R                 # Parâmetro rotacional
    Ze = elétron.eire(elétron.z, m)
    Zp = próton.eire(próton.z, -m)
    Z = Ze * Zp
    z_native = complex(Z.real, Z.imag)
    acoplamento = abs(z_native)

    F = -k_e * q_e**2 / r**2 * acoplamento
    U = -k_e * q_e**2 / r * acoplamento
    U_ev = U / q_e
    U2_ev = U_ev / (2 * n)

    r_bohr = r_n_bohr(n)
    E_b = E_bohr(n)

    print(f"{n:>2} {r*1e9:12.3f} {U_ev:14.2f} {r2*1e9:12.3f} {U2_ev:14.2f} {r_bohr*1e9:12.3f} {E_b:12.2f} {acoplamento:10.6f}")    

# Dados que você já tem em execução:
n_vals = [1, 2, 3, 4, 5]
r_erire = np.array([n * (1.06e-10 / 2) for n in n_vals]) * 1e9  # nm
r_bohr = np.array([n**2 * 5.29e-11 for n in n_vals]) * 1e9     # nm
U_erire = np.array([-0.09, -0.00, -0.00, -0.00, -0.00])
E_bohr = np.array([-13.6 / n**2 for n in n_vals])

# Gráfico comparativo de energia
plt.figure(figsize=(10, 6))
plt.plot(n_vals, E_bohr, 'o--', label='Energia Bohr (eV)', color='gray')
plt.plot(n_vals, U_erire, 's-', label='Energia ERIЯƎ (eV)', color='blue')
plt.title("Caso 2 —- Coerência Máxima - Comparação Energética: ERIЯƎ vs Bohr")
plt.xlabel("Nível Quântico n")
plt.ylabel("Energia (eV)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfico comparativo de raio
plt.figure(figsize=(10, 6))
plt.plot(n_vals, r_bohr, 'o--', label='Raio Bohr (nm)', color='gray')
plt.plot(n_vals, r_erire, 's-', label='Raio ERIЯƎ (nm)', color='green')
plt.title("Caso 2 —- Coerência Máxima - Comparação de Raio: ERIЯƎ vs Bohr")
plt.xlabel("Nível Quântico n")
plt.ylabel("Raio (nm)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()