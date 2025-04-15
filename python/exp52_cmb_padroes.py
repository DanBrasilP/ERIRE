# exp52_padroes.py
import csv
import fractions
import math
import os
from collections import defaultdict

# === 1. Carregar os dados de Fourier do CMB ===
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmb_output')
arquivo_csv = os.path.join(script_dir, 'saida_fourier_Z.csv')
dados = []

with open(arquivo_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        freq = float(row['Freq_(1/ell)'])
        pot = float(row['Power_Z_fft'])
        frac = fractions.Fraction(freq).limit_denominator(1000)
        p, q = frac.numerator, frac.denominator
        produto = p * q
        dados.append({
            'freq': freq,
            'fração': f'{p}/{q}',
            'p': p,
            'q': q,
            'p·q': produto,
            'pot': pot
        })

# === 2. Estimar n_f e verificar padrão ===
D = 10000  # normalização empírica para manter padrão com 21/10000
for d in dados:
    numerador_estimado = d['pot'] * D
    n_f_est = round((d['p·q']) / numerador_estimado)
    if n_f_est == 0:
        d['n_f_est'] = 0
        d['pot_teor'] = float('inf')  # ou 0, ou None
    else:
        d['n_f_est'] = n_f_est
        d['pot_teor'] = d['p·q'] / (n_f_est * D)

# === 3. Comparar com padrões quânticos conhecidos (modo opcional) ===
# Isso pode ser expandido com uma tabela vinda do exp18

# === 4. Exibir no terminal ===
print("\n📊 Análise dos Modos de Frequência e Potência")
print(f"{'f (1/ℓ)':>10} | {'Fraç.':>7} | {'p·q':>5} | {'P_obs':>8} | {'n̂_f':>4} | {'P_teor':>8}")
print("-" * 60)
for d in dados:
    print(f"{d['freq']:>10.5f} | {d['fração']:>7} | {d['p·q']:>5} | {d['pot']:>8.4g} | {d['n_f_est']:>4} | {d['pot_teor']:>8.4g}")

# === 5. Exportar para CSV final com estimativas ===
saida_csv = os.path.join(script_dir, 'saida_padroes_n_f.csv')
with open(saida_csv, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['freq', 'fração', 'p', 'q', 'p·q', 'pot', 'n_f_est', 'pot_teor'])
    writer.writeheader()
    for row in dados:
        writer.writerow(row)

print("\n✅ Arquivo exportado: saida_padroes_n_f.csv")

# === 6. Cálculo do fator vetorial puro Φ(f) ===
import numpy as np

# Frequência base ressonante observada: 3/7
f0 = 3 / 7
alpha = 2  # parâmetro de afinidade angular ressonante (exato, não ajustado)

for d in dados:
    f = d['freq']
    fase = 2 * np.pi * (f / f0)
    phi = abs(np.cos(fase))**alpha
    d['phi_f'] = phi

    # Nova potência teórica com Φ(f)
    d['pot_teor_phi'] = phi * d['p·q'] / (d['n_f_est'] * D) if d['n_f_est'] > 0 else None

# === 7. Atualização da saída de terminal ===
print("\n🎯 Potência projetada com coerência angular Φ(f):")
print(f"{'f':>8} | {'Fraç.':>7} | {'Φ(f)':>6} | {'P_obs':>8} | {'P_Φ':>8}")
print("-" * 55)
for d in dados:
    pot_phi = d['pot_teor_phi']
    if pot_phi is not None:
        print(f"{d['freq']:>8.5f} | {d['fração']:>7} | {d['phi_f']:>6.3f} | {d['pot']:>8.4g} | {pot_phi:>8.4g}")

# === 8. Exportar CSV completo com Φ(f) ===
saida_csv = os.path.join(script_dir, 'saida_padroes_phi.csv')
with open(saida_csv, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=[
        'freq', 'fração', 'p', 'q', 'p·q', 'pot', 'n_f_est',
        'pot_teor', 'phi_f', 'pot_teor_phi'
    ])
    writer.writeheader()
    for row in dados:
        writer.writerow(row)

print("\n📤 Arquivo exportado com Φ(f): saida_padroes_phi.csv")

# === 9. Acoplamento harmônico entre múltiplos modos ===
# Soma harmônica ponderada de todos os múltiplos inteiros de cada f no espectro

def harmonic_overlap(f, all_freqs, max_harm=5, tol=1e-3):
    overlap = 0
    for h in range(2, max_harm+1):
        target = f * h
        for other in all_freqs:
            if abs(other - target) < tol:
                overlap += 1 / h  # peso decrescente com harmônico
    return overlap

all_freqs = [d['freq'] for d in dados]
for d in dados:
    d['harm_overlap'] = harmonic_overlap(d['freq'], all_freqs)

print("\n🔁 Harmônicos acoplados detectados:")
print(f"{'f':>8} | {'H_acopl.':>9}")
print("-" * 20)
for d in dados:
    print(f"{d['freq']:>8.5f} | {d['harm_overlap']:>9.3f}")

# === 10. Reflexão espectral f ↔ 1 – f (simetria de Riemann) ===
for d in dados:
    d['f_mirror'] = abs(1 - d['freq'])

# === 11. Acoplamento angular-topológico (vetorial) ===
# Modelo inicial: φ(f) * φ(1-f) → coerência dupla cruzada
for d in dados:
    if 'phi_f' in d and 'f_mirror' in d:
        phi_mirror = abs(np.cos(2 * np.pi * d['f_mirror'] / f0))**alpha
        d['phi_composta'] = d['phi_f'] * phi_mirror
        d['pot_phi_cruzada'] = d['phi_composta'] * d['p·q'] / (d['n_f_est'] * D) if d['n_f_est'] > 0 else None

# === 12. Peso topológico por múltiplos ramos florais ou toroidais ===
# Modelo simplificado: se f está a Δf de um múltiplo de 1/7 ou 1/14, recebe fator simbólico extra

def ramificacao_log(f):
    base = [1/7, 1/14, 3/7, 5/14, 6/7]
    for b in base:
        if abs(f - b) < 0.005:
            return 1.5  # peso simbólico de ramificação coerente
    return 1.0

for d in dados:
    d['ramo_log'] = ramificacao_log(d['freq'])
    if d.get('pot_phi_cruzada') is not None:
        d['pot_final_res'] = d['pot_phi_cruzada'] * d['ramo_log']
    else:
        d['pot_final_res'] = None  # ou 0.0, dependendo do uso posterior

# === 13. Exportar análise final completa ===
saida_csv = os.path.join(script_dir, 'saida_padroes_resonantes.csv')
with open(saida_csv, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=[
    'freq', 'fração', 'p', 'q', 'p·q', 'pot', 'n_f_est',
    'pot_teor',  # ← ADICIONE ESTA LINHA
    'phi_f', 'pot_teor_phi', 'harm_overlap', 'f_mirror',
    'phi_composta', 'pot_phi_cruzada', 'ramo_log', 'pot_final_res'
    ])

    writer.writeheader()
    for row in dados:
        writer.writerow(row)

print("\n✅ Arquivo exportado com ressonâncias completas: saida_padroes_resonantes.csv")
