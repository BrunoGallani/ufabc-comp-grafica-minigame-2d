from pathlib import Path

import moderngl
import numpy as np

from config import MEIA_ALTURA_TELA, MEIA_LARGURA_TELA

SHADERS = Path(__file__).parent / "shaders"

CANTOS = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))
TRIANGULOS = np.array([0, 1, 2, 2, 3, 0], dtype='u4')
CONTORNO = np.array([0, 1, 2, 3], dtype='u4')
TRIANGULO = ((-0.4, -0.5), (0.6, 0.0), (-0.4, 0.5))


def vertices(pontos):
    return np.array([v for x, y in pontos for v in (x, y, 0.0, 1.0)], dtype='f4')


def leque_circulo(n=40):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    volta = list(zip(np.cos(t), np.sin(t)))
    return vertices([(0.0, 0.0)] + volta + [volta[0]])


class Renderizador:
    def __init__(self, ctx):
        self.ctx = ctx
        self.prog = ctx.program(
            vertex_shader=(SHADERS / "jogo.vert").read_text(encoding="utf-8"),
            fragment_shader=(SHADERS / "jogo.frag").read_text(encoding="utf-8"),
        )

        self.vbo_quadrado = ctx.buffer(vertices(CANTOS).tobytes())
        self.ebo_cheio = ctx.buffer(TRIANGULOS.tobytes())
        self.ebo_borda = ctx.buffer(CONTORNO.tobytes())
        self.vao_cheio = self._vao(self.vbo_quadrado, self.ebo_cheio)
        self.vao_borda = self._vao(self.vbo_quadrado, self.ebo_borda)

        self.vbo_circulo = ctx.buffer(leque_circulo().tobytes())
        self.vao_circulo = self._vao(self.vbo_circulo)

        self.vbo_triangulo = ctx.buffer(vertices(TRIANGULO).tobytes())
        self.vao_triangulo = self._vao(self.vbo_triangulo)

        self.ajustar('u_meia_tela', (MEIA_LARGURA_TELA, MEIA_ALTURA_TELA))
        self.usar_tela()
        self.atenuar(1.0)

    def _vao(self, vbo, ebo=None):
        return self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')], index_buffer=ebo)

    def ajustar(self, nome, valor):
        uniforme = self.prog.get(nome, None)  # o linker descarta uniforms nao usados
        if uniforme is not None:
            uniforme.value = valor

    def limpar(self, cor):
        self.ctx.clear(*cor)

    def usar_camera(self, camera_y):
        self.ajustar('u_camera', (0.0, camera_y))

    def usar_tela(self):
        self.ajustar('u_camera', (0.0, 0.0))

    def atenuar(self, fator):
        self.ajustar('u_atenuacao', fator)

    def _desenhar(self, vao, centro, escala, cor, modo):
        self.ajustar('u_escala', escala)
        self.ajustar('u_deslocamento', centro)
        self.ajustar('u_cor', cor)
        vao.render(modo)

    def retangulo(self, centro, tamanho, cor):
        self._desenhar(self.vao_cheio, centro, tamanho, cor, moderngl.TRIANGLES)

    def contorno(self, centro, tamanho, cor):
        self._desenhar(self.vao_borda, centro, tamanho, cor, moderngl.LINE_LOOP)

    def elipse(self, centro, raios, cor):
        self._desenhar(self.vao_circulo, centro, raios, cor, moderngl.TRIANGLE_FAN)

    def circulo(self, centro, raio, cor):
        self.elipse(centro, (raio, raio), cor)

    def triangulo(self, centro, tamanho, cor):
        self._desenhar(self.vao_triangulo, centro, (tamanho, tamanho), cor, moderngl.TRIANGLES)

    def liberar(self):
        for recurso in (self.vao_cheio, self.vao_borda, self.vao_circulo, self.vao_triangulo,
                        self.ebo_cheio, self.ebo_borda, self.vbo_quadrado, self.vbo_circulo,
                        self.vbo_triangulo, self.prog):
            recurso.release()
