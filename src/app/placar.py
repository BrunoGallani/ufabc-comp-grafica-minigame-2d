"""O placar na cena: os pontos no canto de cima à esquerda e as moedas à direita."""
from config import (
    ALTURA_DIGITO_HUD, COR_MOEDA, COR_PLACAR, MEIA_ALTURA_TELA, MEIA_LARGURA_TELA, Cor,
)
from display import Display

Y_PLACAR = MEIA_ALTURA_TELA - 0.09
MARGEM_PLACAR = 0.05   # das bordas da tela


class Placar:
    def __init__(self, display: Display) -> None:
        self.display = display

    def desenhar_hud(self, pontos: int, moedas: int) -> None:
        """Os pontos e as moedas da partida."""
        self.display.escrever(str(pontos), -MEIA_LARGURA_TELA + MARGEM_PLACAR, Y_PLACAR,
                              ALTURA_DIGITO_HUD, COR_PLACAR)
        self.desenhar_moedas(moedas, COR_MOEDA)

    def desenhar_moedas(self, moedas: int, cor: Cor) -> None:
        """Só as moedas, no canto da direita (nas telas do menu, as da carteira)."""
        self.display.escrever_moedas(moedas, MEIA_LARGURA_TELA - MARGEM_PLACAR, Y_PLACAR,
                                     ALTURA_DIGITO_HUD, cor, 'direita')
