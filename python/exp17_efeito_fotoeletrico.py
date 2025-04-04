from ERIRE import ERIRE
from mpmath import mp, fabs, arg, cos, mpc
import matplotlib.pyplot as plt
import numpy as np

# Precisão estendida
mp.dps = 50

# Constantes físicas (CODATA)
h = mp.mpf('6.62607015e-34')   # Planck (J·s)
e = mp.mpf('1.602176634e-19')  # Carga elementar (C)
c = mp.mpf('299792458')        # Velocidade da luz (m/s)

# Função para simular a transição rotacional coerente
def simular_emissao_foton_erire(z_base, m1, m2, modo="emissão"):
    """
    Simula a transição rotacional ERIЯƎ e calcula a energia emitida ou absorvida.
    """
    erire1 = ERIRE(z_base, m=m1, symbolic=False)
    erire2 = ERIRE(z_base, m=m2, symbolic=False)

    # Calculando os estados rotacionais
    z1 = erire1.eire()
    z2 = erire2.eire()

    # Diferença de fase entre os estados
    delta_phase = fabs(mp.arg(z1) - mp.arg(z2))

    # Energia proporcional à fase × frequência
    energia_joule = h * delta_phase * mp.mpf('4.3e14')  # Frequência base (~ 640 nm / Césio)
    energia_eV = energia_joule / e

    # Definir o sinal (positivo para absorção, negativo para emissão)
    sinal = "-" if modo == "emissão" else "+"
    return float(energia_eV), float(delta_phase), sinal

# Raiz inicial (complexa) representando o estado base
z_base = mpc(1, 1)

# Transição de m=2 → m=1 (Emissão)
energia_emissao, delta_phi_em, sinal_em = simular_emissao_foton_erire(z_base, m1=2, m2=1, modo="emissão")
# Transição de m=1 → m=2 (Absorção)
energia_absorcao, delta_phi_abs, sinal_abs = simular_emissao_foton_erire(z_base, m1=1, m2=2, modo="absorção")

# Função trabalho para Césio (material fotoelétrico)
work_function_cs = 1.94  # eV

# === Saída descritiva ===
print("=== Simulação ERIЯƎ do Efeito Fotoelétrico ===")
print("--- Transição Rotacional e Interpretação ---")
print(f"Transição m=2 → m=1 (Emissão):")
print(f"  • Δφ:       {delta_phi_em:.6f} rad")
print(f"  • Energia:  {energia_emissao:.6f} eV")

print(f"\nTransição m=1 → m=2 (Absorção):")
print(f"  • Δφ:       {delta_phi_abs:.6f} rad")
print(f"  • Energia:  {energia_absorcao:.6f} eV")

print("\n--- Análise Fotoelétrica ---")
print(f"Material:                     Césio (φ ≈ {work_function_cs:.2f} eV)")

if energia_absorcao > work_function_cs:
    print(f">>> Energia absorvida excede o limiar: emissão de elétron é possível.")
    print(f">>> Energia cinética esperada (Einstein): {(energia_absorcao - work_function_cs):.6f} eV")
else:
    print(f">>> Energia absorvida insuficiente: elétron não é emitido.")

# === Visualização ===
plt.figure(figsize=(6, 6))
ax = plt.subplot(111, polar=True)
ax.plot([0, delta_phi_em], [0, 1], 'r-', label='Δφ emissão (m=2→1)')
ax.plot([0, delta_phi_abs], [0, 1], 'b--', label='Δφ absorção (m=1→2)')
ax.set_title("Transições ERIЯƎ no Espaço Rotacional")
ax.legend()
plt.grid(True)
plt.show()

print("\n=== Tentativas de Emissão Ajustadas ===")

# Frequências mais altas (luz UV)
frequencias_uv = [
    ("Luz UV A (320 nm)", c / mp.mpf('320e-9')),
    ("Luz UV B (280 nm)", c / mp.mpf('280e-9')),
    ("Luz UV C (250 nm)", c / mp.mpf('250e-9')),
]

# Transições com maior Δφ (maior salto de m)
saltos = [(3, 1), (4, 1), (5, 1)]

for nome_frequencia, frequencia in frequencias_uv:
    print(f"\n--- Teste com {nome_frequencia} ({float(frequencia):.2e} Hz) ---")
    for m1, m2 in saltos:
        erire_i = ERIRE(z_base, m=m1, symbolic=False)
        erire_f = ERIRE(z_base, m=m2, symbolic=False)

        z_i = erire_i.eire()
        z_f = erire_f.eire()

        delta_phi = fabs(arg(z_i) - arg(z_f))
        energia_joule = h * delta_phi * frequencia
        energia_ev = energia_joule / e

        print(f"Transição m={m1} → m={m2}")
        print(f"  • Δφ = {float(delta_phi):.6f} rad")
        print(f"  • Energia = {float(energia_ev):.6f} eV")

        if energia_ev > work_function_cs:
            print("  >>> Elétron é emitido! ✅")
            print(f"  >>> Energia cinética esperada = {float(energia_ev - work_function_cs):.6f} eV")
        else:
            print("  >>> Energia insuficiente para emissão.")
