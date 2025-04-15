# exp53_sextante_genesis.py

import os
import json
import math
import csv
from sympy import sympify, evalf

# === Diretório de entrada ===
GRAPH_DIR = os.path.join('genesis', 'graph')

# === Constantes conhecidas para comparação ===
PHYSICAL_CONSTANTS = {
    'pi': math.pi,
    'e': math.e,
    'phi': (1 + math.sqrt(5)) / 2,
    'ln2': math.log(2),
    'planck_h': 6.62607015e-34,
    'c_light': 299792458,
    'avogadro': 6.02214076e23,
    'fine_structure': 1 / 137.035999,
    'electron_mass': 9.10938356e-31,
    'proton_mass': 1.6726219e-27
}

# === Carrega os nós do grafo JSON ===
def load_all_nodes(directory=GRAPH_DIR):
    nodes = []
    for file in os.listdir(directory):
        if file.endswith('.json'):
            with open(os.path.join(directory, file), 'r') as f:
                try:
                    node = json.load(f)
                    nodes.append(node)
                except Exception as e:
                    print(f"[ERRO] Falha ao ler {file}: {e}")
    return nodes

# === Converte vetor simbólico em valores reais e calcula norma ===
def extract_real_vectors(nodes, max_nodes=50):
    data = []
    for node in nodes:
        if len(data) >= max_nodes:
            break
        row = {'t': int(node['t']), 'id': node['id'], 'vector': [], 'norm': 0.0}
        norm_sq = 0.0
        for domain, comps in node['vector'].items():
            for comp in comps:
                try:
                    val = float(sympify(comp).evalf())
                    norm_sq += val**2
                    row['vector'].append((domain, comp, val))
                except:
                    continue
        row['norm'] = math.sqrt(norm_sq)
        data.append(row)
    return data

# === Verifica aproximações com constantes conhecidas ===
def check_constant_matches(data, tolerance=0.01):
    matches = []
    for row in data:
        for domain, expr, val in row['vector']:
            for cname, cval in PHYSICAL_CONSTANTS.items():
                if abs(val - cval) / cval < tolerance:
                    matches.append({
                        't': row['t'],
                        'id': row['id'],
                        'domain': domain,
                        'expr': expr,
                        'value': val,
                        'const': cname,
                        'ref': cval
                    })
    return matches

# === Exporta dados como CSV (opcional) ===
def save_csv(data, path='genesis/sextante_extrato.csv'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t', 'id', 'domain', 'expr', 'value', 'norm'])
        for row in data:
            for domain, expr, val in row['vector']:
                writer.writerow([row['t'], row['id'], domain, expr, val, row['norm']])

# === Bloco Adicional — Interpretação Física das Normas Vetoriais ===

def interpret_vector_norms_physically(data, save_path='genesis/sextante_fisico.csv'):
    """
    Associa as normas vetoriais com leis físicas conhecidas,
    como aproximações a factorials (n!), E=mc^2, F=ma, etc.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    physical_insights = []

    for row in data:
        norm = row['norm']
        t = row['t']
        label = ''
        m_close = round(norm / PHYSICAL_CONSTANTS['c_light']**2)
        if abs(norm - m_close * PHYSICAL_CONSTANTS['c_light']**2) / norm < 0.01:
            label = f"E=mc² ~ m={m_close}"

        f_approx = round(norm / t) if t > 0 else 0
        if abs(norm - f_approx * t) / norm < 0.01:
            label = f"F=ma ~ a={f_approx}"

        # Verifica proximidade com fatorial
        try:
            for n in range(1, 50):
                if abs(norm - math.factorial(n)) / norm < 0.01:
                    label = f"n! ~ n={n}"
                    break
        except:
            pass

        if label:
            physical_insights.append({
                't': t,
                'id': row['id'],
                'norm': norm,
                'label': label
            })

    # Salva CSV
    with open(save_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t', 'id', 'norm', 'interpretação'])
        for entry in physical_insights:
            writer.writerow([entry['t'], entry['id'], entry['norm'], entry['label']])

    print("\n[INTERPRETAÇÃO] Correlações com fórmulas físicas clássicas:")
    for entry in physical_insights:
        print(f"t={entry['t']:2d} | ID={entry['id']} | ||Ω|| ≈ {entry['norm']:.6f} → {entry['label']}")

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    print("[INÍCIO] Extração de vetores reais e comparação com constantes...")
    nodes = load_all_nodes()
    extratos = extract_real_vectors(nodes)
    save_csv(extratos)

    print(f"[INFO] {len(extratos)} nós processados.")

    print("\n[RESULTADO] Normas vetoriais:")
    for r in extratos:
        print(f"t={r['t']:2d} | ID={r['id']} | ||Ω|| ≈ {r['norm']:.6f}")

    print("\n[BUSCA] Aproximações com constantes conhecidas:")
    matches = check_constant_matches(extratos)
    if not matches:
        print("Nenhuma correspondência detectada dentro da tolerância.")
    for m in matches:
        print(f"t={m['t']:2d} | ID={m['id']} | {m['domain']} | {m['expr']} ≈ {m['const']} ({m['value']:.6f} ≈ {m['ref']})")
    
    interpret_vector_norms_physically(extratos)