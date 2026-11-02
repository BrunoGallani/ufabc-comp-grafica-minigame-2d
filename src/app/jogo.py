"""
Estados do jogo (menu, loja, recordes, tutorial, jogando, pausa, fim e o diálogo
do ESC), teclado e o que cada tela mostra.
"""
from enum import Enum
from functools import partial

import glfw
import moderngl
import numpy as np

from carteira import Carteira
from config import (
    ALTURA_JANELA, ATENUACAO_FORA_DO_JOGO, AVISO_SEM_SALDO, COR_DESTAQUE, COR_FIM, COR_MOEDA,
    COR_PLACAR, FUNDO, LARGURA_JANELA, NOME_JOGO, TEXTO_FIM, TEXTO_LOJA, TEXTO_PAUSA,
    TEXTO_TUTORIAL,
)
from display import Display
from loja import Loja
from menu import Menu, Opcao, desenhar_opcoes
from partida import Partida
from placar import Placar
from recordes import Recordes
from renderizador import Renderizador
from skins import SKINS, Skin
from tutorial import desenhar_tutorial


class Estado(Enum):
    MENU = "menu"
    LOJA = "loja"
    RECORDES = "recordes"
    TUTORIAL = "tutorial"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    FIM = "fim de jogo"
    DIALOGO = "diálogo"


# P só alterna entre jogando e pausado; nos outros estados não faz nada.
PAUSA = {Estado.JOGANDO: Estado.PAUSADO, Estado.PAUSADO: Estado.JOGANDO}
# Fora da partida, o canto do placar mostra as moedas guardadas na carteira.
TELAS_DO_MENU = (Estado.MENU, Estado.LOJA, Estado.RECORDES, Estado.TUTORIAL)
# A vitrine da loja e as teclas do tutorial ficam sobre o fundo liso, sem a cena.
TELAS_SEM_CENA = (Estado.LOJA, Estado.TUTORIAL)

TECLAS_DIREITA = (glfw.KEY_RIGHT, glfw.KEY_D)
TECLAS_ESQUERDA = (glfw.KEY_LEFT, glfw.KEY_A)
TECLAS_ENTER = (glfw.KEY_ENTER, glfw.KEY_KP_ENTER, glfw.KEY_SPACE)


class Jogo:
    def __init__(self, ctx: moderngl.Context, janela: 'glfw._GLFWwindowPointerT') -> None:
        self.janela = janela
        self.render = Renderizador(ctx)
        self.display = Display(self.render)   # o texto de todas as telas
        self.placar = Placar(self.display)
        self.recordes = Recordes()
        self.carteira = Carteira()
        self.loja = Loja(self.carteira)
        self.vsync = True
        self.relogio = 0.0             # anima as setas que pulsam e as skins da loja
        self.aviso_saldo = 0.0         # enquanto > 0, o saldo fica vermelho: faltaram moedas
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
            glfw.KEY_F: self.alternar_tela_cheia,
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
        """ENTER/ESPAÇO executa a opção escolhida, nas telas que têm lista; na pausa, retoma."""
        if self.estado == Estado.PAUSADO:
            self.estado = Estado.JOGANDO
        elif menu := self.menus.get(self.estado):
            menu.confirmar()

    def voltar(self) -> None:
        """ESC abre o diálogo (CONTINUAR, INICIO, SAIR); de novo, fecha e volta para onde estava."""
        match self.estado:
            case Estado.DIALOGO:
                self.continuar()
            case Estado.RECORDES | Estado.LOJA | Estado.TUTORIAL:
                self.voltar_ao_menu()
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
        if self.estado in (Estado.JOGANDO, Estado.PAUSADO, Estado.FIM):
            self.iniciar()

    # -------------------------------------------------------- ações das opções
    def abrir_menu(self) -> None:
        """Menu principal. Com uma partida guardada (começou e não acabou), oferece CONTINUAR."""
        if self.partida.terminou:
            self.partida = Partida()   # no fundo do menu fica a próxima partida
        opcoes = [("INICIAR", self.iniciar), ("TUTORIAL", self.ver_tutorial),
                  ("LOJA", self.abrir_loja), ("RECORDES", self.ver_recordes),
                  ("SAIR", self.sair)]
        if self.partida.comecou:
            opcoes.insert(0, ("CONTINUAR", self.continuar))
        self._abrir(Estado.MENU, opcoes)

    def iniciar(self) -> None:
        """
        INICIAR, JOGAR e R. A partida guardada é descartada: não entra nos recordes e
        as moedas dela não vão para a carteira.
        """
        if self.partida.comecou:
            self.partida = Partida()
        self.estado = Estado.JOGANDO

    def continuar(self) -> None:
        """Volta para onde o ESC foi apertado, com a partida como estava."""
        self.estado = self.estado_anterior

    def ver_recordes(self) -> None:
        self._abrir(Estado.RECORDES, [("INICIO", self.voltar_ao_menu)])

    def ver_tutorial(self) -> None:
        self._abrir(Estado.TUTORIAL, [("INICIO", self.voltar_ao_menu)])

    def abrir_loja(self) -> None:
        """Uma opção por skin, e INICIO no fim. A seta começa na skin em uso."""
        opcoes = [(skin.nome, partial(self.escolher_skin, skin)) for skin in SKINS]
        self._abrir(Estado.LOJA, [*opcoes, ("INICIO", self.voltar_ao_menu)])
        self.menus[Estado.LOJA].escolhida = SKINS.index(self.loja.escolhida)

    def escolher_skin(self, skin: Skin) -> None:
        """Usa a skin; se ainda não é dela, compra antes. Sem moedas, o saldo fica vermelho."""
        if not self.loja.escolher(skin):
            self.aviso_saldo = AVISO_SEM_SALDO

    def voltar_ao_menu(self) -> None:
        self.estado = Estado.MENU   # a seta do menu continua onde estava

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

    # ------------------------------------------------------------------- janela
    def redimensionar(self, janela: 'glfw._GLFWwindowPointerT', largura: int,
                      altura: int) -> None:
        """Callback do GLFW quando a área de desenho muda de tamanho (em pixels)."""
        self.render.ajustar_viewport(largura, altura)

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        self.relogio += dt
        self.aviso_saldo = max(0.0, self.aviso_saldo - dt)
        if self.estado == Estado.JOGANDO:
            self.partida.atualizar(dt, self.direcao())
            if self.partida.terminou:
                self.posicao_recorde = self.recordes.registrar(self.partida.pontuacao)
                # Só a partida que chega ao fim guarda as moedas: abandonar não guarda.
                self.carteira.depositar(self.partida.moedas_coletadas)
                self._abrir(Estado.FIM, [("JOGAR", self.iniciar), ("INICIO", self.abrir_menu)])

    def desenhar(self) -> None:
        self.render.limpar(FUNDO)
        jogando = self.estado == Estado.JOGANDO
        self.render.atenuar(1.0 if jogando else ATENUACAO_FORA_DO_JOGO)
        if self.estado not in TELAS_SEM_CENA:
            self.partida.desenhar(self.render, self.loja.escolhida)

        # Daqui para baixo, coordenadas da tela e sem atenuação.
        self.render.usar_tela()
        self.render.atenuar(1.0)
        if self.estado in TELAS_DO_MENU:
            cor = COR_FIM if self.aviso_saldo else COR_MOEDA
            self.placar.desenhar_moedas(self.carteira.saldo, cor)
        else:
            self.placar.desenhar_hud(self.partida.pontuacao, self.partida.moedas_coletadas)
        match self.estado:
            case Estado.MENU:
                self.display.escrever(NOME_JOGO, 0.0, 0.48, 0.13, COR_DESTAQUE, 'centro')
                self._opcoes(0.12, 0.08)
            case Estado.LOJA:
                self.display.escrever(TEXTO_LOJA, 0.0, 0.74, 0.11, COR_DESTAQUE, 'centro')
                self.loja.desenhar(self.render, self.display, self.menus[Estado.LOJA].escolhida,
                                   0.52, self._pulso(), self.relogio)
            case Estado.RECORDES:
                self.recordes.desenhar(self.render, self.display, None, 0.45, self._pulso())
                self._opcoes(-0.45, 0.07)
            case Estado.TUTORIAL:
                self.display.escrever(TEXTO_TUTORIAL, 0.0, 0.74, 0.11, COR_DESTAQUE, 'centro')
                desenhar_tutorial(self.render, self.display, 0.52)
                self._opcoes(-0.86, 0.07)
            case Estado.PAUSADO:
                for lado in (-1.0, 1.0):
                    self.render.retangulo((0.06 * lado, 0.08), (0.07, 0.26), COR_PLACAR)
                self.display.escrever(TEXTO_PAUSA, 0.0, -0.22, 0.12, COR_PLACAR, 'centro')
            case Estado.FIM:
                self.display.escrever(TEXTO_FIM, 0.0, 0.70, 0.11, COR_FIM, 'centro')
                self.display.escrever(str(self.partida.pontuacao), 0.0, 0.48, 0.16,
                                      COR_PLACAR, 'centro')
                self.recordes.desenhar(self.render, self.display, self.posicao_recorde, 0.22,
                                       self._pulso())
                self._opcoes(-0.62, 0.07)
            case Estado.DIALOGO:
                # Caixa da cor do fundo: esconde a cena atrás das opções.
                self.render.retangulo((0.0, 0.0), (0.86, 0.54), FUNDO)
                self.render.contorno((0.0, 0.0), (0.86, 0.54), COR_FIM)
                self._opcoes(0.14, 0.07)

    def _opcoes(self, y: float, altura: float) -> None:
        menu = self.menus[self.estado]
        desenhar_opcoes(self.render, self.display, menu.textos, menu.escolhida, y, altura,
                        self._pulso())

    def _pulso(self) -> float:
        return 1.0 + 0.12 * np.sin(2.0 * np.pi * 1.2 * self.relogio)

    def titulo(self, fps: float) -> str:
        return (f"{NOME_JOGO} - {self.estado.value} - {self.partida.pontuacao} pts - "
                f"vsync {'on' if self.vsync else 'OFF'} - {fps:5.1f} fps")

    def liberar(self) -> None:
        self.render.liberar()
