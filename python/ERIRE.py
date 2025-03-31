import numpy as np
import sympy as sp
import mpmath as mp
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

mp.mp.dps = 50 # Aumenta a precisão para 50 dígitos

class ERIRE:
    """
    Classe que implementa a Teoria ERIRE, suportando cálculos simbólicos e numéricos com 
    precisão arbitrária para logaritmos e exponenciação, utilizando mpmath para operações
    de alta precisão em casos críticos.
    """

    def __init__(self, z, m=1, n=1, plane='i', symbolic=False):
        self.symbolic = symbolic
        self.z = self.convert_to_complex(z)
        self.m = m
        self.n = n
        self.plane = plane.lower()
        if not self.symbolic:
            self.z = self.ensure_high_precision(self.z)
        self.small_threshold = mp.mpf('1e-5')      # Limite inferior para normalização
        self.large_threshold = mp.mpf('1e5')         # Limite superior para normalização
        self.normalization_scale = mp.mpf('1e5')       # Fator usado para reescala

    def convert_to_complex(self, z):
        if self.symbolic:
            if isinstance(z, (int, float, complex)):
                return sp.S(z)
            elif isinstance(z, (tuple, list, np.ndarray)) and len(z) >= 2:
                return sp.S(z[0]) + sp.I * sp.S(z[1])
            elif isinstance(z, sp.Basic):
                return z
            else:
                raise ValueError("Formato inválido para modo simbólico.")
        else:
            if isinstance(z, (int, float)):
                # Garante a conversão para complex, inclusive para reais negativos
                return complex(z, 0)
            elif isinstance(z, complex):
                return z
            elif isinstance(z, (tuple, list, np.ndarray)) and len(z) >= 2:
                return complex(z[0], z[1])
            else:
                raise ValueError("Formato inválido.")

    def convert_mpc_to_complex(z):
        """Converte um número complexo da mpmath para um número complexo nativo do Python."""
        return complex(z.real, z.imag) if isinstance(z, mp.mpc) else z

    def ensure_high_precision(self, z):
        """
        Garante precisão máxima para valores pequenos, convertendo z para um mpmath.mpc.
        """
        if isinstance(z, complex):
            return mp.mpc(z.real, z.imag)
        return z

    def normalize_input(self, z):
        """
        Normaliza z corretamente com ajuste explícito após cálculo.
        """
        r = mp.fabs(z)
        adjust = mp.mpc(0)
        if r < self.small_threshold:
            F = self.normalization_scale
            z_norm = z * F
            adjust = mp.log(F)
        elif r > self.large_threshold:
            F = self.normalization_scale
            z_norm = z / F
            adjust = -mp.log(F)
        else:
            z_norm = z
        return z_norm, adjust

    def fixed_log(self, z):
        """
        Ajusta explicitamente o ramo principal e desfaz normalização corretamente.
        """
        if self.symbolic:
            return sp.log(z, evaluate=False).rewrite(sp.log).expand(complex=True).simplify()
        else:
            z_stable = self.ensure_high_precision(z)
            if abs(z_stable) < 1e-30:
                raise ValueError("Logaritmo indefinido para valor próximo de zero.")
            z_norm, adjust = self.normalize_input(z_stable)
            modulus = mp.fabs(z_norm)
            angle = mp.arg(z_norm)
            return (mp.log(modulus) + mp.mpc(0, angle)) - adjust

    def eire(self):
        """
        Aplica a operação EIRE garantindo que a entrada não seja zero.
        """
        if self.z == 0:
            raise ValueError("Operação EIRE indefinida para z = 0.")
        try:
            z_stable = self.ensure_high_precision(self.z)
            if abs(z_stable) < 1e-30:
                raise ValueError("EIRE: Entrada muito próxima de zero.")
            if self.symbolic:
                return sp.simplify(sp.exp(sp.I * self.m * sp.log(z_stable)))
            return mp.exp(self.m * mp.mpc(0, 1) * self.fixed_log(z_stable))
        except Exception as e:
            print("Erro em eire:", e)
            return None

    def rire(self):
        """
        Aplica a operação RIRE garantindo que a entrada não seja zero.
        """
        if self.z == 0:
            raise ValueError("Operação RIRE indefinida para z = 0.")
        z_stable = self.ensure_high_precision(self.z)
        if self.symbolic:
            return sp.simplify(sp.exp(sp.log(z_stable) / (self.n * sp.I)))
        return mp.exp(mp.log(z_stable) / (self.n * mp.mpc(0,1)))

    def erire_combined(self):
        """
        Calcula RIRE(EIRE(z, m), n) com precisão máxima.
        Garante que a simetria só é exata quando m = n.
        """
        if self.m != self.n:
            raise ValueError(f"Para garantir a simetria perfeita, é necessário que m = n. Recebido: m={self.m}, n={self.n}")
        eire_result = self.eire()
        if eire_result is None:
            print("Erro em erire_combined: eire retornou None devido a entrada inadequada.")
            return None
        if self.symbolic:
            return sp.simplify(sp.exp(sp.log(eire_result) / (self.n * sp.I)))
        return mp.exp(self.fixed_log(eire_result) / (self.n * mp.mpc(0, 1)))

    def sqrt_i(self):
        """
        Calcula a raiz imaginária z^(1/i) com precisão máxima,
        utilizando o logaritmo fixo para garantir consistência.
        """
        z_stable = self.ensure_high_precision(self.z)
        if self.symbolic:
            return sp.simplify(sp.exp(-sp.I * sp.log(z_stable)))
        return mp.exp(-mp.mpc(0,1) * mp.log(z_stable))

    def hypercomplex_transform(self, vector):
        """
        Aplica uma rotação hipercomplexa em um vetor 3D com precisão.
        Assegura que o eixo de rotação seja normalizado e converte o vetor para np.float64.
        """
        if len(vector) != 3:
            raise ValueError("Vetor deve ser 3D.")
        axis = np.array({'i': [1, 0, 0], 'j': [0, 1, 0], 'k': [0, 0, 1]}[self.plane], dtype=np.float64)
        axis /= np.linalg.norm(axis)
        # Converte self.z (mpmath.mpc) para Python complex para usar np.angle
        angle = np.angle(complex(self.z)) * self.m
        quaternion = R.from_rotvec(angle * axis)
        return quaternion.apply(np.array(vector, dtype=np.float64))

    def rotation_matrix(self, dim, theta, plane=(0, 1)):
        """
        Gera uma matriz de rotação para um plano específico.
        """
        matrix = np.eye(dim, dtype=np.float64)
        i, j = plane
        matrix[i, i] = np.cos(theta)
        matrix[i, j] = -np.sin(theta)
        matrix[j, i] = np.sin(theta)
        matrix[j, j] = np.cos(theta)
        return matrix

    def erire_transform(self, f, w, t_range=(-10, 10)):
        """
        Computa corretamente a Transformada ERIRE usando mpmath.quad().
        """
        integral = mp.quad(lambda t: f(t) * mp.exp(-mp.fabs(self.m) * t) * mp.exp(1j * w * t),
                        [t_range[0], t_range[1]])
        return integral

    def apply_quantum_gate(self, qc, qubit):
        """
        Aplica uma porta lógica baseada em EIRE em um circuito quântico.
        """
        qc.p(np.pi * self.m, qubit)

    def rotate_point(self, x, y):
        """
        Aplica rotação ERIRE a um ponto no plano 2D.
        """
        z_val = complex(x, y)
        z_rot = self.eire()
        return z_rot.real, z_rot.imag

    def visualize_complex(self):
        """
        Visualiza a transformação no plano complexo.
        Converte os valores para float para compatibilidade com matplotlib.
        """
        original = self.z
        transformed = self.eire()
        plt.figure(figsize=(6, 6))
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True, linestyle='--', linewidth=0.5)
        plt.scatter([float(original.real)], [float(original.imag)], color='red', label='Original')
        plt.scatter([float(transformed.real)], [float(transformed.imag)], color='blue', label='Transformado')
        plt.plot([0, float(original.real)], [0, float(original.imag)], 'r--')
        plt.plot([0, float(transformed.real)], [0, float(transformed.imag)], 'b--')
        plt.xlabel("Re")
        plt.ylabel("Im")
        plt.legend()
        plt.title("Transformação ERIRE no Plano Complexo")
        plt.show()

    def visualize_hypercomplex(self, vector=None):
        """
        Visualiza a transformação hipercomplexa em 3D.
        """
        if vector is None:
            vector = np.array([self.z.real, self.z.imag, 0], dtype=np.float64)
        elif len(vector) != 3:
            raise ValueError("Vetor deve ser 3D.")
        transformed = self.hypercomplex_transform(vector)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(vector[0], vector[1], vector[2], color='red', label='Original')
        ax.scatter(transformed[0], transformed[1], transformed[2], color='blue', label='Transformado')
        ax.plot([0, vector[0]], [0, vector[1]], [0, vector[2]], 'r--')
        ax.plot([0, transformed[0]], [0, transformed[1]], [0, transformed[2]], 'b--')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Transformação Hipercomplexa ERIRE")
        ax.legend()
        plt.show()

    def quaternion_exp(self, q):
        """
        Calcula a exponencial de um quaternion q.
        """
        a, v1, v2, v3 = q
        norm_v = mp.sqrt(v1**2 + v2**2 + v3**2)

        if norm_v == 0:
            return [mp.exp(a), 0, 0, 0]

        exp_a = mp.exp(a)
        v_unit = [v1 / norm_v, v2 / norm_v, v3 / norm_v]
        sin_term = mp.sin(norm_v) * mp.mpc(v_unit[0], 0) + mp.mpc(0, 1) * mp.sin(norm_v) * (v_unit[1] + v_unit[2])

        return [exp_a * mp.cos(norm_v), exp_a * sin_term.real, exp_a * sin_term.imag, exp_a * sin_term.imag]

    def quaternion_ln(self, q):
        """
        Calcula o logaritmo natural de um quaternion q.
        """
        norm_q = mp.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
        v = [q[1], q[2], q[3]]
        norm_v = mp.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

        if norm_v == 0:
            return [mp.ln(norm_q), 0, 0, 0]

        theta = mp.acos(q[0] / norm_q)
        v_unit = [v[0] / norm_v, v[1] / norm_v, v[2] / norm_v]

        return [mp.ln(norm_q), theta * v_unit[0], theta * v_unit[1], theta * v_unit[2]]

    def quaternion_rotation(self, q, axis, angle):
        """
        Aplica uma rotação tridimensional usando quaternions.

        Parâmetros:
        - q: O quaternion a ser rotacionado (lista de 4 elementos)
        - axis: O eixo de rotação (lista de 3 elementos normalizados)
        - angle: O ângulo da rotação em radianos
        """
        axis_norm = mp.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
        if axis_norm == 0:
            raise ValueError("O eixo de rotação não pode ser nulo.")

        axis = [axis[0] / axis_norm, axis[1] / axis_norm, axis[2] / axis_norm]
        rotor = [mp.cos(angle / 2), mp.sin(angle / 2) * axis[0], mp.sin(angle / 2) * axis[1], mp.sin(angle / 2) * axis[2]]
        rotor_inv = [mp.cos(angle / 2), -mp.sin(angle / 2) * axis[0], -mp.sin(angle / 2) * axis[1], -mp.sin(angle / 2) * axis[2]]

        return self.quaternion_multiply(self.quaternion_multiply(rotor, q), rotor_inv)

    def quaternion_multiply(self, q1, q2):
        """
        Multiplicação de dois quaternions q1 e q2.
        """
        a1, b1, c1, d1 = q1
        a2, b2, c2, d2 = q2

        return [
            a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2,
            a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
            a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2,
            a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2
        ]
        
# Testes para a classe ERIRE com precisão máxima

# Dummy QuantumCircuit para teste da função apply_quantum_gate
class DummyQuantumCircuit:
    def __init__(self):
        self.gates = []
    def p(self, theta, qubit):
        self.gates.append(("p", theta, qubit))
    def draw(self, style):
        print("Quantum Circuit Gates:", self.gates)

def test_symmetry_numeric():
    """Teste 1: Verifica se RIRE(EIRE(z, m), m) = z numericamente."""
    z = 1 + 1j
    erire = ERIRE(z, m=2, n=2, symbolic=False)
    combined = erire.erire_combined()
    error_numeric = abs(z - combined)
    print("🔹 Teste 1: Simetria Numérica")
    print(f"Original: {z}")
    print(f"RIRE(EIRE(z, 2), 2): {combined}")
    print(f"Erro de simetria: {error_numeric}\n")

def test_symmetry_symbolic():
    """Teste 2: Verifica se RIRE(EIRE(z, m), m) = z simbolicamente."""
    z_sym = sp.S(1) + sp.I
    erire = ERIRE(z_sym, m=2, n=2, symbolic=True)
    combined = erire.erire_combined()
    error_symbolic = sp.simplify(z_sym - combined)
    print("🔹 Teste 2: Simetria Simbólica")
    print(f"Original: {z_sym}")
    print(f"RIRE(EIRE(z, 2), 2): {combined}")
    print(f"Erro de simetria: {error_symbolic}\n")

def test_root_imaginary():
    """Teste 3: Valida o cálculo da raiz imaginária z^(1/i)."""
    z = 1 + 1j
    erire_num = ERIRE(z, symbolic=False)
    erire_sym = ERIRE(z, symbolic=True)
    sqrt_i_num = erire_num.sqrt_i()
    sqrt_i_sym = erire_sym.sqrt_i()
    error_sqrt = abs(sqrt_i_num - complex(sqrt_i_sym.evalf()))
    print("🔹 Teste 3: Raiz Imaginária")
    print(f"Raiz (numérica): {sqrt_i_num}")
    print(f"Raiz (simbólica): {sqrt_i_sym}")
    print(f"Erro: {error_sqrt}\n")

def test_hypercomplex_rotation():
    """Teste 4: Valida a rotação hipercomplexa em 3D."""
    z = 1 + 1j
    vector = np.array([1.0, 1.0, 0.0])
    erire = ERIRE(z, m=1, plane='k', symbolic=False)
    transformed = erire.hypercomplex_transform(vector)
    norm_diff = abs(np.linalg.norm(vector) - np.linalg.norm(transformed))
    print("🔹 Teste 4: Rotação em C³")
    print(f"Vetor Original: {vector}")
    print(f"Vetor Transformado: {transformed}")
    print(f"Erro de norma: {norm_diff}\n")

def test_rotation_matrix():
    """Teste 5: Verifica a matriz de rotação 2D para 45°."""
    erire = ERIRE(1 + 1j, symbolic=False)
    theta = np.pi / 4
    rot_mat = erire.rotation_matrix(2, theta, plane=(0, 1))
    expected = np.array([[np.cos(theta), -np.sin(theta)],
                         [np.sin(theta),  np.cos(theta)]])
    error_mat = np.linalg.norm(rot_mat - expected)
    print("🔹 Teste 5: Matriz de Rotação (2D, 45°)")
    print(rot_mat)
    print(f"Erro: {error_mat}\n")

def test_variable_m_n():
    """Teste 6: Avalia transformações apenas quando m = n."""
    z = mp.mpc(1, 1)
    z = ERIRE.convert_mpc_to_complex(z)

    for m, n in [(1, 1), (2, 2), (5, 5)]:  # Evitando casos onde m ≠ n
        erire = ERIRE(z, m=m, n=n, symbolic=False)
        combined = erire.erire_combined()
        expected = z  # Garantimos que m = n, então esperamos que z seja preservado
        error = abs(expected - combined)
        print(f"🔹 Teste 6: m={m}, n={n}")
        print(f"Obtido: {combined}")
        print(f"Esperado: {expected}")
        print(f"Erro: {error}\n")

def test_real_number_operations():
    """Teste 7: Verifica operações com números reais."""
    z_real = 2.0
    erire = ERIRE(z_real, m=2, n=2, symbolic=False)
    combined = erire.erire_combined()
    error = abs(z_real - combined)
    print("🔹 Teste 7: Operações com Número Real")
    print(f"Original: {z_real}")
    print(f"Obtido: {combined}")
    print(f"Erro: {error}\n")

def test_stability():
    """Teste 8: Verifica estabilidade com valores muito pequenos."""
    z_small = 1e-10 + 1e-10j
    erire = ERIRE(z_small, m=2, n=2, symbolic=False)
    combined = erire.erire_combined()
    error = abs(z_small - combined)
    print("🔹 Teste 8: Estabilidade Computacional")
    print(f"Original: {z_small}")
    print(f"Obtido: {combined}")
    print(f"Erro: {error}\n")

def test_visualization_complex():
    """Teste 9: Exibe visualização no plano complexo (inspeção visual)."""
    erire = ERIRE(1 + 1j, m=2, symbolic=False)
    print("🔹 Teste 9: Visualização no Plano Complexo\n")
    erire.visualize_complex()

def test_visualization_hypercomplex():
    """Teste 10: Exibe visualização no espaço hipercomplexo (inspeção visual)."""
    erire = ERIRE(1 + 1j, m=1, plane='k', symbolic=False)
    print("🔹 Teste 10: Visualização no Espaço Hipercomplexo\n")
    erire.visualize_hypercomplex()

# Funções adicionais para suportar os novos testes

def test_complex_conjugate():
    """Teste 11: Verifica se EIRE e RIRE preservam propriedades do conjugado complexo."""
    z = 1 + 1j
    erire = ERIRE(z, m=2, n=2, symbolic=False)
    eire_result = erire.eire()
    rire_result = erire.rire()
    conj_z = mp.conj(z)
    conj_eire = mp.conj(eire_result)
    conj_rire = mp.conj(rire_result)
    conj_z = ERIRE.convert_mpc_to_complex(conj_z)
    error_eire = abs(mp.conj(erire.eire()) - ERIRE(conj_z, m=2).eire())
    error_rire = abs(mp.conj(erire.rire()) - ERIRE(conj_z, n=2).rire())
    print("🔹 Teste 11: Propriedade do Conjugado")
    print(f"Conjugado de z: {conj_z}")
    print(f"EIRE(z): {eire_result}, Conjugado: {conj_eire}")
    print(f"RIRE(z): {rire_result}, Conjugado: {conj_rire}")
    print(f"Erro EIRE: {error_eire}")
    print(f"Erro RIRE: {error_rire}\n")

def test_zero_input():
    """Teste 12: Verifica comportamento com z = 0."""
    z = 0
    erire = ERIRE(z, m=2, n=2, symbolic=False)

    try:
        eire_result = erire.eire()
        rire_result = erire.rire()
        combined = erire.erire_combined()
        print("🔹 Teste 12: Entrada Zero\n")
        print(f"Original: {z}")
        print(f"EIRE(z, 2): {eire_result}")
        print(f"RIRE(z, 2): {rire_result}")
        if combined is None:
            print("RIRE(EIRE(z, 2), 2) retornou None devido à entrada inadequada (z = 0).")
        else:
            error = abs(z - combined)
            print(f"RIRE(EIRE(z, 2), 2): {combined}")
            print(f"Erro: {error}\n")
    except ValueError as e:
        print("🔹 Teste 12: Entrada Zero")
        print(f"Erro detectado corretamente: {e}\n")

def test_negative_real():
    """Teste 13: Testa números reais negativos."""
    z = -2.0
    erire = ERIRE(z, m=2, n=2, symbolic=False)
    combined = erire.erire_combined()
    error = abs(z - combined)
    print("🔹 Teste 13: Número Real Negativo")
    print(f"Original: {z}")
    print(f"RIRE(EIRE(z, 2), 2): {combined}")
    print(f"Erro: {error}\n")

def test_transform_convergence():
    """Teste 14: Verifica convergência da transformada ERIRE."""
    
    def signal(t):
        """Garante compatibilidade com `mpmath` e `numpy`."""
        if isinstance(t, mp.mpf):  # Se for um número de alta precisão, usa `mpmath.cos`
            return mp.cos(t)
        else:  # Caso contrário, usa `numpy.cos()`
            return np.cos(t)

    z = 1 + 1j
    erire = ERIRE(z, m=1, symbolic=False)
    transform = erire.erire_transform(signal, w=1.0)
    
    print("🔹 Teste 14: Transformada ERIRE")
    print(f"Transformada de cos(t) com w=1: {transform}\n")

def test_quantum_gate():
    """Teste 15: Simula aplicação de uma porta quântica baseada em EIRE."""
    z = 1 + 1j
    erire = ERIRE(z, m=2, symbolic=False)
    qc = DummyQuantumCircuit()
    erire.apply_quantum_gate(qc, 0)
    print("🔹 Teste 15: Porta Quântica")
    print(f"Gates aplicados: {qc.gates}\n")

def test_large_values():
    """Teste 16: Testa comportamento com valores grandes."""
    z = 1e10 + 1e10j
    erire = ERIRE(z, m=2, n=2, symbolic=False)
    combined = erire.erire_combined()
    error = abs(z - combined)
    print("🔹 Teste 16: Valores Grandes")
    print(f"Original: {z}")
    print(f"RIRE(EIRE(z, 2), 2): {combined}")
    print(f"Erro: {error}\n")

def test_pure_imaginary():
    """Teste 17: Testa números puramente imaginários."""
    z = 2j
    erire = ERIRE(z, m=2, n=2, symbolic=False)
    combined = erire.erire_combined()
    error = abs(z - combined)
    print("🔹 Teste 17: Número Puro Imaginário")
    print(f"Original: {z}")
    print(f"RIRE(EIRE(z, 2), 2): {combined}")
    print(f"Erro: {error}\n")

def test_multiple_planes():
    """Teste 18: Verifica rotação em diferentes planos hipercomplexos."""
    z = 1 + 1j
    vector = np.array([1.0, 1.0, 0.0])
    for plane in ['i', 'j', 'k']:
        erire = ERIRE(z, m=1, plane=plane, symbolic=False)
        transformed = erire.hypercomplex_transform(vector)
        print(f"🔹 Teste 18: Rotação no plano {plane}")
        print(f"Vetor Original: {vector}")
        print(f"Vetor Transformado: {transformed}\n")

def teste_quaternion_exp():
    """Teste 19: Verifica se a exponencial de um quaternion é computada corretamente."""
    erire = ERIRE(0)

    q = [mp.mpf(0), mp.mpf(1), mp.mpf(1), mp.mpf(0)]
    resultado = erire.quaternion_exp(q)

    print("\n🔹 Teste 19: Exponencial de um quaternion")
    print("  Quaternion original:", q)
    print("  Exponencial do quaternion:", resultado)

def teste_quaternion_ln():
    """Teste 20: Verifica se o logaritmo de um quaternion é computado corretamente."""
    erire = ERIRE(0)

    q = [mp.mpf(1), mp.mpf(2), mp.mpf(2), mp.mpf(0)]
    resultado = erire.quaternion_ln(q)

    print("\n🔹 Teste 20: Logaritmo de um quaternion")
    print("  Quaternion original:", q)
    print("  Logaritmo natural do quaternion:", resultado)

def teste_quaternion_multiplicacao():
    """Teste 21: Verifica a multiplicação de dois quaternions."""
    erire = ERIRE(0)

    q1 = [mp.mpf(1), mp.mpf(1), mp.mpf(0), mp.mpf(0)]
    q2 = [mp.mpf(0), mp.mpf(1), mp.mpf(1), mp.mpf(0)]
    resultado = erire.quaternion_multiply(q1, q2)

    print("\n🔹 Teste 21: Multiplicação de quaternions")
    print("  Quaternion 1:", q1)
    print("  Quaternion 2:", q2)
    print("  Produto dos quaternions:", resultado)

def teste_quaternion_rotacao():
    """Teste 22: Verifica se uma rotação tridimensional é aplicada corretamente."""
    erire = ERIRE(0)

    q = [mp.mpf(0), mp.mpf(1), mp.mpf(0), mp.mpf(0)]
    axis = [mp.mpf(0), mp.mpf(1), mp.mpf(0)]
    angle = mp.pi / 2
    resultado = erire.quaternion_rotation(q, axis, angle)

    print("\n🔹 Teste 22: Rotação de quaternion")
    print("  Quaternion original:", q)
    print("  Eixo de rotação:", axis)
    print("  Ângulo (radianos):", angle)
    print("  Quaternion após rotação:", resultado)

# Chamada na main com todos os testes
if __name__ == "__main__":
    test_symmetry_numeric()
    test_symmetry_symbolic()
    test_root_imaginary()
    test_hypercomplex_rotation()
    test_rotation_matrix()
    test_variable_m_n()
    test_real_number_operations()
    test_stability()
    test_visualization_complex()
    test_visualization_hypercomplex()
    test_complex_conjugate()
    test_zero_input()
    test_negative_real()
    test_transform_convergence()
    test_quantum_gate()
    test_large_values()
    test_pure_imaginary()
    test_multiple_planes()
    teste_quaternion_exp()
    teste_quaternion_ln()
    teste_quaternion_multiplicacao()
    teste_quaternion_rotacao()
