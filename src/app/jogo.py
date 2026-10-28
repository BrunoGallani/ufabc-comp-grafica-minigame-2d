import sys
from enum import Enum

import glfw
import moderngl
import numpy as np

from config import (
    ALTURA_JANELA, ATENUACAO_FORA_DO_JOGO, COR_DESTAQUE, COR_FIM, COR_PLACAR, DT_MAXIMO,
    FUNDO, LARGURA_JANELA, NOME_JOGO, TEXTO_FIM, TEXTO_INICIO, TEXTO_PAUSA,
)
from partida import Partida
from placar import Placar
from renderizador import Renderizador


class Estado(Enum):
    INICIO = "inicio"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    FIM = "fim de jogo"


def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


class Jogo:
    def __init__(self):
        glfw.set_error_callback(erro_glfw)
        if not glfw.init():
            sys.exit("FALHA: glfw nao inicializou")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.janela = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, NOME_JOGO, None, None)
        if not self.janela:
            glfw.terminate()
            sys.exit("FALHA: nao foi possivel criar a janela")
        glfw.make_context_current(self.janela)
        self.vsync = True
        glfw.swap_interval(1)

        self.render = Renderizador(moderngl.create_context())
        self.placar = Placar(self.render)
        self.partida = Partida()
        self.estado = Estado.INICIO
        self.tempo_tela = 0.0
        glfw.set_key_callback(self.janela, self.tecla)

    def nova_partida(self, estado):
        self.partida = Partida()
        self.estado = estado
        self.tempo_tela = 0.0

    def tecla(self, janela, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(janela, True)
        elif key == glfw.KEY_V:
            self.vsync = not self.vsync
            glfw.swap_interval(1 if self.vsync else 0)
        elif key == glfw.KEY_P:
            if self.estado == Estado.JOGANDO:
                self.estado = Estado.PAUSADO
            elif self.estado == Estado.PAUSADO:
                self.estado = Estado.JOGANDO
        elif key == glfw.KEY_R:
            self.nova_partida(Estado.INICIO)
        elif key in (glfw.KEY_ENTER, glfw.KEY_KP_ENTER, glfw.KEY_SPACE):
            if self.estado == Estado.INICIO:
                self.estado = Estado.JOGANDO
            elif self.estado == Estado.FIM:
                self.nova_partida(Estado.JOGANDO)

    def direcao(self):
        def apertada(*teclas):
            return any(glfw.get_key(self.janela, t) == glfw.PRESS for t in teclas)
        direita = apertada(glfw.KEY_RIGHT, glfw.KEY_D)
        esquerda = apertada(glfw.KEY_LEFT, glfw.KEY_A)
        return float(direita) - float(esquerda)

    def atualizar(self, dt):
        if self.estado == Estado.JOGANDO:
            self.partida.atualizar(dt, self.direcao())
            if self.partida.terminou:
                self.estado = Estado.FIM
                self.tempo_tela = 0.0
        elif self.estado != Estado.PAUSADO:
            self.tempo_tela += dt

    def desenhar(self):
        self.render.limpar(FUNDO)
        jogando = self.estado == Estado.JOGANDO
        self.render.atenuar(1.0 if jogando else ATENUACAO_FORA_DO_JOGO)
        self.partida.desenhar(self.render)

        self.render.usar_tela()
        self.render.atenuar(1.0)
        self.placar.desenhar_hud(self.partida.pontuacao, self.partida.moedas_coletadas)
        if self.estado == Estado.INICIO:
            self.placar.escrever(TEXTO_INICIO, 0.0, 0.3, 0.16, COR_DESTAQUE, 'centro')
            self._icone_jogar(-0.05)
        elif self.estado == Estado.PAUSADO:
            for lado in (-1.0, 1.0):
                self.render.retangulo((0.06 * lado, 0.08), (0.07, 0.26), COR_PLACAR)
            self.placar.escrever(TEXTO_PAUSA, 0.0, -0.22, 0.12, COR_PLACAR, 'centro')
        elif self.estado == Estado.FIM:
            self.placar.escrever(TEXTO_FIM, 0.0, 0.38, 0.13, COR_FIM, 'centro')
            self.placar.escrever(str(self.partida.pontuacao), 0.0, 0.1, 0.2, COR_PLACAR, 'centro')
            self._icone_jogar(-0.28)

    def _icone_jogar(self, y):
        pulso = 1.0 + 0.12 * np.sin(2.0 * np.pi * 1.2 * self.tempo_tela)
        self.render.triangulo((0.0, y), 0.22 * pulso, COR_DESTAQUE)

    def executar(self):
        instante_anterior = glfw.get_time()
        quadros, marco = 0, instante_anterior

        while not glfw.window_should_close(self.janela):
            agora = glfw.get_time()
            # atualizado em todo quadro, inclusive na pausa: o tempo pausado nao entra no dt
            dt = min(agora - instante_anterior, DT_MAXIMO)
            instante_anterior = agora

            self.atualizar(dt)
            self.desenhar()
            glfw.swap_buffers(self.janela)
            glfw.poll_events()

            quadros += 1
            if agora - marco >= 0.5:
                fps = quadros / (agora - marco)
                glfw.set_window_title(
                    self.janela,
                    f"{NOME_JOGO} - {self.estado.value} - {self.partida.pontuacao} pts - "
                    f"vsync {'on' if self.vsync else 'OFF'} - {fps:5.1f} fps")
                quadros, marco = 0, agora

        self.render.liberar()
        glfw.terminate()
