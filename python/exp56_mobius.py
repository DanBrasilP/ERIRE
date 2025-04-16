from ERIRE import ERIRE
from mpmath import mp, mpc, fabs, polar, sin, cos, pi
import math

# Configuração de precisão e escopo de busca
mp.dps = 50
mod_range = [1e-20 * i for i in range(1, 11)]  # módulos de 1e-20 até 1e-19
angle_steps = 36  # 10° por passo → 360° mapeados

def mobius_operator_erire(z, m=1):
    eri = ERIRE(z, m=m)
    twisted = eri.eire() * (-1)
    return eri.rire(twisted)

def mobius_operator_erire_inverse(z, m=1):
    eri = ERIRE(z, m=m)
    twisted = eri.eire() * (+1)
    return eri.rire(twisted)

def generate_complex(mag, angle_deg):
    angle_rad = mp.radians(angle_deg)
    return mpc(mag * cos(angle_rad), mag * sin(angle_rad))

# Inicialização
best_error = mp.inf
best_result = None

print("=== EXP56 – Dualidade Möbiana Coerencial ===")

for r1 in mod_range:
    for angle in range(0, 360, int(360 / angle_steps)):
        Z1 = generate_complex(r1, angle)
        Z2 = -Z1  # conjuguado angular e invertido

        Z1_restored = mobius_operator_erire(Z1)
        Z2_restored = mobius_operator_erire_inverse(Z2)

        Z_total = Z1_restored + Z2_restored
        Z_abs = fabs(Z_total)
        error = fabs(Z_abs - 1)

        if error < best_error:
            best_error = error
            best_result = {
                "Z1": Z1,
                "Z2": Z2,
                "Z1_restored": Z1_restored,
                "Z2_restored": Z2_restored,
                "Z_total": Z_total,
                "Z_abs": Z_abs,
                "angle_deg": angle,
                "r1": r1
            }

# Exibição final do melhor resultado
br = best_result
print("\n=== MELHOR CONFIGURAÇÃO ENCONTRADA ===")
print(f"Módulo:       {br['r1']}")
print(f"Ângulo:       {br['angle_deg']}°")
print(f"Z1:           {br['Z1']}")
print(f"Z2:           {br['Z2']}")
print(f"Z1_restaurado:{br['Z1_restored']}")
print(f"Z2_restaurado:{br['Z2_restored']}")
print(f"Z_total:      {br['Z_total']}")
print(f"|Z_total|:    {br['Z_abs']}")
print(f"Erro |Z|-1:   {best_error}")

if best_error < 1e-3:
    print("\n✔ Coerência restaurada: retorno à esfera confirmado.")
else:
    print("\n✖ Coerência incompleta: ajuste ainda não perfeito.")

# Inicialização
best_error = mp.inf
best_result = {}

print("\n\n=== EXP56 – Trindade Möbiana Coerencial ===")

for r in mod_range:
    for base_angle in range(0, 360, int(360 / angle_steps)):

        # Gera três pontos colapsados a 120° de separação
        Zs = [generate_complex(r, base_angle + k * 120) for k in range(3)]
        Z_restored = [mobius_operator_erire(z) for z in Zs]

        Z_total = sum(Z_restored)
        Z_abs = fabs(Z_total)
        error = fabs(Z_abs - 1)

        if error < best_error:
            best_error = error
            best_result = {
                "base_angle": base_angle,
                "modulo": r,
                "Zs": Zs,
                "Z_restored": Z_restored,
                "Z_total": Z_total,
                "Z_abs": Z_abs,
                "error": error
            }

# Resultado final
br = best_result
print("\n=== MELHOR TRINDADE ENCONTRADA ===")
print(f"Módulo:       {br['modulo']}")
print(f"Ângulo base:  {br['base_angle']}°")
for i, (z, zr) in enumerate(zip(br["Zs"], br["Z_restored"])):
    print(f"Z{i}:          {z}")
    print(f"Z{i}_restaurado: {zr}")
print(f"Z_total:      {br['Z_total']}")
print(f"|Z_total|:    {br['Z_abs']}")
print(f"Erro |Z|-1:   {br['error']}")

if br["error"] < 1e-3:
    print("\n✔ Coerência restaurada: trindade Möbiana fechada.")
else:
    print("\n✖ Coerência incompleta: ajuste ainda não perfeito.")