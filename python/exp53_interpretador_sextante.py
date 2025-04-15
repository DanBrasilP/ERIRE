# exp53_interpretador_sextante.py

import csv
import math
import os
from pathlib import Path
import matplotlib.pyplot as plt

# Caminhos dos arquivos
BASE_DIR = Path(__file__).resolve().parent
EXTRATO_FILE = BASE_DIR / "genesis" / "sextante_extrato.csv"
FISICO_FILE = BASE_DIR / "genesis" / "sextante_fisico.csv"
INTERPRETACAO_FILE = BASE_DIR / "genesis" / "interpretacao_consolidada.csv"
FATORIAIS_FILE = BASE_DIR / "genesis" / "aproximacoes_fatoriais.csv"

def load_csv(file_path):
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except UnicodeDecodeError:
        with open(file_path, newline='', encoding='latin1') as f:  # ou 'cp1252' se preferir
            reader = csv.DictReader(f)
            return list(reader)

def is_close(a, b, tol=0.001):
    return abs(a - b) / max(abs(b), 1e-9) < tol

def match_factorial(value):
    for n in range(1, 100):
        f = math.factorial(n)
        if is_close(value, f):
            return n, f
    return None, None

def match_classical(value):
    known = {
        "pi": math.pi,
        "e": math.e,
        "phi": (1 + 5 ** 0.5) / 2,
        "ln(2)": math.log(2),
        "c": 299_792_458,
        "h": 6.62607015e-34,
        "G": 6.67430e-11
    }
    for name, const in known.items():
        if is_close(value, const):
            return name, const
    return None, None

def interpretar(extrato, fisico):
    registros = []
    fatoriais = []
    for linha in extrato:
        t = int(linha["t"])
        omega_norm = float(linha["norm"])
        id_ = linha["id"]
        dominio = fisico[t].get("interpretação", "desconhecido") if t < len(fisico) else "desconhecido"

        # Verifica factorial
        n, f = match_factorial(omega_norm)
        if n:
            fatoriais.append({
                "t": t, "id": id_, "dominio": dominio, "valor": omega_norm,
                "aproxima_fatorial": f, "n": n
            })

        # Verifica constantes físicas
        nome, valor = match_classical(omega_norm)
        if nome:
            registros.append({
                "t": t, "id": id_, "dominio": dominio,
                "valor": omega_norm, "constante": nome, "valor_teorico": valor
            })

    return registros, fatoriais

def salvar_csv(nome, dados, campos):
    with open(nome, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

def gerar_grafico_fatoriais(fatoriais):
    xs = [int(f["t"]) for f in fatoriais]
    ys = [float(f["valor"]) for f in fatoriais]
    ns = [int(f["n"]) for f in fatoriais]

    plt.figure(figsize=(10, 6))
    plt.scatter(xs, ys, c="blue", label="||Ω|| aproximando n!")
    for x, y, n in zip(xs, ys, ns):
        plt.annotate(f"{n}!", (x, y), fontsize=8)
    plt.title("Aproximações Fatoriais em ||Ω(t)||")
    plt.xlabel("t")
    plt.ylabel("||Ω||")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(BASE_DIR / "genesis" / "grafico_fatoriais.png")
    print("[GRÁFICO] Salvo: grafico_fatoriais.png")

def main():
    print("[INÍCIO] Interpretação complementar dos dados do sextante...")
    extrato = load_csv(EXTRATO_FILE)
    fisico = load_csv(FISICO_FILE)
    registros, fatoriais = interpretar(extrato, fisico)

    if registros:
        salvar_csv(INTERPRETACAO_FILE, registros, list(registros[0].keys()))
        print(f"[CSV] Constantes reconhecidas salvas em: {INTERPRETACAO_FILE.name}")

    if fatoriais:
        salvar_csv(FATORIAIS_FILE, fatoriais, list(fatoriais[0].keys()))
        print(f"[CSV] Aproximações fatoriais salvas em: {FATORIAIS_FILE.name}")
        gerar_grafico_fatoriais(fatoriais)

    print("[FIM] Interpretação concluída.")

if __name__ == "__main__":
    main()
