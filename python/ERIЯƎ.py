import numpy as np
import math
from scipy.spatial.transform import Rotation as R

class ERIЯƎ:
    """
    Classe que implementa a Teoria ERIЯƎ - Exponencialização e Racionalização Imaginária Rotacional Evolutiva.
    Inclui operações de transformação ressonante sobre números complexos e extensões para hipercomplexos.
    """

    def __init__(self, z, m=1, n=1, plane='i'):
        """
        Inicializa um número complexo ou quaternário para aplicação das operações ERIRE.

        :param z: Número complexo ou hipercomplexo a ser transformado.
        :param m: Parâmetro de transformação ressonante para EIRE.
        :param n: Parâmetro de estabilização para RIRE.
        :param plane: Plano de rotação ('i', 'j', 'k' para quaternions).
        """
        self.z = self.convert_to_complex(z)
        self.m = m
        self.n = n
        self.plane = plane.lower()

    def convert_to_complex(self, z):
        """
        Converte diferentes representações numéricas para um número complexo.
        
        :param z: Entrada numérica (cartesiana, polar, vetorial, matriz, dicionário).
        :return: Número complexo correspondente.
        """
        if isinstance(z, (int, float, complex)):
            return complex(z)
        elif isinstance(z, (tuple, list)) and len(z) == 2:
            return complex(z[0], z[1])
        elif isinstance(z, dict) and "real" in z and "imag" in z:
            return complex(z["real"], z["imag"])
        elif isinstance(z, np.ndarray) and z.shape == (2,):
            return complex(z[0], z[1])
        else:
            raise ValueError("Formato não reconhecido para número complexo.")

    def eire(self):
        """
        Aplica a operação EIRE (Exponencialização Imaginária Rotacional Evolutiva).

        :return: Número complexo transformado por EIRE.
        """
        return np.exp(1j * self.m * np.log(self.z))

    def rire(self):
        """
        Aplica a operação RIRE (Racionalização Imaginária Rotacional Evolutiva).

        :return: Número complexo transformado por RIRE.
        """
        r, phi = np.abs(self.z), np.angle(self.z)
        return (r ** (1 / self.n)) * np.exp(1j * (phi + (np.pi / self.n)))

    def quaternion_rotation(self, q, angle):
        """
        Aplica uma rotação quaternária no número.

        :param q: Número quaternário (x, y, z, w).
        :param angle: Ângulo de rotação.
        :return: Número quaternário rotacionado.
        """
        rot = R.from_rotvec(angle * np.array([1, 0, 0]))  # Rotação no eixo 'i'
        return rot.apply(q)

    def rotate_n_dim(self, vector, theta):
        """
        Aplica uma rotação multidimensional sobre um vetor.

        :param vector: Vetor a ser rotacionado.
        :param theta: Ângulo de rotação.
        :return: Vetor rotacionado.
        """
        if len(vector) < 2:
            raise ValueError("Vetor deve ter pelo menos duas dimensões para rotação.")
        
        dim = len(vector)
        rotation_matrix = self.rotation_matrix(dim, theta)
        return np.dot(rotation_matrix, vector)

    def rotation_matrix(self, dim, theta):
        """
        Gera uma matriz de rotação para espaços de múltiplas dimensões.

        :param dim: Dimensão do espaço.
        :param theta: Ângulo de rotação.
        :return: Matriz de rotação (dim x dim).
        """
        matrix = np.eye(dim)
        for i in range(dim - 1):
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            rotation_submatrix = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
            matrix[i:i+2, i:i+2] = rotation_submatrix
        return matrix
        
    def visualize_rotation(self, x, y):
        """
        Plota a rotação de um ponto no plano complexo sob EIRE.
        
        :param x: Coordenada X do ponto.
        :param y: Coordenada Y do ponto.
        """
        import matplotlib.pyplot as plt

        x_new, y_new = self.rotate_point(x, y)

        plt.scatter([x], [y], color='blue', label='Original')
        plt.scatter([x_new], [y_new], color='red', label='Transformado')
        plt.legend()
        plt.xlabel("Re")
        plt.ylabel("Im")
        plt.title("Rotação ERIЯƎ")
        plt.grid()
        plt.show()

    def hypercomplex_transform(self):
        """
        Extensão para números hipercomplexos (exemplo usando quaternions).

        :return: Transformação ressonante em um número hipercomplexo.
        """
        quaternion = np.array([self.z.real, self.z.imag, 0, 0])  # Expansão para 4D
        return self.quaternion_rotation(quaternion, self.m * np.pi / 2)

    def visualize_complex(self):
        """
        Visualiza a transformação no plano complexo.

        :return: Gráfico mostrando a transformação.
        """
        import matplotlib.pyplot as plt

        original = self.z
        transformed = self.eire()

        plt.figure(figsize=(6, 6))
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True, linestyle='--', linewidth=0.5)

        plt.scatter(original.real, original.imag, color='red', label='Original')
        plt.scatter(transformed.real, transformed.imag, color='blue', label='Transformado')
        plt.plot([0, original.real], [0, original.imag], 'r--')
        plt.plot([0, transformed.real], [0, transformed.imag], 'b--')

        plt.xlabel("Re")
        plt.ylabel("Im")
        plt.legend()
        plt.title("Transformação ERIRE no Plano Complexo")
        plt.show()

    def visualize_hypercomplex(self):
        """
        Visualiza a transformação hipercomplexa (3D com extensão quaternária).

        :return: Gráfico mostrando a transformação hipercomplexa.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        original = np.array([self.z.real, self.z.imag, 0])
        transformed = self.hypercomplex_transform()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(original[0], original[1], original[2], color='red', label="Original")
        ax.scatter(transformed[0], transformed[1], transformed[2], color='blue', label="Transformado")
        ax.plot([0, original[0]], [0, original[1]], [0, original[2]], 'r--')
        ax.plot([0, transformed[0]], [0, transformed[1]], [0, transformed[2]], 'b--')

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Transformação Hipercomplexa ERIRE")
        ax.legend()
        plt.show()

    def erire_transform(self, f, w):
        """
        Computa a Transformada ERIЯƎ de uma função f(t).
        
        :param f: Função de entrada a ser transformada.
        :param w: Frequência angular da transformação.
        :return: Valor transformado.
        """
        integral, _ = quad(lambda t: f(t) * np.exp(1j * self.m * (-1j * w * t)), -np.inf, np.inf)
        return integral

    def apply_quantum_gate(self, qc, qubit):
        """
        Aplica uma porta lógica baseada na exponencialização EIRE em um circuito quântico.
        
        :param qc: Objeto QuantumCircuit do Qiskit.
        :param qubit: Índice do qubit onde a porta será aplicada.
        """
        qc.p(np.pi * self.m, qubit)  # Aplica rotação de fase baseada na EIRE

    def rotate_point(self, x, y):
        """
        Aplica uma rotação ERIЯƎ a um ponto no plano.
        
        :param x: Coordenada X do ponto.
        :param y: Coordenada Y do ponto.
        :return: Coordenadas transformadas (x', y').
        """
        z = complex(x, y)
        z_rot = self.eire()
        return z_rot.real, z_rot.imag

# Exemplo de uso:
z = 1 + 1j
erire_instance = ERIRE(z, m=2, n=3)

# Aplicação das operações
eire_result = erire_instance.eire()
rire_result = erire_instance.rire()

print(f"EIRE({z}, m=2): {eire_result}")
print(f"RIRE({z}, n=3): {rire_result}")

# Exemplo de aplicação em computação quântica
qc = QuantumCircuit(1)
erire_comp.apply_quantum_gate(qc, 0)
qc.draw('mpl')

# Visualização da rotação ERIЯƎ
erire_comp.visualize_rotation(1, 1)

# Visualização das transformações
erire_instance.visualize_complex()
erire_instance.visualize_hypercomplex()
