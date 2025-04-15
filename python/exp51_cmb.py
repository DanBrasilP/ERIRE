import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.stats import pearsonr
import os
import csv

# === 1. Carregar o espectro CMB do Planck ===
print("🔭 Carregando espectro CMB (Planck)...")
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmb_output')
filename = os.path.join(script_dir, 'data', 'COM_PowerSpect_CMB_R2.02.fits')
hdul = fits.open(filename)
data = hdul[1].data

ell = data['ELL']                # ℓ multipolos
cl_planck = data['D_ELL']        # D_ℓ = ℓ(ℓ+1)C_ℓ / 2π
hdul.close()
print(f"✔️  Dados carregados: {len(ell)} pontos espectrais\n")

# === 2. Coerência Angular e Parâmetros ERIЯƎ ===
print("🔧 Calculando coerência, fase e tempo emergente vetorial...")

D_max = np.max(cl_planck)
Gamma = cl_planck / D_max
Gamma = np.clip(Gamma, 0, 1)

Delta_phi = np.arccos(Gamma)
dphi = np.gradient(Delta_phi, ell)
omega = np.abs(dphi) + 1e-10  # Frequência coerencial, evita singularidade

# Tempo emergente
tempo = np.cumsum(1 / omega)
tempo -= tempo[0]
tempo_norm = tempo / np.max(tempo)

# === 3. Transformada Inversa TSR: Reconstrução da Coerência Z(ℓ) ===
print("🔄 Reconstruindo coerência Z(ℓ) pela transformada inversa TSR...")
mu = 1.0  # massa específica normalizada (ajustável)
A = 1.0   # área projetada unitária (normalização)

Z = np.sqrt((mu * A) / (cl_planck + 1e-12))  # Evita divisão por zero

# === 4. Detecção de Singularidades *∞ ===
print("🌀 Identificando zonas ressonantes e rupturas topológicas...")
ruptura = (np.gradient(Gamma, ell, edge_order=2) < 0) & (np.abs(dphi) > 0.015)
singularidade = omega > np.percentile(omega, 95)  # zonas de *∞

# === 5. Estatísticas e Diagnóstico ===
planck_mean = np.mean(cl_planck)
planck_std = np.std(cl_planck)
corr_time, _ = pearsonr(tempo_norm, cl_planck)

print("=== Estatísticas ERIЯƎ-TSR ===")
print(f"Média D_ℓ:              {planck_mean:.2f} µK²")
print(f"Desvio padrão:          {planck_std:.2f} µK²")
print(f"Tempo máximo emergente: {tempo[-1]:.2f}")
print(f"Correlação tempo-potência: {corr_time:.4f}")
print(f"Zonas de ruptura:       {np.sum(ruptura)} pontos")
print(f"Singularidades *∞:      {np.sum(singularidade)} pontos")
print("================================\n")

# === 6. Gráficos ERIЯƎ-TSR ===
plt.figure(figsize=(14, 6))

# (A) Espectro e regiões críticas
plt.subplot(1, 2, 1)
plt.plot(ell, cl_planck, label='CMB (Dₗ)', color='gray')
plt.scatter(ell[ruptura], cl_planck[ruptura], color='orange', label='Rupturas TSR', s=15)
plt.scatter(ell[singularidade], cl_planck[singularidade], color='red', label='*∞', s=15)
plt.xlabel(r'Multipolo $\ell$')
plt.ylabel(r'$D_\ell$ [$\mu K^2$]')
plt.title('Espectro CMB e Zonas Topológicas')
plt.grid(True)
plt.legend()

# (B) Tempo emergente e coerência reconstruída
plt.subplot(1, 2, 2)
plt.plot(ell, tempo_norm, label='t(ℓ) emergente', color='indigo')
plt.plot(ell, Z / np.max(Z), '--', label='Z(ℓ) reconstruído (normalizado)', color='teal')
plt.xlabel(r'Multipolo $\ell$')
plt.ylabel('Tempo / Coerência')
plt.title('Tempo Rotacional vs. Coerência Z(ℓ)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

# === 7. Exportar CSV com dados vetoriais ===
output_file = os.path.join(output_dir, 'saida_cmb_erire_vetorial.csv')
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['ell', 'D_ell', 'Gamma', 'Delta_phi', 'Omega', 'Tempo', 'Z', 'Ruptura', 'Singularidade'])
    for i in range(len(ell)):
        writer.writerow([
            ell[i], cl_planck[i], Gamma[i], Delta_phi[i],
            omega[i], tempo[i], Z[i],
            int(ruptura[i]), int(singularidade[i])
        ])

print(f"📁 Dados exportados para: {output_file}")

# === 8. Classificação Topológica Floral-Toroidal ===
print("🌸 Classificando padrões coerenciais no espectro...")

# Detectar flutuações oscilatórias em Z(ℓ)
Z_diff = np.gradient(Z, ell)
Z_ddiff = np.gradient(Z_diff, ell)

floral = (np.abs(Z_diff) > 0.002) & (np.abs(Z_ddiff) > 0.001)
toroidal = (np.abs(Z_diff) <= 0.002) & (np.abs(Z_ddiff) <= 0.001)

# Marcação no gráfico de coerência
plt.figure(figsize=(10, 4))
plt.plot(ell, Z, label='Z(ℓ) reconstruído', color='black')
plt.scatter(ell[floral], Z[floral], color='purple', s=15, label='Floral')
plt.scatter(ell[toroidal], Z[toroidal], color='green', s=15, label='Toroidal')
plt.xlabel(r'Multipolo $\ell$')
plt.ylabel('Z(ℓ) [unid. coerencial]')
plt.title('Classificação Topológica da Coerência Reconstruída')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === 9. Exportar classificações topológicas ===
output_topo = os.path.join(output_dir, 'saida_topologia_cmb.csv')
with open(output_topo, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['ell', 'Z', 'Topo_Floral', 'Topo_Toroidal'])
    for i in range(len(ell)):
        writer.writerow([
            ell[i], Z[i],
            int(floral[i]), int(toroidal[i])
        ])

print(f"🗂️ Topologia exportada para: {output_topo}")

# === 10. Construção da Hélice Coerencial Rotacional (3D) ===
print("🧭 Gerando hélice vetorial 3D (Z, φ, t)...")

# Coordenadas vetoriais ERIЯƎ
x = Z * np.cos(Delta_phi)
y = Z * np.sin(Delta_phi)
z = tempo

# Gráfico 3D da hélice
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, color='darkviolet', linewidth=2, label='Hélice coerencial')
ax.scatter(x[ruptura], y[ruptura], z[ruptura], color='orange', label='Ruptura', s=30)
ax.scatter(x[singularidade], y[singularidade], z[singularidade], color='red', label='*∞', s=30)
ax.set_xlabel('x = Z cos(φ)')
ax.set_ylabel('y = Z sin(φ)')
ax.set_zlabel('z = t(ℓ)')
ax.set_title('Hélice Ressonante ERIЯƎ do CMB')
ax.legend()
plt.tight_layout()
plt.show()

# === 11. Exportar Hélice Vetorial para CSV ===
output_helix = os.path.join(output_dir, 'saida_helice_erire.csv')
with open(output_helix, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['ell', 'x', 'y', 'z', 'Z', 'Delta_phi', 'Tempo', 'Ruptura', 'Singularidade'])
    for i in range(len(ell)):
        writer.writerow([
            ell[i], x[i], y[i], z[i],
            Z[i], Delta_phi[i], tempo[i],
            int(ruptura[i]), int(singularidade[i])
        ])
print(f"🧬 Hélice vetorial exportada para: {output_helix}")

# === 12. Amostra de pontos da hélice no terminal ===
print("🧾 Amostra da hélice vetorial ERIЯƎ:")
for i in range(0, len(ell), 4):
    print(f"ℓ={ell[i]:4d} | x={x[i]:+.4f} | y={y[i]:+.4f} | z={z[i]:.2f} | Z={Z[i]:.4f}")

# === 13. Amostra interpretada da hélice coerencial ===
print("\n📡 Leitura interpretada da hélice ERIЯƎ:")
print(f"{'ℓ':>4} | {'D_ℓ [µK²]':>10} | {'Γ':>5} | {'Δφ [rad]':>10} | {'Z':>7} | {'ω [rad/ℓ]':>9} | {'t':>7} | Tipo")
print("-" * 72)

for i in range(len(ell)):
    tipo = []
    if ruptura[i]: tipo.append("Ruptura")
    if singularidade[i]: tipo.append("*∞")
    if floral[i]: tipo.append("Floral")
    if toroidal[i]: tipo.append("Toroidal")
    tipo_str = ", ".join(tipo) if tipo else "—"

    print(f"{ell[i]:4d} | {cl_planck[i]:10.2f} | {Gamma[i]:.3f} | {Delta_phi[i]:10.4f} |"
          f" {Z[i]:7.4f} | {omega[i]:9.5f} | {tempo[i]:7.2f} | {tipo_str}")

# === 14. Análise de Fourier sobre a Coerência Z(ℓ) ===
print("\n🎼 Aplicando Transformada de Fourier sobre Z(ℓ)...")

from scipy.fft import fft, fftfreq

# Dados
N = len(Z)
Z_meaned = Z - np.mean(Z)  # Remover tendência para análise espectral pura
Z_fft = fft(Z_meaned)
freqs = fftfreq(N, d=np.mean(np.diff(ell)))  # Frequência em domínio ℓ⁻¹

# Apenas metade útil (positiva)
N2 = N // 2
Z_power = np.abs(Z_fft[:N2])**2
freqs_pos = freqs[:N2]

# Localizar frequências dominantes
idx_sorted = np.argsort(Z_power)[::-1]
top_freqs = freqs_pos[idx_sorted[:5]]
top_powers = Z_power[idx_sorted[:5]]

# === Log interpretativo no terminal ===
print("🎧 Modos dominantes de coerência global (Z):")
print(f"{'Freq (1/ℓ)':>12} | {'Potência':>10}")
print("-" * 26)
for i in range(len(top_freqs)):
    print(f"{top_freqs[i]:12.5f} | {top_powers[i]:10.4f}")
print("-" * 26)
print(f"🔎 Frequência dominante: {top_freqs[0]:.5f} (1/ℓ)")

# === 15. Exportar espectro de coerência para CSV ===
output_fourier = os.path.join(output_dir, 'saida_fourier_Z.csv')
with open(output_fourier, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Freq_(1/ell)', 'Power_Z_fft'])
    for f, p in zip(freqs_pos, Z_power):
        writer.writerow([f, p])

print(f"📤 Espectro de coerência global exportado para: {output_fourier}")
