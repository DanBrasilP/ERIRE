# === Simulação ERIЯƎ - Representação Geométrica da Equação de Schrödinger ===

import numpy as np
import matplotlib.pyplot as plt
import time
import cmath
from ERIRE import ERIRE
from matplotlib.animation import FuncAnimation
from mpmath import mp, arg, mpc
from mpl_toolkits.mplot3d import Axes3D  # Import 3D plot support


# === Configurações Globais ===
mp.dps = 50  # Precisão estendida

# Raiz inicial (complexa) representando o estado base
z_base = mpc(1, 1)

# Constantes físicas (CODATA)
h = mp.mpf('6.62607015e-34')   # Planck (J·s)
e = mp.mpf('1.602176634e-19')  # Carga elementar (C)

print("=== Iniciando Simulação Geométrica ERIЯƎ para Schrödinger ===")

# === Parâmetros da malha espacial ===
L = 200               # Comprimento total
dx = 1                # Espaçamento espacial
N = L // dx           # Número de pontos
x = np.linspace(-L//2, L//2, N)

# === Tempo ===
dt = 0.1              # Passo de tempo (arbitrário por enquanto)
steps = 100           # Número total de iterações

# === Inicialização do campo rotacional coerente (ψ) ===
def gerar_estado_coerente(x, centro=0, largura=15, m=2):
    """Cria uma estrutura de coerência rotacional ERIЯƎ centralizada"""
    return np.array([
        ERIRE(mpc(np.exp(-((xi - centro)**2) / largura**2), 0), m=m).eire()
        for xi in x
    ])

# Estado inicial
psi = gerar_estado_coerente(x)
print(f"> Estado inicial rotacional gerado (m=2), pontos: {len(psi)}")

# === Funções de análise ===
def densidade_coerencia(psi):
    """Calcula a densidade projetada |ψ|² como coerência local"""
    return np.abs(psi)**2

def fase_rotacional(psi):
    """Fase rotacional local"""
    return np.angle(np.array([complex(p) for p in psi]))

# === Plot inicial ===
def plot_estado_inicial():
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(x, densidade_coerencia(psi), label='|ψ|²')
    plt.title("Densidade de Coerência |ψ(x)|²")
    plt.xlabel("Espaço (x)")
    plt.ylabel("Densidade")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(x, fase_rotacional(psi), color='orange', label='Fase ψ')
    plt.title("Fase Rotacional de ψ(x)")
    plt.xlabel("Espaço (x)")
    plt.ylabel("Fase [rad]")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === Execução inicial ===
start = time.time()
plot_estado_inicial()
end = time.time()

print(f"> Tempo de geração e plotagem inicial: {end - start:.2f} segundos")
print(">>> Pronto para iniciar evolução temporal e modelagem potencial.")


# === Bloco 2: Evolução Temporal da Coerência ===

print("\n=== Iniciando evolução temporal ===")
omega = 0.05  # Frequência angular simulada da rotação do campo (rad/unidade t)

# Inicialização de figura para animação
fig, ax = plt.subplots(figsize=(10, 5))
linha_coerencia, = ax.plot([], [], lw=2, label="|ψ(x, t)|²")
linha_fase, = ax.plot([], [], lw=1, linestyle='--', label="arg(ψ)")
ax.set_xlim(x.min(), x.max())
ax.set_ylim(0, 2)
ax.set_xlabel("Espaço (x)")
ax.set_ylabel("Valor")
ax.set_title("Evolução Temporal da Estrutura Rotacional ERIЯƎ")
ax.grid(True)
ax.legend()

# Estado global compartilhado
psi_temporal = np.copy(psi)

def init_anim():
    linha_coerencia.set_data([], [])
    linha_fase.set_data([], [])
    return linha_coerencia, linha_fase

def update_anim(frame):
    global psi_temporal
    t = frame * dt

    # Aplica evolução rotacional por multiplicação fase (i.e., ψ(x) * e^{-iωt})
    psi_temporal = np.array([
        val * np.exp(-1j * omega * t)
        for val in psi_temporal
    ])

    coerencia = np.abs(psi_temporal)**2
    fase = np.angle(np.array([complex(p) for p in psi_temporal]))

    linha_coerencia.set_data(x, coerencia)
    linha_fase.set_data(x, fase)

    # Dentro de update_anim (opcional: imprimir somente a cada 20 frames)
    if frame % 20 == 0:
        energia_media = np.mean(coerencia)
        fase_media = np.mean(fase)
        print(f"[Frame {frame}] ⏱ t = {float(t):.2f}")
        print(f"  • Energia média (|ψ|²): {float(energia_media):.4f}")
        print(f"  • Fase média:           {float(fase_media):.4f} rad")

    return linha_coerencia, linha_fase

# Criação da animação (exibe em tempo real)
ani = FuncAnimation(fig, update_anim, frames=200, init_func=init_anim,
                    blit=True, interval=50, repeat=False)

plt.show()

# === Bloco 3: Influência de um Potencial Externo V(x) ===

print("\n=== Simulando a influência de um potencial externo ===")

# Define um potencial externo (poço ou barreira)
# Exemplo: uma barreira de potencial entre -1 e 1
Vx = [mp.mpf('0.0') if abs(xi) > 1 else mp.mpf('0.6') for xi in x]

# Aplica modulação da coerência rotacional pela presença de V(x)
coerencia_modulada = []
fase_modulada = []

for i, xi in enumerate(x):
    # Cada ponto espacial simula um "átomo" com coerência rotacional influenciada por V(x)
    influencia = Vx[i]
    estado = ERIRE(z_base, m=2 + float(influencia)*3, symbolic=False)
    z = estado.eire()

    # Fase rotacional e coerência ajustada
    coerencia_modulada.append(float(abs(z)**2))
    fase_modulada.append(float(mp.arg(z)))

# Gráfico: coerência e fase sob influência de V(x)
fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

axs[0].plot(x, list(map(float, Vx)), 'k--', label="V(x) - Potencial")
axs[0].set_ylabel("Potencial (V)")
axs[0].legend()
axs[0].grid()

axs[1].plot(x, coerencia_modulada, 'b-', label="|ψ(x)|² com V(x)")
axs[1].plot(x, fase_modulada, 'r--', label="arg(ψ) com V(x)")
axs[1].set_ylabel("Coerência e Fase")
axs[1].set_xlabel("Espaço (x)")
axs[1].legend()
axs[1].grid()

plt.suptitle("Influência de Potencial Externo na Estrutura Rotacional")
plt.tight_layout()
plt.show()

# Estatísticas após potencial externo
print("\n--- Análise após Potencial Externo ---")
print(f"  • Máximo |ψ(x)|² com V(x): {max(coerencia_modulada):.4f}")
print(f"  • Mínimo |ψ(x)|² com V(x): {min(coerencia_modulada):.4f}")
print(f"  • V(x) máximo:             {max(map(float, Vx)):.2f}")
print(f"  • V(x) mínimo:             {min(map(float, Vx)):.2f}")


# === Bloco 4: Projeções Tridimensionais da Estrutura Rotacional ===

# psi_base será uma cópia da parte real da função de onda inicial, convertida para float
psi_base = np.array([float(p.real) for p in psi])

# Estimativa da energia local pode ser feita usando uma aproximação proporcional à densidade de coerência
# Aqui usamos a densidade rotacional (|ψ|²) como proxy da energia
energia_local = np.array([float(np.abs(p)**2) for p in psi])

print("\n=== Estrutura Rotacional Tridimensional ===")

# Parâmetros espaciais
x_vals = x  # reutilizando vetor x do domínio
n_vals = [1, 2, 3]  # múltiplos níveis rotacionais (como n quântico)

# Armazena coordenadas projetadas nos planos rotacionais
coords_xy, coords_yz, coords_xz = [], [], []

for xi in x_vals:
    # Modelo ERIЯƎ tridimensional — 3 planos ortogonais coerentes
    z_xy = ERIRE(z_base, m=2, symbolic=False).eire()
    z_yz = ERIRE(z_base, m=3, symbolic=False).eire()
    z_xz = ERIRE(z_base, m=4, symbolic=False).eire()

    # Projeções em cada plano
    coords_xy.append((float(mp.re(z_xy)), float(mp.im(z_xy))))
    coords_yz.append((float(mp.re(z_yz)), float(mp.im(z_yz))))
    coords_xz.append((float(mp.re(z_xz)), float(mp.im(z_xz))))

# Separar coordenadas
x_xy, y_xy = zip(*coords_xy)
x_yz, z_yz = zip(*coords_yz)
y_xz, z_xz = zip(*coords_xz)

# Gráfico 3D das projeções rotacionais
plt.figure(figsize=(10, 5))
psi_float = [complex(float(z.real), float(z.imag)) for z in psi_base]
phases = [cmath.phase(z) for z in psi_float]

projections = {
    "Plano XY (Re vs Im)": [(z.real, z.imag) for z in psi_float],
    "Plano YZ (Im vs Φ)":  [(z.imag, p) for z, p in zip(psi_float, phases)],
    "Plano XZ (Re vs Φ)":  [(z.real, p) for z, p in zip(psi_float, phases)],
}

for i, (title, coords) in enumerate(projections.items()):
    plt.subplot(1, 3, i+1)
    x_proj, y_proj = zip(*coords)
    plt.plot(x_proj, y_proj, label=title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(title)
    plt.grid(True)
    plt.legend()

plt.suptitle("Projeções Rotacionais nos Três Planos ERIЯƎ")
plt.tight_layout()
plt.show()

# === Bloco 5: Amortecimento Coerencial (Interação com o Meio) ===

print("\n=== Simulação com Amortecimento Coerencial ===")

print("\n=== Preparando base para amortecimento ===")

print("> psi_base e energia_local definidas com base no estado atual")

# Define uma função de modulação para o fator de coerência Γ ao longo do espaço
def gamma_modulador(x, tipo="linear"):
    if tipo == "linear":
        return 1 - 0.3 * (x / x.max())  # diminui gradualmente
    elif tipo == "gauss":
        return np.exp(-((x - x.mean())**2) / (2 * (0.3 * x.max())**2))
    else:
        return np.ones_like(x)  # sem modulação

gamma_coerencia = gamma_modulador(x, tipo="gauss")  # escolha do tipo de amortecimento

# Recalcula a função de onda com modulação
psi_modulado = np.real(psi_base) * gamma_coerencia

# Recalcula energia local com modulação
energia_modulada = energia_local * gamma_coerencia

# Plota a função de onda com amortecimento
plt.figure(figsize=(10, 4))
plt.plot(x, psi_base.real, 'b--', label='Função de Onda (real)')
plt.plot(x, psi_modulado, 'r-', label='Com Amortecimento (real)')
plt.title('Função de Onda com Modulação Coerencial (Éter)')
plt.xlabel('x (espaço rotacional)')
plt.ylabel('ψ(x)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Plota energia local com e sem modulação
plt.figure(figsize=(10, 4))
plt.plot(x, energia_local, 'g--', label='Energia Local (sem Γ)')
plt.plot(x, energia_modulada, 'k-', label='Com Amortecimento (Γ(x))')
plt.title('Energia Rotacional Local com Amortecimento')
plt.xlabel('x (espaço rotacional)')
plt.ylabel('Energia (eV)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Estatísticas após potencial externo
print("\n--- Análise após Potencial Externo ---")
print(f"  • Máximo |ψ(x)|² com V(x): {max(coerencia_modulada):.4f}")
print(f"  • Mínimo |ψ(x)|² com V(x): {min(coerencia_modulada):.4f}")
print(f"  • V(x) máximo:             {max(map(float, Vx)):.2f}")
print(f"  • V(x) mínimo:             {min(map(float, Vx)):.2f}")


# === Bloco 6: Estimativa Geométrica da Constante de Planck (h) e Fator de Coerência ===

print("\n=== Estimativa Dinâmica de h (Planck) via ERIЯƎ ===")

# Fase rotacional entre dois estados coerentes
z_m2 = ERIRE(z_base, m=2).eire()
z_m1 = ERIRE(z_base, m=1).eire()
delta_phi = mp.fabs(arg(z_m2) - arg(z_m1))
delta_phi_float = float(delta_phi)
gamma_phi = float(mp.cos(delta_phi))  # Γ = cos(Δφ)

# Frequência real da transição de Lyman-α (n=2 → n=1, hidrogênio)
# λ ≈ 121.6 nm => ν = c / λ
c = mp.mpf('299792458')  # velocidade da luz (m/s)
lambda_real = mp.mpf('121.6e-9')  # metros
freq_real = c / lambda_real

# Energia rotacional corrigida com coerência (Γ·Δφ·h·ν)
energia_rotacional_corrigida = h * delta_phi * gamma_phi * freq_real
energia_ev_corrigida = energia_rotacional_corrigida / e

# Recalcula h com base na energia corrigida
h_estimado = (energia_ev_corrigida * e) / (delta_phi * gamma_phi * freq_real)

print(f"Δφ usado:                       {delta_phi_float:.6f} rad")
print(f"Γ = cos(Δφ):                    {gamma_phi:.6f}")
print(f"Frequência real (ν):            {float(freq_real):.3e} Hz")
print(f"Energia estimada (corrigida):   {float(energia_ev_corrigida):.6f} eV")
print(f"h real (CODATA):                {float(h):.5e} J·s")
print(f"h estimado (corrigido):         {float(h_estimado):.5e} J·s")
print(f"Erro relativo:                  {float(abs(h_estimado - h) / h * 100):.5e} %")

print("\n--- Diagnóstico da Estimativa de h ---")
h_erro_abs = abs(h_estimado - h)
print(f"  • Erro absoluto (h):            {float(h_erro_abs):.5e} J·s")
if h_erro_abs < 1e-40:
    print("  ✅ Excelente aproximação de h (alta coerência rotacional)")
else:
    print("  ⚠️  Erro ainda alto — revisar fator de coerência ou transição usada.")


# === Gráfico de coerência rotacional Γ(Δφ) ===

phi_range = np.linspace(0, np.pi, 300)
gamma_vals = np.cos(phi_range)

plt.figure(figsize=(8, 4))
plt.plot(phi_range, gamma_vals, 'm-', label='Γ(Δφ) = cos(Δφ)')
plt.axvline(x=delta_phi_float, color='gray', linestyle='--', label=f'Δφ usado')
plt.title("Projeção Geométrica do Fator de Coerência Γ")
plt.xlabel("Δφ (rad)")
plt.ylabel("Γ = cos(Δφ)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# === Bloco 7: Conversão Rotacional → Medidas Reais (λ, ν, E) ===
print("\n=== Conversão do Domínio Rotacional para Medidas Reais ===")

# Usa Δφ obtido anteriormente (delta_phi)
# Assumimos que a energia simulada (em eV) foi calculada como:
energia_simulada = h * delta_phi * gamma_phi * freq_real / e  # já temos isso acima

# Convertemos para frequência estimada inversa
# Rearranjando: ν_estimado = E / (Δφ * Γ * h)
nu_estimado = (energia_simulada * e) / (delta_phi * gamma_phi * h)

# Comprimento de onda estimado
lambda_estimado = c / nu_estimado  # m

# Dados reais para comparação (exemplo: Lyman-α)
lambda_lyman = mp.mpf("121.6e-9")  # m
nu_lyman = c / lambda_lyman

print(f"Δφ (rad):                        {float(delta_phi):.6f}")
print(f"Γ (cos Δφ):                      {float(gamma_phi):.6f}")
print(f"Frequência estimada (Hz):        {float(nu_estimado):.3e}")
print(f"Comprimento de onda estimado:    {float(lambda_estimado*1e9):.2f} nm")
print(f"Comparativo (Lyman-α):           121.60 nm")

erro_nm = abs(lambda_estimado - lambda_lyman) * 1e9
erro_percentual = (erro_nm / float(lambda_lyman*1e9)) * 100

print(f"Erro absoluto em λ:              {float(erro_nm):.3f} nm")
print(f"Erro percentual relativo:        {float(erro_percentual):.3f} %")

# === Bloco 8: Superposição Tridimensional Coerente ===

print("\n=== Superposição Tridimensional de Estados ERIЯƎ ===")

# Defasagens entre os planos (i, j, k)
phase_i = 0                      # Plano XY
phase_j = 2 * np.pi / 3          # Plano YZ (120° defasado)
phase_k = 4 * np.pi / 3          # Plano XZ (240° defasado)

# Calcula os três componentes rotacionais com suas defasagens
psi_i = np.array([
    ERIRE(z_base * cmath.exp(1j * phase_i), m=2).eire()
    for _ in x
])
psi_j = np.array([
    ERIRE(z_base * cmath.exp(1j * phase_j), m=3).eire()
    for _ in x
])
psi_k = np.array([
    ERIRE(z_base * cmath.exp(1j * phase_k), m=4).eire()
    for _ in x
])

# Superposição normalizada
psi_superposto = (psi_i + psi_j + psi_k) / 3

# Módulo e fase da superposição
coerencia_total = np.abs(psi_superposto) ** 2
fase_total = np.angle(np.array([complex(p) for p in psi_superposto]))

# Gráficos
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(x, coerencia_total, label="|Ψᵢⱼₖ(x)|²")
plt.title("Densidade de Coerência da Superposição Tridimensional")
plt.xlabel("Espaço (x)")
plt.ylabel("|Ψ|²")
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(x, fase_total, color='orange', label="arg(Ψᵢⱼₖ(x))")
plt.title("Fase Rotacional da Superposição")
plt.xlabel("Espaço (x)")
plt.ylabel("Fase [rad]")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.suptitle("Superposição Tridimensional de Estados ERIЯƎ (ψᵢ + ψⱼ + ψₖ)")
plt.show()

# === Diagnóstico Terminal da Superposição ===
print("\n--- Diagnóstico da Superposição Tridimensional ---")
print(f"  • Amplitude média |Ψᵢⱼₖ|²:         {float(np.mean(coerencia_total)):.4f}")
print(f"  • Amplitude máxima |Ψᵢⱼₖ|²:        {float(np.max(coerencia_total)):.4f}")
print(f"  • Amplitude mínima |Ψᵢⱼₖ|²:        {float(np.min(coerencia_total)):.4f}")
print(f"  • Fase média (rad):               {float(np.mean(fase_total)):.4f}")
print(f"  • Fase desvio padrão (rad):       {float(np.std(fase_total)):.4f}")
print(f"  • Desvio coerencial (indicador de colapso): {float(np.max(coerencia_total) - np.min(coerencia_total)):.4f}")

# === Gerar estados rotacionais completos para cada plano ===
# Corrigir psi_xy, psi_yz, psi_xz para gerar coerência espacial
psi_xy = np.array([
    ERIRE(mpc(np.exp(-((xi)**2) / 15**2), 0), m=2).eire()
    for xi in x
])
psi_yz = np.array([
    ERIRE(mpc(np.exp(-((xi)**2) / 15**2), 0), m=3).eire()
    for xi in x
])
psi_xz = np.array([
    ERIRE(mpc(np.exp(-((xi)**2) / 15**2), 0), m=4).eire()
    for xi in x
])

# Coerência total original (antes de perturbação)
coerencia_total = np.abs(psi_xy)**2 + np.abs(psi_yz)**2 + np.abs(psi_xz)**2

# === Bloco 9: Perturbações e Colapso de Coerência ===

print("\n=== Bloco 9: Perturbações e Colapso de Coerência ===")

# Introduz perturbação rotacional simulada (ex: ruído ou campo externo não coerente)
def perturbar_estado(psi, intensidade=0.05):
    np.random.seed(42)  # Reprodutibilidade
    ruido_fase = np.random.normal(loc=0.0, scale=intensidade, size=len(psi))
    psi_perturbado = np.array([
        val * np.exp(1j * ruido_fase[i])
        for i, val in enumerate(psi)
    ])
    return psi_perturbado

# Aplica perturbação à estrutura coerente tridimensional
psi_xy_pert = perturbar_estado(psi_xy, intensidade=0.1)
psi_yz_pert = perturbar_estado(psi_yz, intensidade=0.1)
psi_xz_pert = perturbar_estado(psi_xz, intensidade=0.1)

# Recalcula coerência e fase
coerencia_perturbada = np.abs(psi_xy_pert)**2 + np.abs(psi_yz_pert)**2 + np.abs(psi_xz_pert)**2
fase_perturbada = np.angle(np.array([complex(p) for p in psi_xy_pert])) \
                + np.angle(np.array([complex(p) for p in psi_yz_pert])) \
                + np.angle(np.array([complex(p) for p in psi_xz_pert]))

# Gráfico da estrutura com ruído
plt.figure(figsize=(10, 4))
plt.plot(x, coerencia_total, 'b--', label='Original |Ψ|²')
plt.plot(x, coerencia_perturbada, 'r-', label='Perturbada |Ψ|²')
plt.title("Comparação da Estrutura Coerente vs Perturbada")
plt.xlabel("x (espaço rotacional)")
plt.ylabel("Densidade Total")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Diagnóstico pós-perturbação
print("\n--- Diagnóstico Pós-Perturbação ---")
print(f"  • Coerência média (original):    {float(np.mean(coerencia_total)):.4f}")
print(f"  • Coerência média (perturbada):  {float(np.mean(coerencia_perturbada)):.4f}")
print(f"  • Desvio coerencial (original):  {float(np.max(coerencia_total) - np.min(coerencia_total)):.4f}")
print(f"  • Desvio coerencial (perturbado):{float(np.max(coerencia_perturbada) - np.min(coerencia_perturbada)):.4f}")
print(f"  • Fase média perturbada:         {float(np.mean(fase_perturbada)):.4f} rad")
print(f"  • Desvio padrão fase perturbada: {float(np.std(fase_perturbada)):.4f} rad")

# === Bloco 10: Recuperação da Coerência Rotacional (Pós-Perturbação) ===

print("\n=== Simulação de Recuperação de Coerência ===")

# Reaplica fator de coerência espacial (simula ambiente tentando reorganizar coerência)
recuperacao_gamma = gamma_modulador(x, tipo="gauss")

# Recupera coerência suavizando cada plano
psi_xy_rec = np.array([float(np.real(p)) for p in psi_xy]) * recuperacao_gamma
psi_yz_rec = np.array([float(np.real(p)) for p in psi_yz]) * recuperacao_gamma
psi_xz_rec = np.array([float(np.real(p)) for p in psi_xz]) * recuperacao_gamma

# Recalcula coerência total restaurada
coerencia_restaurada = psi_xy_rec**2 + psi_yz_rec**2 + psi_xz_rec**2

# Gráfico comparativo da coerência original, perturbada e restaurada
plt.figure(figsize=(10, 5))
plt.plot(x, coerencia_total, 'g--', label='Original')
plt.plot(x, coerencia_perturbada, 'r:', label='Perturbada')
plt.plot(x, coerencia_restaurada, 'b-', label='Restaurada')
plt.title("Comparativo de Coerência Rotacional |ψ|²")
plt.xlabel("x")
plt.ylabel("Coerência Total")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Output Terminal ---
print("\n--- Análise de Recuperação ---")
print(f"Coerência Máxima Original:      {float(np.max(coerencia_total)):.4f}")
print(f"Coerência Máxima Perturbada:    {float(np.max(coerencia_perturbada)):.4f}")
print(f"Coerência Máxima Restaurada:    {float(np.max(coerencia_restaurada)):.4f}")
print(f"Δ Máxima Perturbação:           {float(np.max(np.abs(coerencia_total - coerencia_perturbada))):.4f}")
print(f"Δ Máxima Recuperação:           {float(np.max(np.abs(coerencia_total - coerencia_restaurada))):.4f}")

# === Bloco 11: Frequência Angular Coerente e Energia Local ===

print("\n=== Cálculo da Frequência Angular Local ===")

# A frequência angular coerente local é estimada pela razão entre fase e amplitude total
# como uma variação de orientação rotacional ao longo do espaço

fase_xy = np.angle(np.array([complex(p) for p in psi_xy]))
fase_yz = np.angle(np.array([complex(p) for p in psi_yz]))
fase_xz = np.angle(np.array([complex(p) for p in psi_xz]))

# Derivada numérica das fases (variação angular local)
dfase_xy = np.gradient(fase_xy, dx)
dfase_yz = np.gradient(fase_yz, dx)
dfase_xz = np.gradient(fase_xz, dx)

# Estima a "frequência rotacional local"
frequencia_local = np.sqrt(dfase_xy**2 + dfase_yz**2 + dfase_xz**2)

# Conversão para frequência em Hz (considerando fator escalar simbólico, arbitrário)
escala_freq = 1e15  # Ajustável
frequencia_real = frequencia_local * escala_freq

# Energia local estimada (usando h de Planck real)
energia_local_real = frequencia_real * float(h) / float(e)  # Convertido para eV

# --- Gráfico ---
plt.figure(figsize=(10, 5))
plt.plot(x, energia_local_real, label='Energia Local Estimada (eV)', color='purple')
plt.xlabel("x")
plt.ylabel("Energia Local (eV)")
plt.title("Distribuição de Energia com Base na Frequência Angular Coerente")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# --- Output Terminal ---
print("\n--- Diagnóstico de Frequência Angular ---")
print(f"Frequência máxima estimada:     {float(np.max(frequencia_real)):.3e} Hz")
print(f"Frequência mínima estimada:     {float(np.min(frequencia_real)):.3e} Hz")
print(f"Energia máxima estimada:        {float(np.max(energia_local_real)):.4f} eV")
print(f"Energia mínima estimada:        {float(np.min(energia_local_real)):.4f} eV")

# === Bloco 12: Modelagem do Campo e do Meio (Éter Rotacional) ===

print("\n=== Modelagem do Campo e do Meio (Éter Rotacional) ===")

# Campo externo simulado: senoidal coerente, como uma onda eletromagnética que influencia a estrutura
campo_externo = np.sin(2 * np.pi * x / 50)

# Meio (éter rotacional): modulação espacial da densidade de coerência do substrato
meio_eter = np.exp(-((x - x.mean())**2) / (2 * (0.25 * x.max())**2))

# Simula a influência combinada (produto ponto a ponto) como modulação rotacional
psi_influenciado = psi_modulado * campo_externo * meio_eter

# Recalcula a densidade rotacional com a influência do meio e do campo
coerencia_influenciada = np.abs(psi_influenciado)**2
fase_influenciada = np.angle(psi_influenciado)

# Diagnóstico numérico
print("--- Diagnóstico do Campo e do Meio ---")
print(f"  • Campo máximo:              {float(np.max(campo_externo)):.4f}")
print(f"  • Campo mínimo:              {float(np.min(campo_externo)):.4f}")
print(f"  • Pico do meio (éter):       {float(np.max(meio_eter)):.4f}")
print(f"  • Mínimo do meio (éter):     {float(np.min(meio_eter)):.4f}")
print(f"  • Máxima coerência resultante: {float(np.max(coerencia_influenciada)):.4f}")
print(f"  • Fase média resultante:     {float(np.mean(fase_influenciada)):.4f} rad")

# === Visualização ===

plt.figure(figsize=(12, 6))

plt.subplot(3, 1, 1)
plt.plot(x, campo_externo, 'g-', label="Campo Externo (onda)")
plt.title("Campo Externo Coerente")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(x, meio_eter, 'c-', label="Meio (Éter Rotacional)")
plt.title("Distribuição do Meio Coerente (Éter)")
plt.ylabel("Densidade")
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(x, coerencia_influenciada, 'b-', label="|ψ(x)|² com Campo + Meio")
plt.title("Coerência Rotacional Resultante")
plt.xlabel("Espaço (x)")
plt.ylabel("|ψ|²")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
