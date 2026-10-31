"""
Estados do jogo (menu, recordes, jogando, pausa, fim e o diálogo do ESC), teclado
e o que cada tela mostra.
"""
from enum import Enum
from functools import partial

import glfw
import moderngl
import numpy as np

from config import (
    ATENUACAO_FORA_DO_JOGO, COR_DESTAQUE, COR_FIM, COR_PLACAR, FUNDO, NOME_JOGO, TEXTO_FIM,
    TEXTO_PAUSA,
)
from menu import Menu, Opcao
from partida import Partida
from placar import Placar
from recordes import Recordes
from renderizador import Renderizador


class Estado(Enum):
    MENU = "menu"
    RECORDES = "recordes"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    FIM = "fim de jogo"
    DIALOGO = "diálogo"


# P só alterna entre jogando e pausado; nos outros estados não faz nada.
PAUSA = {Estado.JOGANDO: Estado.PAUSADO, Estado.PAUSADO: Estado.JOGANDO}

TECLAS_DIREITA = (glfw.KEY_RIGHT, glfw.KEY_D)
TECLAS_ESQUERDA = (glfw.KEY_LEFT, glfw.KEY_A)
TECLAS_ENTER = (glfw.KEY_ENTER, glfw.KEY_KP_ENTER)


class Jogo:
    def __init__(self, ctx: moderngl.Context, janela: 'glfw._GLFWwindowPointerT') -> None:
        self.janela = janela
        self.render = Renderizador(ctx)
        self.placar = Placar(self.render)
        self.recordes = Recordes()
        self.vsync = True
        self.relogio = 0.0             # anima as setas que pulsam
        self.posicao_recorde = None    # na tabela de recordes, quando a partida acaba
        self.estado_anterior = Estado.JOGANDO   # para onde o CONTINUAR volta
        # As opções de cada tela que tem lista. Ficam guardadas: o diálogo do ESC
        # aberto no fim de jogo volta para a lista do fim como ela estava.
        self.menus: dict[Estado, Menu] = {}
        self.partida = Partida()
        self.abrir_menu()

        # Tecla nova = um método + uma linha aqui.
        self.acoes = {
            glfw.KEY_ESCAPE: self.voltar,
            glfw.KEY_UP: partial(self.mover, -1),
            glfw.KEY_DOWN: partial(self.mover, 1),
            glfw.KEY_V: self.alternar_vsync,
            glfw.KEY_P: self.alternar_pausa,
            glfw.KEY_R: self.reiniciar,
            **dict.fromkeys(TECLAS_ENTER, self.confirmar),
        }

    # ------------------------------------------------------------------ teclado
    def tecla(self, janela: 'glfw._GLFWwindowPointerT', key: int, scancode: int,
              action: int, mods: int) -> None:
        """Callback de teclado do GLFW. Só o PRESS conta: segurar não repete a ação."""
        if action == glfw.PRESS and (acao := self.acoes.get(key)):
            acao()

    def mover(self, passo: int) -> None:
        if menu := self.menus.get(self.estado):
            menu.mover(passo)

    def confirmar(self) -> None:
        """ENTER executa a opção escolhida, nas telas que têm lista."""
        if menu := self.menus.get(self.estado):
            menu.confirmar()

    def voltar(self) -> None:
        """ESC abre o diálogo (CONTINUAR, INICIO, SAIR); de novo, fecha e volta para onde estava."""
        match self.estado:
            case Estado.DIALOGO:
                self.continuar()
            case Estado.RECORDES:
                self.fechar_recordes()
            case Estado.MENU:
                pass   # para sair do jogo, a opção SAIR
            case _:    # jogando, pausado ou no fim
                self.estado_anterior = self.estado
                self._abrir(Estado.DIALOGO, [
                    ("CONTINUAR", self.continuar), ("INICIO", self.abrir_menu), ("SAIR", self.sair),
                ])

    def alternar_vsync(self) -> None:
        self.vsync = not self.vsync
        glfw.swap_interval(int(self.vsync))

    def alternar_pausa(self) -> None:
        self.estado = PAUSA.get(self.estado, self.estado)

    def reiniciar(self) -> None:
        if self.estado in (Estado.JOGANDO, Estado.PAUSADO, Estado.FIM):
            self.iniciar()

    # -------------------------------------------------------- ações das opções
    def abrir_menu(self) -> None:
        """Menu principal. Com uma partida guardada (começou e não acabou), oferece CONTINUAR."""
        if self.partida.terminou:
            self.partida = Partida()   # no fundo do menu fica a próxima partida
        opcoes = [("INICIAR", self.iniciar), ("RECORDES", self.ver_recordes), ("SAIR", self.sair)]
        if self.partida.comecou:
            opcoes.insert(0, ("CONTINUAR", self.continuar))
        self._abrir(Estado.MENU, opcoes)

    def iniciar(self) -> None:
        """INICIAR, JOGAR e R. A partida guardada é descartada sem entrar nos recordes."""
        if self.partida.comecou:
            self.partida = Partida()
        self.estado = Estado.JOGANDO

    def continuar(self) -> None:
        """Volta para onde o ESC foi apertado, com a partida como estava."""
        self.estado = self.estado_anterior

    def ver_recordes(self) -> None:
        self._abrir(Estado.RECORDES, [("INICIO", self.fechar_recordes)])

    def fechar_recordes(self) -> None:
        self.estado = Estado.MENU   # a seta do menu continua em RECORDES

    def sair(self) -> None:
        glfw.set_window_should_close(self.janela, True)

    def _abrir(self, estado: Estado, opcoes: list[Opcao]) -> None:
        """Vai para uma tela com lista, com a seta na primeira opção."""
        self.menus[estado] = Menu(opcoes)
        self.estado = estado

    def _apertada(self, teclas: tuple[int, ...]) -> bool:
        return any(glfw.get_key(self.janela, t) == glfw.PRESS for t in teclas)

    def direcao(self) -> float:
        """-1 (esquerda), 0 ou 1 (direita). Lida a cada quadro, não pelo callback."""
        return float(self._apertada(TECLAS_DIREITA)) - float(self._apertada(TECLAS_ESQUERDA))

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        self.relogio += dt
        if self.estado == Estado.JOGANDO:
            self.partida.atualizar(dt, self.direcao())
            if self.partida.terminou:
                self.posicao_recorde = self.recordes.registrar(self.partida.pontuacao)
                self._abrir(Estado.FIM, [("JOGAR", self.iniciar), ("INICIO", self.abrir_menu)])

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
            case Estado.MENU:
                self.placar.escrever(NOME_JOGO, 0.0, 0.40, 0.13, COR_DESTAQUE, 'centro')
                self._opcoes(0.0, 0.08)
            case Estado.RECORDES:
                self.placar.desenhar_recordes(self.recordes.pontos, None, 0.45, self._pulso())
                self._opcoes(-0.45, 0.07)
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
                self._opcoes(-0.62, 0.07)
            case Estado.DIALOGO:
                # Caixa da cor do fundo: esconde a cena atrás das opções.
                self.render.retangulo((0.0, 0.0), (0.86, 0.54), FUNDO)
                self.render.contorno((0.0, 0.0), (0.86, 0.54), COR_FIM)
                self._opcoes(0.14, 0.07)

    def _opcoes(self, y: float, altura: float) -> None:
        menu = self.menus[self.estado]
        self.placar.desenhar_opcoes(menu.textos, menu.escolhida, y, altura, self._pulso())

    def _pulso(self) -> float:
        return 1.0 + 0.12 * np.sin(2.0 * np.pi * 1.2 * self.relogio)

    def titulo(self, fps: float) -> str:
        return (f"{NOME_JOGO} - {self.estado.value} - {self.partida.pontuacao} pts - "
                f"vsync {'on' if self.vsync else 'OFF'} - {fps:5.1f} fps")

    def liberar(self) -> None:
        self.render.liberar()
