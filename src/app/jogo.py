"""Estados do jogo (início, jogando, pausa, fim, saída), teclado e o que cada tela mostra."""
from enum import Enum

import glfw
import moderngl
import numpy as np

from config import (
    ALTURA_JANELA, ATENUACAO_FORA_DO_JOGO, COR_DESTAQUE, COR_FIM, COR_PLACAR, FUNDO,
    LARGURA_JANELA, NOME_JOGO, TEXTO_FIM, TEXTO_INICIO, TEXTO_PAUSA, TEXTO_SAIR,
)
from partida import Partida
from placar import Placar
from recordes import Recordes
from renderizador import Renderizador


class Estado(Enum):
    INICIO = "inicio"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    FIM = "fim de jogo"
    SAINDO = "sair?"


# P só alterna entre jogando e pausado; nos outros estados não faz nada.
PAUSA = {Estado.JOGANDO: Estado.PAUSADO, Estado.PAUSADO: Estado.JOGANDO}

TECLAS_DIREITA = (glfw.KEY_RIGHT, glfw.KEY_D)
TECLAS_ESQUERDA = (glfw.KEY_LEFT, glfw.KEY_A)
TECLAS_ENTER = (glfw.KEY_ENTER, glfw.KEY_KP_ENTER)
# Tecla e efeito, mostrados na tela de saída.
DICAS_SAIDA = (("ENTER", "SAI"), ("ESC", "FICA"))


class Jogo:
    def __init__(self, ctx: moderngl.Context, janela: 'glfw._GLFWwindowPointerT') -> None:
        self.janela = janela
        self.render = Renderizador(ctx)
        self.placar = Placar(self.render)
        self.recordes = Recordes()
        self.vsync = True
        self.nova_partida(Estado.INICIO)

        # Tecla nova = um método + uma linha aqui.
        self.acoes = {
            glfw.KEY_ESCAPE: self.alternar_saida,
            glfw.KEY_V: self.alternar_vsync,
            glfw.KEY_F: self.alternar_tela_cheia,
            glfw.KEY_P: self.alternar_pausa,
            glfw.KEY_R: self.reiniciar,
            glfw.KEY_SPACE: self.jogar,
            **dict.fromkeys(TECLAS_ENTER, self.confirmar),
        }

    # ------------------------------------------------------------------ teclado
    def tecla(self, janela: 'glfw._GLFWwindowPointerT', key: int, scancode: int,
              action: int, mods: int) -> None:
        """Callback de teclado do GLFW. Só o PRESS conta: segurar não repete a ação."""
        if action == glfw.PRESS and (acao := self.acoes.get(key)):
            acao()

    def sair(self) -> None:
        glfw.set_window_should_close(self.janela, True)

    def alternar_saida(self) -> None:
        """ESC pergunta antes de fechar; ESC de novo volta para onde estava."""
        if self.estado == Estado.SAINDO:
            self.estado = self.estado_anterior
        else:
            self.estado_anterior, self.estado = self.estado, Estado.SAINDO

    def alternar_vsync(self) -> None:
        self.vsync = not self.vsync
        glfw.swap_interval(int(self.vsync))

    def alternar_tela_cheia(self) -> None:
        """
        Alterna entre janela e tela cheia no monitor principal. O novo tamanho chega
        logo depois, pelo callback redimensionar.
        """
        monitor = glfw.get_primary_monitor()
        modo = glfw.get_video_mode(monitor)
        largura_monitor, altura_monitor = modo.size

        if glfw.get_window_monitor(self.janela):   # volta para a janela, centralizada
            x = (largura_monitor - LARGURA_JANELA) // 2
            y = (altura_monitor - ALTURA_JANELA) // 2
            glfw.set_window_monitor(self.janela, None, x, y, LARGURA_JANELA, ALTURA_JANELA, 0)
        else:
            # Com a resolução e a taxa do monitor, o GLFW não troca o modo de vídeo e
            # a tela não pisca ao entrar.
            glfw.set_window_monitor(self.janela, monitor, 0, 0, largura_monitor,
                                    altura_monitor, modo.refresh_rate)

    def alternar_pausa(self) -> None:
        self.estado = PAUSA.get(self.estado, self.estado)

    def reiniciar(self) -> None:
        if self.estado != Estado.SAINDO:   # na pergunta de saída só ENTER e ESC valem
            self.nova_partida(Estado.INICIO)

    def jogar(self) -> None:
        match self.estado:
            case Estado.INICIO:
                self.estado = Estado.JOGANDO
            case Estado.FIM:
                self.nova_partida(Estado.JOGANDO)

    def confirmar(self) -> None:
        """ENTER joga, como o ESPAÇO, e é a única tecla que confirma a saída."""
        if self.estado == Estado.SAINDO:
            self.sair()
        else:
            self.jogar()

    def nova_partida(self, estado: Estado) -> None:
        self.partida = Partida()
        self.estado = estado
        self.tempo_tela = 0.0
        self.posicao_recorde = None   # na tabela de recordes, quando a partida acaba

    def _apertada(self, teclas: tuple[int, ...]) -> bool:
        return any(glfw.get_key(self.janela, t) == glfw.PRESS for t in teclas)

    def direcao(self) -> float:
        """-1 (esquerda), 0 ou 1 (direita). Lida a cada quadro, não pelo callback."""
        return float(self._apertada(TECLAS_DIREITA)) - float(self._apertada(TECLAS_ESQUERDA))

    # ------------------------------------------------------------------- janela
    def redimensionar(self, janela: 'glfw._GLFWwindowPointerT', largura: int,
                      altura: int) -> None:
        """Callback do GLFW quando a área de desenho muda de tamanho (em pixels)."""
        self.render.ajustar_viewport(largura, altura)

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        if self.estado == Estado.JOGANDO:
            self.partida.atualizar(dt, self.direcao())
            if self.partida.terminou:
                self.estado = Estado.FIM
                self.tempo_tela = 0.0
                self.posicao_recorde = self.recordes.registrar(self.partida.pontuacao)
        elif self.estado in (Estado.INICIO, Estado.FIM):
            self.tempo_tela += dt   # anima as telas de início e fim

    def desenhar(self) -> None:
        self.render.limpar(FUNDO)
        jogando = self.estado == Estado.JOGANDO
        self.render.atenuar(1.0 if jogando else ATENUACAO_FORA_DO_JOGO)
        self.partida.desenhar(self.render)

        # Daqui para baixo, coordenadas da tela e sem atenuação.
        self.render.usar_tela()
        self.render.atenuar(1.0)
        self.placar.desenhar_hud(self.partida.pontuacao, self.partida.moedas_coletadas)
        match self.estado:
            case Estado.INICIO:
                self.placar.escrever(TEXTO_INICIO, 0.0, 0.3, 0.16, COR_DESTAQUE, 'centro')
                self._icone_jogar(-0.05)
            case Estado.PAUSADO:
                for lado in (-1.0, 1.0):
                    self.render.retangulo((0.06 * lado, 0.08), (0.07, 0.26), COR_PLACAR)
                self.placar.escrever(TEXTO_PAUSA, 0.0, -0.22, 0.12, COR_PLACAR, 'centro')
            case Estado.FIM:
                self.placar.escrever(TEXTO_FIM, 0.0, 0.70, 0.11, COR_FIM, 'centro')
                self.placar.escrever(str(self.partida.pontuacao), 0.0, 0.48, 0.16,
                                     COR_PLACAR, 'centro')
                self.placar.desenhar_recordes(self.recordes.pontos, self.posicao_recorde,
                                              0.22, self._pulso())
                self._icone_jogar(-0.66)
            case Estado.SAINDO:
                # Caixa da cor do fundo: esconde a cena atrás do aviso.
                self.render.retangulo((0.0, 0.0), (0.76, 0.54), FUNDO)
                self.render.contorno((0.0, 0.0), (0.76, 0.54), COR_FIM)
                self.placar.escrever(TEXTO_SAIR, 0.0, 0.13, 0.12, COR_FIM, 'centro')
                for i, (nome_tecla, efeito) in enumerate(DICAS_SAIDA):
                    y = -0.05 - 0.13 * i
                    self.placar.escrever(nome_tecla, -0.28, y, 0.06, COR_DESTAQUE)
                    self.placar.escrever(efeito, 0.28, y, 0.06, COR_PLACAR, 'direita')

    def _pulso(self) -> float:
        return 1.0 + 0.12 * np.sin(2.0 * np.pi * 1.2 * self.tempo_tela)

    def _icone_jogar(self, y: float) -> None:
        self.render.triangulo((0.0, y), 0.22 * self._pulso(), COR_DESTAQUE)

    def titulo(self, fps: float) -> str:
        return (f"{NOME_JOGO} - {self.estado.value} - {self.partida.pontuacao} pts - "
                f"vsync {'on' if self.vsync else 'OFF'} - {fps:5.1f} fps")

    def liberar(self) -> None:
        self.render.liberar()
