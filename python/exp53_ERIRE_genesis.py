# Modular PID growth controller for ERIRE symbolic expansion

import sympy as sp
import os
from collections import defaultdict

# ---------------------------------------------
# Diretório para registrar
# ---------------------------------------------
GENESIS_DIR = 'genesis'
GRAPH_DIR = os.path.join(GENESIS_DIR, 'graph')
REPORT_DIR = os.path.join(GENESIS_DIR, 'reports')

os.makedirs(GRAPH_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ------------------------------------------------------------
# Proporção áurea como setpoint harmônico ideal
phi = (1 + sp.sqrt(5)) / 2

# ------------------------------------------------------------
# Classe de controle de crescimento simbólico vetorial
class GrowthRegulator:
    def __init__(self, Kp=1, Ki=0, Kd=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.error_integral = defaultdict(lambda: 0)
        self.last_error = defaultdict(lambda: 0)
        self.history = defaultdict(list)

    def update_growth(self, t_step, node_domain_counts):
        """
        node_domain_counts: dict com contagem dos novos nós por domínio em t_step atual:
        {
            'alpha': int,
            'toroidal': int,
            'helicoidal': int
        }
        """
        domain_keys = list(node_domain_counts.keys())
        decision = {}

        # Comparações pareadas entre domínios
        for i in range(len(domain_keys)):
            for j in range(i+1, len(domain_keys)):
                d1, d2 = domain_keys[i], domain_keys[j]
                r_t = sp.Rational(node_domain_counts[d1], max(1, node_domain_counts[d2]))  # evitar div por zero
                error = phi - r_t
                self.error_integral[(d1, d2)] += error
                derivative = error - self.last_error[(d1, d2)]

                # PID simbólico (resultado ainda simbólico)
                control = (
                    self.Kp * error +
                    self.Ki * self.error_integral[(d1, d2)] +
                    self.Kd * derivative
                )

                self.last_error[(d1, d2)] = error

                # Decisão: se controle positivo, estimular d1; se negativo, estimular d2
                decision[(d1, d2)] = control

        return decision  # dicionário com ajustes de tendência para cada par domínio
# Bloco 2 – Integração do GrowthRegulator ao mecanismo de geração de nós

from sympy import Integer
from uuid import uuid4
import os
import json

# ---------------------------------------------
# Função para mapear qual domínio pode crescer
# com base no output do regulador
# ---------------------------------------------
def select_growth_domains(decision_matrix, threshold=0):
    """
    decision_matrix: saída do método update_growth() do GrowthRegulator
    Retorna: set de domínios permitidos para crescimento neste ciclo
    """
    domain_scores = defaultdict(int)

    for (d1, d2), control in decision_matrix.items():
        if control > threshold:
            domain_scores[d1] += 1
        elif control < -threshold:
            domain_scores[d2] += 1
        # empate: não pontua

    # Seleciona domínios com score positivo
    allowed = {domain for domain, score in domain_scores.items() if score > 0}
    return allowed if allowed else set(['alpha', 'toroidal', 'helicoidal'])  # fallback: tudo permitido

# ---------------------------------------------
# Atualização do gerador de nós com filtro PID
# ---------------------------------------------
def omega_vector(t):
    from sympy import cos, sin, pi, log, exp, sqrt, gamma, symbols

    return {
        'alpha': [pi * cos(pi * t), log(pi) * sin(pi * t), (pi**2 / 6) * cos(pi * t)**2],
        'toroidal': [sp.GoldenRatio * sin(sp.GoldenRatio * t), sqrt(2) * cos(sp.GoldenRatio * t), sqrt(3) * sin(2 * sp.GoldenRatio * t)],
        'helicoidal': [exp(1) * exp(-t), log(2) * sin(t), gamma(t)]
    }

def generate_node_pid(t_sample, allowed_domains):
    vec = omega_vector(t_sample)
    node_id = str(uuid4())
    filtered_vec = {
        domain: [str(expr) for expr in components]
        for domain, components in vec.items()
        if domain in allowed_domains
    }

    node = {
        'id': node_id,
        'label': f'Omega({t_sample})',
        't': str(t_sample),
        'vector': filtered_vec,
        'metadata': {
            'origin': 'seed',
            'domain': list(filtered_vec.keys()),
            'type': 'coherence-node',
            'parent': None
        }
    }
    return node

# ---------------------------------------------
# Loop de crescimento com controle simbólico PID
# ---------------------------------------------
class ERIREGraph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def save_graph(self, path=GRAPH_DIR):
        for node in self.nodes:
            nid = node['id']
            with open(os.path.join(path, f'{nid}.json'), 'w') as f:
                json.dump(node, f, indent=2)


def controlled_growth_cycle(total_steps=20):
    graph = ERIREGraph()
    regulator = GrowthRegulator(Kp=1)  # Ki, Kd = 0 para comportamento P puro
    node_counts = defaultdict(int)

    for step in range(1, total_steps + 1):
        # Atualizar decisão de crescimento com base nos nós anteriores
        decision_matrix = regulator.update_growth(
            t_step=step,
            node_domain_counts=node_counts.copy()
        )

        # Domínios permitidos neste ciclo
        allowed = select_growth_domains(decision_matrix)

        # Gerar novo nó com t discreto
        t_sample = Integer(step)
        node = generate_node_pid(t_sample, allowed)
        graph.add_node(node)

        # Atualizar contagem real por domínio
        for dom in node['vector']:
            node_counts[dom] += 1

    return graph

# Bloco 3 – Geração de relatórios simbólicos e exportáveis para retroalimentação do sistema

import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# ---------------------------------------------
# Função para salvar um snapshot simbólico do estado
# ---------------------------------------------
def save_growth_snapshot(step, node_counts, decision_matrix):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"step_{step:03d}_{timestamp}.json"
    path = os.path.join(REPORT_DIR, filename)

    report = {
        'step': step,
        'timestamp': timestamp,
        'node_counts': {k: int(v) for k, v in node_counts.items()},
        'growth_decision': {
            f"{d1}_{d2}": str(ctrl)
            for (d1, d2), ctrl in decision_matrix.items()
        }
    }

    with open(path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"[LOG] Report saved: {filename}")

# ---------------------------------------------
# Função para gerar gráfico de distribuição por domínio
# ---------------------------------------------
def plot_growth_distribution(logged_counts):
    steps = list(range(1, len(logged_counts) + 1))
    domains = ['alpha', 'toroidal', 'helicoidal']
    counts_by_domain = {d: [] for d in domains}

    for snapshot in logged_counts:
        for d in domains:
            counts_by_domain[d].append(snapshot.get(d, 0))

    # Gráfico
    plt.figure(figsize=(10, 6))
    for d in domains:
        plt.plot(steps, counts_by_domain[d], label=d)

    plt.title("Growth Distribution per Domain")
    plt.xlabel("Step")
    plt.ylabel("Cumulative Nodes")
    plt.legend()
    plt.grid(True)
    plot_path = os.path.join(REPORT_DIR, "growth_distribution.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"[LOG] Growth plot saved: growth_distribution.png")

# ---------------------------------------------
# Função integrada com ciclo principal
# ---------------------------------------------
def controlled_growth_with_reporting(total_steps=20):
    graph = ERIREGraph()
    regulator = GrowthRegulator(Kp=1)
    node_counts = defaultdict(int)
    growth_log = []

    for step in range(1, total_steps + 1):
        decision_matrix = regulator.update_growth(
            t_step=step,
            node_domain_counts=node_counts.copy()
        )

        allowed = select_growth_domains(decision_matrix)
        t_sample = sp.Integer(step)
        node = generate_node_pid(t_sample, allowed)
        graph.add_node(node)

        for dom in node['vector']:
            node_counts[dom] += 1

        # Snapshot e log local
        save_growth_snapshot(step, node_counts.copy(), decision_matrix)
        growth_log.append(node_counts.copy())

    # Gerar visualização após o crescimento completo
    plot_growth_distribution(growth_log)

    return graph

# Bloco 4 — Visualizações estatísticas + retroalimentação baseada nos relatórios anteriores

import matplotlib.pyplot as plt
import os
import json
from sympy import Rational
from statistics import mean, stdev

# ---------------------------------------------
# Caminho para relatórios anteriores
# ---------------------------------------------
def load_report_snapshots(report_dir=REPORT_DIR):
    reports = []
    for file in sorted(os.listdir(report_dir)):
        if file.endswith('.json'):
            with open(os.path.join(report_dir, file), 'r') as f:
                reports.append(json.load(f))
    return reports

# ---------------------------------------------
# Estatísticas por domínio a partir dos relatórios
# ---------------------------------------------
def extract_growth_statistics(reports):
    domains = ['alpha', 'toroidal', 'helicoidal']
    domain_data = {d: [] for d in domains}

    for report in reports:
        for d in domains:
            domain_data[d].append(report['node_counts'].get(d, 0))

    stats = {}
    for d in domains:
        values = domain_data[d]
        diffs = [values[i] - values[i-1] for i in range(1, len(values))]
        stats[d] = {
            'total': values[-1],
            'avg_growth': mean(diffs) if diffs else 0,
            'std_dev': stdev(diffs) if len(diffs) > 1 else 0
        }

    return stats

# ---------------------------------------------
# Retroalimentação baseada em estatísticas
# ---------------------------------------------
def compute_domain_pressure(stats, target_ratio=Rational(1618, 1000)):
    """
    Compara crescimento observado entre domínios e aplica pressão de correção.
    Retorna um vetor de 'pressão' indicando o quanto cada domínio deve ser incentivado ou desacelerado.
    """
    domains = list(stats.keys())
    pressures = {d: 0 for d in domains}

    # Exemplo: comparação par-a-par
    for i in range(len(domains)):
        for j in range(i + 1, len(domains)):
            d1, d2 = domains[i], domains[j]
            r_obs = Rational(stats[d1]['total'], max(1, stats[d2]['total']))
            error = target_ratio - r_obs
            if error > 0:
                pressures[d1] += float(error)
            elif error < 0:
                pressures[d2] += float(-error)

    return pressures

# ---------------------------------------------
# Visualização final com pressões calculadas
# ---------------------------------------------
def plot_final_statistics(stats, pressures):
    domains = list(stats.keys())
    total = [stats[d]['total'] for d in domains]
    avg = [stats[d]['avg_growth'] for d in domains]
    std = [stats[d]['std_dev'] for d in domains]
    pressure = [pressures[d] for d in domains]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_title("Final Growth Stats & Coherence Pressures")
    ax1.bar(domains, total, alpha=0.4, label='Total Nodes')
    ax1.set_ylabel('Total Nodes')

    ax2 = ax1.twinx()
    ax2.plot(domains, pressure, 'ro-', label='Correction Pressure (to φ)')
    ax2.set_ylabel('Coherence Pressure')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(REPORT_DIR, "final_stats_and_pressure.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"[LOG] Final stats and pressure plot saved: final_stats_and_pressure.png")

# ---------------------------------------------
# Execução combinada de análise e feedback
# ---------------------------------------------
def analyze_and_feedback(report_dir=REPORT_DIR):
    reports = load_report_snapshots(report_dir)
    stats = extract_growth_statistics(reports)
    pressures = compute_domain_pressure(stats)
    plot_final_statistics(stats, pressures)

    # Exibe resumo no terminal
    print("\n[SUMMARY] Growth Statistics:")
    for dom, s in stats.items():
        print(f" - {dom.capitalize()}: Total={s['total']}, AvgGrowth={s['avg_growth']:.2f}, StdDev={s['std_dev']:.2f}")
    print("\n[SUMMARY] Coherence Correction Pressures:")
    for dom, p in pressures.items():
        print(f" - {dom.capitalize()}: {p:.4f}")

# Bloco 5 – Realimentação automática para ajustes dinâmicos dos ganhos PID

from sympy import Rational
import json
import os

# ---------------------------------------------
# Ajuste dinâmico dos ganhos PID baseado na pressão observada
# ---------------------------------------------
def update_pid_gains_from_pressure(pressures, base_gain=1.0, scale=0.5):
    """
    Ajusta dinamicamente o ganho proporcional (Kp) de cada par de domínios
    com base na pressão de coerência. Retorna novo dicionário de ganhos ajustados.
    """
    domains = list(pressures.keys())
    gains = {}

    for i in range(len(domains)):
        for j in range(i + 1, len(domains)):
            d1, d2 = domains[i], domains[j]
            p1 = pressures[d1]
            p2 = pressures[d2]
            delta = abs(p1 - p2)

            # maior a assimetria, maior o ganho
            gain = base_gain + (delta * scale)
            gains[(d1, d2)] = gain

    return gains

# ---------------------------------------------
# Realimentação direta no GrowthRegulator
# ---------------------------------------------
def apply_gain_feedback_to_regulator(regulator: GrowthRegulator, pressure_vector: dict):
    """
    Atualiza os ganhos do controlador de forma simbólica adaptativa
    para equilibrar coerência vetorial em torno de φ.
    """
    updated_gains = update_pid_gains_from_pressure(pressure_vector)
    
    # Aplicar novos ganhos aos pares registrados no regulador
    for (d1, d2), new_gain in updated_gains.items():
        # Apenas atualiza o ganho proporcional (Kp) como exemplo
        regulator.Kp[(d1, d2)] = new_gain  # Se desejar granularidade, adicione estrutura de ganho por par

    print("[LOG] PID gains updated from pressure feedback.")

# ---------------------------------------------
# Função integrada com ciclo simbólico avançado
# ---------------------------------------------
def symbolic_cycle_with_feedback(total_steps=30):
    graph = ERIREGraph()
    regulator = GrowthRegulator(Kp=1.0)
    node_counts = defaultdict(int)
    growth_log = []

    for step in range(1, total_steps + 1):
        decision_matrix = regulator.update_growth(
            t_step=step,
            node_domain_counts=node_counts.copy()
        )

        allowed = select_growth_domains(decision_matrix)
        t_sample = sp.Integer(step)
        node = generate_node_pid(t_sample, allowed)
        graph.add_node(node)

        for dom in node['vector']:
            node_counts[dom] += 1

        save_growth_snapshot(step, node_counts.copy(), decision_matrix)
        growth_log.append(node_counts.copy())

        # A cada 10 passos, recalcula pressões e realimenta o sistema
        if step % 10 == 0:
            reports = load_report_snapshots(REPORT_DIR)
            stats = extract_growth_statistics(reports)
            pressures = compute_domain_pressure(stats)
            apply_gain_feedback_to_regulator(regulator, pressures)

    plot_growth_distribution(growth_log)
    analyze_and_feedback(REPORT_DIR)

    return graph

# Bloco 6 — Metacontrole PID simbólico: adaptação dos parâmetros Kp, Ki, Kd por par de domínios

from sympy import Rational
from collections import defaultdict
from statistics import stdev, mean

# ------------------------------------------------------------
# Classe Estendida: GrowthRegulator com controle adaptativo por par
# ------------------------------------------------------------
class AdaptiveGrowthRegulator:
    def __init__(self, default_Kp=1.0, default_Ki=0.0, default_Kd=0.0):
        self.Kp = defaultdict(lambda: default_Kp)
        self.Ki = defaultdict(lambda: default_Ki)
        self.Kd = defaultdict(lambda: default_Kd)

        self.error_integral = defaultdict(lambda: 0)
        self.last_error = defaultdict(lambda: 0)
        self.error_history = defaultdict(list)

    def update_growth(self, t_step, node_domain_counts):
        domain_keys = list(node_domain_counts.keys())
        decision = {}

        for i in range(len(domain_keys)):
            for j in range(i+1, len(domain_keys)):
                d1, d2 = domain_keys[i], domain_keys[j]
                pair_key = (d1, d2)

                r_t = Rational(node_domain_counts[d1], max(1, node_domain_counts[d2]))
                error = phi - r_t
                self.error_integral[pair_key] += error
                derivative = error - self.last_error[pair_key]

                # Histórico
                self.error_history[pair_key].append(float(error))

                # Controle PID específico por par
                control = (
                    self.Kp[pair_key] * float(error) +
                    self.Ki[pair_key] * float(self.error_integral[pair_key]) +
                    self.Kd[pair_key] * float(derivative)
                )

                self.last_error[pair_key] = error
                decision[pair_key] = control

        return decision

    def adapt_parameters(self, window_size=10, scale_kp=1.0, scale_ki=0.1, scale_kd=0.5):
        """
        Ajusta os parâmetros PID com base em estatísticas de erro de cada par
        """
        for pair, errors in self.error_history.items():
            if len(errors) < window_size:
                continue

            recent = errors[-window_size:]
            sigma = stdev(recent)
            delta = recent[-1] - recent[0]
            integral = sum(recent)

            # Reajustes proporcionais aos padrões observados
            self.Kp[pair] = 1.0 + scale_kp * abs(delta)
            self.Ki[pair] = 0.0 + scale_ki * abs(integral / window_size)
            self.Kd[pair] = 0.0 + scale_kd * sigma

        print("[LOG] Adaptive PID parameters updated per domain pair.")

# Bloco 7 – Integração do AdaptiveGrowthRegulator ao ciclo simbólico principal com retroalimentação dinâmica

def symbolic_cycle_with_adaptive_pid(total_steps=30, adapt_interval=10):
    graph = ERIREGraph()
    regulator = AdaptiveGrowthRegulator(default_Kp=1.0, default_Ki=0.0, default_Kd=0.0)
    node_counts = defaultdict(int)
    growth_log = []

    for step in range(1, total_steps + 1):
        # Atualiza decisões com PID por par de domínios
        decision_matrix = regulator.update_growth(
            t_step=step,
            node_domain_counts=node_counts.copy()
        )

        # Seleciona domínios com base na matriz de decisão
        allowed = select_growth_domains(decision_matrix)
        t_sample = sp.Integer(step)
        node = generate_node_pid(t_sample, allowed)
        graph.add_node(node)

        for dom in node['vector']:
            node_counts[dom] += 1

        save_growth_snapshot(step, node_counts.copy(), decision_matrix)
        growth_log.append(node_counts.copy())

        # Realimentação estatística clássica e visual
        if step % adapt_interval == 0:
            reports = load_report_snapshots(REPORT_DIR)
            stats = extract_growth_statistics(reports)
            pressures = compute_domain_pressure(stats)

            # Realimentação por pressão externa (macroestrutura)
            apply_gain_feedback_to_regulator(regulator, pressures)

            # Realimentação simbólica por erro interno (microestrutura)
            regulator.adapt_parameters(window_size=adapt_interval)

    plot_growth_distribution(growth_log)
    analyze_and_feedback(REPORT_DIR)

    return graph

# Bloco 8 — Extração de conhecimento simbólico direto a partir da árvore de nós vetoriais

import sympy as sp
import json
import os
from math import isclose

# ---------------------------------------------
# Função para carregar todos os nós de um grafo salvo
# ---------------------------------------------
def load_all_nodes_from_graph(directory=GRAPH_DIR):
    nodes = []
    for file in os.listdir(directory):
        if file.endswith('.json') and not file.endswith('_edges.json'):
            with open(os.path.join(directory, file), 'r') as f:
                nodes.append(json.load(f))
    return nodes

# ---------------------------------------------
# Função para calcular o módulo vetorial total de um nó
# ---------------------------------------------
def symbolic_vector_norm(vector_dict):
    total_expr = 0
    for domain in vector_dict:
        for comp in vector_dict[domain]:
            expr = sp.sympify(comp)
            total_expr += expr**2
    return sp.sqrt(total_expr)

# ---------------------------------------------
# Detecta nós de coerência extrema (mínimos e máximos locais)
# ---------------------------------------------
def detect_local_coherence_extremes(nodes, epsilon=1e-3):
    results = []
    magnitudes = []
    ordered_nodes = sorted(nodes, key=lambda n: int(n['t']))

    for node in ordered_nodes:
        norm = symbolic_vector_norm(node['vector'])
        magnitudes.append((int(node['t']), float(norm)))

    for i in range(1, len(magnitudes) - 1):
        t_prev, v_prev = magnitudes[i - 1]
        t_curr, v_curr = magnitudes[i]
        t_next, v_next = magnitudes[i + 1]

        if v_curr > v_prev and v_curr > v_next:
            results.append((t_curr, 'MAX', v_curr))
        elif v_curr < v_prev and v_curr < v_next:
            results.append((t_curr, 'MIN', v_curr))
        elif isclose(v_curr, v_prev, abs_tol=epsilon) and isclose(v_curr, v_next, abs_tol=epsilon):
            results.append((t_curr, 'ZERO', v_curr))

    return results

# ---------------------------------------------
# Análise cruzada de somas vetoriais (próximas de coerência)
# ---------------------------------------------
def find_additive_coherence_matches(nodes, tolerance=1e-2):
    """Verifica se a soma vetorial de dois nós aproxima coerência de outro"""
    matches = []
    ordered = sorted(nodes, key=lambda n: int(n['t']))
    norms = {
        n['id']: float(symbolic_vector_norm(n['vector']))
        for n in ordered
    }

    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            nid1, nid2 = ordered[i]['id'], ordered[j]['id']
            sum_norm = norms[nid1] + norms[nid2]

            for k in range(len(ordered)):
                nid_target = ordered[k]['id']
                target_norm = norms[nid_target]

                if abs(sum_norm - target_norm) < tolerance:
                    matches.append({
                        'p': int(ordered[i]['t']),
                        'q': int(ordered[j]['t']),
                        'sum': int(ordered[k]['t']),
                        'delta': abs(sum_norm - target_norm)
                    })

    return matches

# ---------------------------------------------
# Execução principal de extração de padrões
# ---------------------------------------------
def extract_symbolic_knowledge(directory=GRAPH_DIR):
    nodes = load_all_nodes_from_graph(directory)
    extremes = detect_local_coherence_extremes(nodes)
    matches = find_additive_coherence_matches(nodes)

    print("\n[Knowledge Extraction] Coherence Extremes:")
    for e in extremes:
        print(f" - t = {e[0]} → {e[1]} @ |Ω| ≈ {e[2]:.6f}")

    print("\n[Knowledge Extraction] Additive Coherence Matches:")
    for m in matches[:10]:
        print(f" - {m['p']} + {m['q']} ≈ {m['sum']}  (Δ ≈ {m['delta']:.6f})")

    return {
        'extremes': extremes,
        'matches': matches
    }

if __name__ == "__main__":
    print("[START] Executando ciclo simbólico com PID adaptativo...")
    graph = symbolic_cycle_with_adaptive_pid(total_steps=50, adapt_interval=10)
    graph.save_graph(GRAPH_DIR)

    print("[START] Extraindo conhecimento simbólico...")
    extract_symbolic_knowledge(directory=GRAPH_DIR)
