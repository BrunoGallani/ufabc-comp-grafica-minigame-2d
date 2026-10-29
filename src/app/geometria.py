"""
Geometrias em numpy (nada aqui fala com a GPU).

Todo vértice é (x, y, 0, 1) em float32, o formato do `vec4 vPosition` do shader.
As formas nascem centradas na origem com tamanho 1; posição e tamanho vêm depois,
pelos uniforms `u_deslocamento` e `u_escala`.
"""
import numpy as np

QUADRADO = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))
TRIANGULOS_QUADRADO = np.array([0, 1, 2, 2, 3, 0], dtype='u4')   # EBO do preenchimento
CONTORNO_QUADRADO = np.array([0, 1, 2, 3], dtype='u4')           # EBO do LINE_LOOP
SETA = ((-0.4, -0.5), (0.6, 0.0), (-0.4, 0.5))                   # aponta para a direita


def vertices(pontos) -> np.ndarray:
    """Pontos (x, y) viram vértices (x, y, 0, 1) em float32."""
    xy = np.asarray(pontos, dtype='f4')
    return np.column_stack((xy, np.zeros(len(xy)), np.ones(len(xy)))).astype('f4')


def leque_circulo(n: int = 40) -> np.ndarray:
    """Círculo de raio 1 para TRIANGLE_FAN: o centro, a volta e o 1º ponto repetido."""
    t = np.linspace(0.0, 2.0 * np.pi, n + 1)   # com o ponto final, t = 2π fecha a volta
    return vertices(np.vstack(((0.0, 0.0), np.column_stack((np.cos(t), np.sin(t))))))


def ziguezague(espiras: int) -> np.ndarray:
    """
    Mola para LINE_STRIP: vai e volta entre as bordas, começando e terminando no
    meio. Com `u_escala.y` maior, as espiras se afastam e a mola estica.
    """
    n = 2 * espiras
    k = np.arange(n + 1)
    x = np.where(k % 2, -0.5, 0.5)
    x[[0, -1]] = 0.0
    return vertices(np.column_stack((x, k / n - 0.5)))
