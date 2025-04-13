import numpy as np
import math

# Parâmetros globais
EPSILON = 1e-6

# Função de rotação helicoidal coerencial em planos (0,1) e (2,3)
def tau(v, phi=0.0):
    rot_matrix = np.array([
        [np.cos(phi), -np.sin(phi), 0, 0],
        [np.sin(phi),  np.cos(phi), 0, 0],
        [0, 0, np.cos(phi), -np.sin(phi)],
        [0, 0, np.sin(phi),  np.cos(phi)],
    ])
    return np.dot(rot_matrix, v)

# Geração da mensagem vetorial
def gerar_mensagem(a, b, c, d):
    return np.array([a, b, c, d], dtype=float)

# Chave privada e fase
def gerar_chave_privada():
    chave = np.random.randn(4)
    fase = np.random.uniform(0, 2 * math.pi)
    return chave, fase

# Geração de chave pública (sem fase, usada apenas para referência)
def gerar_chave_publica(chave_privada):
    return tau(chave_privada, 0.0)

# Cifragem: msg × chave_privada → rotação τ com fase
def encriptar(msg, chave_priv, phi):
    produto = np.multiply(msg, chave_priv)
    return tau(produto, phi)

# Decriptografia com inversão angular e divisão por chave
def decriptar(cifra, chave_priv, phi):
    vetor_invertido = tau(cifra, -phi)  # rotação inversa
    return np.divide(vetor_invertido, chave_priv)

# Verificação de coerência vetorial absoluta
def verificar_coerencia(v1, v2):
    return np.linalg.norm(v1 - v2) < EPSILON

# === Execução do experimento ===
msg = gerar_mensagem(1.2, -0.8, 0.4, 0.9)
chave_priv, fase_correta = gerar_chave_privada()
chave_pub = gerar_chave_publica(chave_priv)

# Criptografar com fase correta
cifra = encriptar(msg, chave_priv, fase_correta)

# Decriptar com fase correta
recuperada = decriptar(cifra, chave_priv, fase_correta)

# Mostrar resultados
print("\n--- Experimento ERIЯƎ-Crypto 01 — Versão Final Corrigida ---")
print(f"Mensagem original:     {msg}")
print(f"Chave privada:         {chave_priv}")
print(f"Chave pública (τ):     {chave_pub}")
print(f"Fase aplicada:         {fase_correta:.4f} rad")
print(f"Mensagem cifrada:      {cifra}")
print(f"Mensagem decriptada:   {recuperada}")
print(f"Coerência mantida?     {verificar_coerencia(msg, recuperada)}")

# Tentativa com fase incorreta
fase_falsa = fase_correta + 0.1
recuperada_falsa = decriptar(cifra, chave_priv, fase_falsa)

print(f"\nTentativa com fase incorreta (+0.1 rad):")
print(f"Resultado:             {recuperada_falsa}")
print(f"Coerência mantida?     {verificar_coerencia(msg, recuperada_falsa)}")
