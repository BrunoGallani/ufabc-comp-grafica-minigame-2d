"""Tudo que fala com a GPU fica aqui: shaders, malhas (VBO/VAO/EBO) e draw calls."""
from dataclasses import dataclass
from pathlib import Path

import moderngl
import numpy as np

import geometria
from config import (
    ALTURA_JANELA, COR_FAIXAS, ESPIRAS_MOLA, LARGURA_JANELA, MEIA_ALTURA_TELA,
    MEIA_LARGURA_TELA, Cor, Par,
)

SHADERS = Path(__file__).parent / "shaders"


@dataclass(frozen=True)
class Malha:
    """Uma geometria já na VRAM, com a primitiva usada para desenhá-la."""
    vao: moderngl.VertexArray
    primitiva: int


class Renderizador:
    """
    Um único programa de shaders desenha tudo: cada forma vai para a VRAM uma vez
    só e é posicionada pelos uniforms (vértice * u_escala + u_deslocamento, menos
    a câmera).
    """

    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx
        self.prog = ctx.program(
            vertex_shader=(SHADERS / "jogo.vert").read_text(encoding="utf-8"),
            fragment_shader=(SHADERS / "jogo.frag").read_text(encoding="utf-8"),
        )
        self._recursos: list = [self.prog]   # liberados em ordem inversa no fim
        # Escritos a cada draw call: busca no programa uma vez só.
        self._escala, self._deslocamento, self._cor = (
            self.prog[nome] for nome in ('u_escala', 'u_deslocamento', 'u_cor'))

        # O mesmo VBO do quadrado serve ao preenchimento e ao contorno, cada um com seu EBO.
        quadrado = self._buffer(geometria.vertices(geometria.QUADRADO))
        self._cheio = self._malha(quadrado, moderngl.TRIANGLES, geometria.TRIANGULOS_QUADRADO)
        self._borda = self._malha(quadrado, moderngl.LINE_LOOP, geometria.CONTORNO_QUADRADO)
        self._circulo = self._malha(self._buffer(geometria.leque_circulo()),
                                    moderngl.TRIANGLE_FAN)
        self._seta = self._malha(self._buffer(geometria.vertices(geometria.SETA)),
                                 moderngl.TRIANGLES)
        self._ziguezague = self._malha(self._buffer(geometria.ziguezague(ESPIRAS_MOLA)),
                                       moderngl.LINE_STRIP)

        self.ajustar('u_meia_tela', (MEIA_LARGURA_TELA, MEIA_ALTURA_TELA))
        self.usar_tela()
        self.atenuar(1.0)

    def _buffer(self, dados: np.ndarray) -> moderngl.Buffer:
        buffer = self.ctx.buffer(dados.tobytes())
        self._recursos.append(buffer)
        return buffer

    def _malha(self, vbo: moderngl.Buffer, primitiva: int,
               indices: np.ndarray | None = None) -> Malha:
        ebo = self._buffer(indices) if indices is not None else None
        vao = self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')], index_buffer=ebo)
        self._recursos.append(vao)
        return Malha(vao, primitiva)

    def ajustar(self, nome: str, valor) -> None:
        # O linker descarta uniform que não é usado, e aí prog[nome] daria KeyError.
        if (uniforme := self.prog.get(nome, None)) is not None:
            uniforme.value = valor

    def ajustar_viewport(self, largura: int, altura: int) -> None:
        """
        Desenha no maior retângulo centralizado com a proporção da janela. Com outra
        proporção o jogo estica e os círculos viram elipses; as sobras dos lados são
        pintadas em limpar.
        """
        if largura == 0 or altura == 0:   # janela minimizada
            return
        escala = min(largura / LARGURA_JANELA, altura / ALTURA_JANELA)
        largura_jogo, altura_jogo = round(LARGURA_JANELA * escala), round(ALTURA_JANELA * escala)
        self.ctx.viewport = ((largura - largura_jogo) // 2, (altura - altura_jogo) // 2,
                             largura_jogo, altura_jogo)

    def limpar(self, cor: Cor) -> None:
        # O clear ignora o viewport: pinta tudo com a cor das faixas e depois só a
        # área do jogo com a cor do fundo.
        self.ctx.clear(*COR_FAIXAS)
        self.ctx.clear(*cor, viewport=self.ctx.viewport)

    def usar_camera(self, camera_y: float) -> None:
        self.ajustar('u_camera', (0.0, camera_y))

    def usar_tela(self) -> None:
        """Volta para as coordenadas da tela (HUD e textos não andam com a câmera)."""
        self.ajustar('u_camera', (0.0, 0.0))

    def atenuar(self, fator: float) -> None:
        self.ajustar('u_atenuacao', fator)

    def _desenhar(self, malha: Malha, centro: Par, escala: Par, cor: Cor) -> None:
        self._escala.value = escala
        self._deslocamento.value = centro
        self._cor.value = cor
        malha.vao.render(malha.primitiva)

    def retangulo(self, centro: Par, tamanho: Par, cor: Cor) -> None:
        self._desenhar(self._cheio, centro, tamanho, cor)

    def contorno(self, centro: Par, tamanho: Par, cor: Cor) -> None:
        self._desenhar(self._borda, centro, tamanho, cor)

    def elipse(self, centro: Par, raios: Par, cor: Cor) -> None:
        self._desenhar(self._circulo, centro, raios, cor)

    def circulo(self, centro: Par, raio: float, cor: Cor) -> None:
        self.elipse(centro, (raio, raio), cor)

    def triangulo(self, centro: Par, tamanho: float, cor: Cor) -> None:
        self._desenhar(self._seta, centro, (tamanho, tamanho), cor)

    def ziguezague(self, centro: Par, tamanho: Par, cor: Cor) -> None:
        self._desenhar(self._ziguezague, centro, tamanho, cor)

    def liberar(self) -> None:
        # Ordem inversa da criação: cada VAO sai antes dos buffers que ele usa.
        for recurso in reversed(self._recursos):
            recurso.release()
