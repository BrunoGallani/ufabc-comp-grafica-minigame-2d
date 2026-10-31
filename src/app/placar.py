"""
Texto em display de 7 segmentos, feito com o mesmo retângulo das plataformas:
o placar do HUD, os títulos das telas, as listas de opções e a tabela de recordes.
"""
from config import (
    ALTURA_DIGITO_HUD, COR_DESTAQUE, COR_MOEDA, COR_PLACAR, MEIA_ALTURA_TELA,
    MEIA_LARGURA_TELA, MOEDAS_ATIVAS, TEXTO_RECORDES, TOTAL_RECORDES, Cor, Par,
)
from renderizador import Renderizador

# a topo, b/c direita, d base, e/f esquerda, g meio
SEGMENTOS = {
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
    '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
    'A': 'abcefg', 'B': 'cdefg', 'C': 'adef', 'D': 'bcdeg', 'E': 'adefg',
    'F': 'aefg', 'G': 'acdef', 'H': 'bcefg', 'I': 'ef', 'J': 'bcde',
    'L': 'def', 'N': 'ceg', 'O': 'abcdef', 'P': 'abefg', 'R': 'eg',
    'S': 'acdfg', 'T': 'defg', 'U': 'bcdef', 'Y': 'bcdfg', '-': 'g', ' ': '',
}

# Proporções em relação à altura do caractere.
LARGURA_CARACTERE = 0.55
ESPESSURA_SEGMENTO = 0.16
ESPACO_CARACTERES = 0.30
ENTRELINHA = 2.0

# Quanto da largura do texto fica à esquerda do x pedido.
ALINHAMENTOS = {'esquerda': 0.0, 'centro': 0.5, 'direita': 1.0}


def segmentos(cx: float, cy: float, altura: float) -> dict[str, tuple[Par, Par]]:
    """(centro, tamanho) de cada segmento de um caractere centrado em (cx, cy)."""
    largura, espessura = LARGURA_CARACTERE * altura, ESPESSURA_SEGMENTO * altura
    horizontal, vertical = (largura, espessura), (espessura, altura / 2)
    dx, dy = (largura - espessura) / 2, (altura - espessura) / 2
    return {
        'a': ((cx, cy + dy), horizontal),
        'b': ((cx + dx, cy + altura / 4), vertical),
        'c': ((cx + dx, cy - altura / 4), vertical),
        'd': ((cx, cy - dy), horizontal),
        'e': ((cx - dx, cy - altura / 4), vertical),
        'f': ((cx - dx, cy + altura / 4), vertical),
        'g': ((cx, cy), horizontal),
    }


class Placar:
    def __init__(self, render: Renderizador) -> None:
        self.render = render

    @staticmethod
    def largura(texto: str, altura: float) -> float:
        n = len(texto)
        return (n * LARGURA_CARACTERE + max(0, n - 1) * ESPACO_CARACTERES) * altura

    def escrever(self, texto: str, x: float, y: float, altura: float, cor: Cor,
                 alinhamento: str = 'esquerda') -> None:
        """Escreve em coordenadas da tela; caractere fora de SEGMENTOS vira espaço."""
        x -= self.largura(texto, altura) * ALINHAMENTOS[alinhamento]
        primeiro = x + LARGURA_CARACTERE * altura / 2
        passo = (LARGURA_CARACTERE + ESPACO_CARACTERES) * altura
        for i, caractere in enumerate(texto.upper()):
            posicoes = segmentos(primeiro + i * passo, y, altura)
            for segmento in SEGMENTOS.get(caractere, ''):
                self.render.retangulo(*posicoes[segmento], cor)

    def desenhar_hud(self, pontos: int, moedas: int) -> None:
        y = MEIA_ALTURA_TELA - 0.09
        self.escrever(str(pontos), -MEIA_LARGURA_TELA + 0.05, y, ALTURA_DIGITO_HUD, COR_PLACAR)
        if MOEDAS_ATIVAS:
            x = MEIA_LARGURA_TELA - 0.05
            self.escrever(str(moedas), x, y, ALTURA_DIGITO_HUD, COR_MOEDA, 'direita')
            x_icone = x - self.largura(str(moedas), ALTURA_DIGITO_HUD) - 0.045
            self.render.circulo((x_icone, y), 0.028, COR_MOEDA)

    def desenhar_opcoes(self, textos: list[str], escolhida: int, y: float, altura: float,
                        pulso: float) -> None:
        """
        Uma opção por linha, a partir de `y` para baixo, alinhadas à esquerda e com o
        bloco centrado na tela. A escolhida ganha a cor de destaque e uma seta pulsando.
        """
        x = -max(self.largura(texto, altura) for texto in textos) / 2
        for i, texto in enumerate(textos):
            y_linha = y - ENTRELINHA * altura * i
            cor = COR_DESTAQUE if i == escolhida else COR_PLACAR
            self.escrever(texto, x, y_linha, altura, cor)
            if i == escolhida:
                self.render.triangulo((x - 1.5 * altura, y_linha), altura * pulso, cor)

    def desenhar_recordes(self, pontos: list[int], destaque: int | None, y: float,
                          pulso: float) -> None:
        """
        Tabela com as posições vazias como "-". A linha `destaque` (a da partida que
        acabou) ganha a cor de destaque e uma seta pulsando.
        """
        self.escrever(TEXTO_RECORDES, 0.0, y, 0.07, COR_DESTAQUE, 'centro')
        for i in range(TOTAL_RECORDES):
            y_linha = y - 0.16 - 0.12 * i
            cor = COR_DESTAQUE if i == destaque else COR_PLACAR
            texto = str(pontos[i]) if i < len(pontos) else '-'
            self.escrever(str(i + 1), -0.28, y_linha, 0.06, cor)
            self.escrever(texto, 0.32, y_linha, 0.06, cor, 'direita')
            if i == destaque:
                self.render.triangulo((-0.38, y_linha), 0.07 * pulso, cor)
