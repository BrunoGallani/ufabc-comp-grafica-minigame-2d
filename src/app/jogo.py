"""Estados do jogo (início, jogando, pausa, fim), teclado e o que cada tela mostra."""
from enum import Enum

import glfw
import moderngl
import numpy as np

from config import (
    ATENUACAO_FORA_DO_JOGO, COR_DESTAQUE, COR_FIM, COR_PLACAR, FUNDO, NOME_JOGO, TEXTO_FIM,
    TEXTO_INICIO, TEXTO_PAUSA,
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


# P só alterna entre jogando e pausado; nos outros estados não faz nada.
PAUSA = {Estado.JOGANDO: Estado.PAUSADO, Estado.PAUSADO: Estado.JOGANDO}

TECLAS_DIREITA = (glfw.KEY_RIGHT, glfw.KEY_D)
TECLAS_ESQUERDA = (glfw.KEY_LEFT, glfw.KEY_A)
TECLAS_CONFIRMAR = (glfw.KEY_ENTER, glfw.KEY_KP_ENTER, glfw.KEY_SPACE)


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
            glfw.KEY_ESCAPE: self.sair,
            glfw.KEY_V: self.alternar_vsync,
            glfw.KEY_P: self.alternar_pausa,
            glfw.KEY_R: self.reiniciar,
            **dict.fromkeys(TECLAS_CONFIRMAR, self.confirmar),
        }

    # ------------------------------------------------------------------ teclado
    def tecla(self, janela: 'glfw._GLFWwindowPointerT', key: int, scancode: int,
              action: int, mods: int) -> None:
        """Callback de teclado do GLFW. Só o PRESS conta: segurar não repete a ação."""
        if action == glfw.PRESS and (acao := self.acoes.get(key)):
            acao()

    def sair(self) -> None:
        glfw.set_window_should_close(self.janela, True)

    def alternar_vsync(self) -> None:
        self.vsync = not self.vsync
        glfw.swap_interval(int(self.vsync))

    def alternar_pausa(self) -> None:
        self.estado = PAUSA.get(self.estado, self.estado)

    def reiniciar(self) -> None:
        self.nova_partida(Estado.INICIO)

    def confirmar(self) -> None:
        match self.estado:
            case Estado.INICIO:
                self.estado = Estado.JOGANDO
            case Estado.FIM:
                self.nova_partida(Estado.JOGANDO)

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

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        if self.estado == Estado.JOGANDO:
            self.partida.atualizar(dt, self.direcao())
            if self.partida.terminou:
                self.estado = Estado.FIM
                self.tempo_tela = 0.0
                self.posicao_recorde = self.recordes.registrar(self.partida.pontuacao)
        elif self.estado != Estado.PAUSADO:
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

    def _pulso(self) -> float:
        return 1.0 + 0.12 * np.sin(2.0 * np.pi * 1.2 * self.tempo_tela)

    def _icone_jogar(self, y: float) -> None:
        self.render.triangulo((0.0, y), 0.22 * self._pulso(), COR_DESTAQUE)

    def titulo(self, fps: float) -> str:
        return (f"{NOME_JOGO} - {self.estado.value} - {self.partida.pontuacao} pts - "
                f"vsync {'on' if self.vsync else 'OFF'} - {fps:5.1f} fps")

    def liberar(self) -> None:
        self.render.liberar()
