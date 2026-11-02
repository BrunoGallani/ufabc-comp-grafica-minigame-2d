"""
Texto em display de 7 segmentos, feito com o mesmo retângulo das plataformas:
o placar do HUD, os títulos das telas, as listas de opções, a tabela de recordes
e a vitrine da loja.
"""
from config import (
    ALTURA_DIGITO_HUD, COR_DESTAQUE, COR_FIM, COR_MOEDA, COR_PLACAR, ESCALA_VITRINE,
    MEIA_ALTURA_TELA, MEIA_LARGURA_TELA, TEXTO_RECORDES, TOTAL_RECORDES, Cor, Par,
)
from entidades import desenhar_personagem
from loja import Loja
from renderizador import Renderizador
from skins import SKINS

# a topo, b/c direita, d base, e/f esquerda, g meio
SEGMENTOS = {
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
    '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
    'A': 'abcefg', 'B': 'cdefg', 'C': 'adef', 'D': 'bcdeg', 'E': 'adefg',
    'F': 'aefg', 'G': 'acdef', 'H': 'bcefg', 'I': 'ef', 'J': 'bcde',
    'L': 'def', 'N': 'ceg', 'O': 'abcdef', 'P': 'abefg', 'R': 'eg',
    'S': 'acdfg', 'T': 'defg', 'U': 'bcdef', 'Y': 'bcdfg', '-': 'g', ' ': '',
}
# Em 7 segmentos o X sairia igual ao H: ele é desenhado à parte, em diagonais.
LETRA_X = 'X'
DEGRAUS_X = 9

# Proporções em relação à altura do caractere.
LARGURA_CARACTERE = 0.55
ESPESSURA_SEGMENTO = 0.16
ESPACO_CARACTERES = 0.30
ENTRELINHA = 2.0
RAIO_ICONE_MOEDA = 0.4
ESPACO_ICONE_MOEDA = 0.25

ESPACO_LINHAS_LOJA = 0.21

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
            if caractere == LETRA_X:
                self._xis(primeiro + i * passo, y, altura, cor)
                continue
            posicoes = segmentos(primeiro + i * passo, y, altura)
            for segmento in SEGMENTOS.get(caractere, ''):
                self.render.retangulo(*posicoes[segmento], cor)

    def _xis(self, cx: float, cy: float, altura: float, cor: Cor) -> None:
        """Duas diagonais em escada, com quadrados da espessura de um segmento."""
        lado = ESPESSURA_SEGMENTO * altura
        for k in range(DEGRAUS_X):
            t = k / (DEGRAUS_X - 1) - 0.5   # de -0.5 a 0.5, de baixo para cima
            dx, dy = t * (LARGURA_CARACTERE * altura - lado), t * (altura - lado)
            self.render.retangulo((cx + dx, cy + dy), (lado, lado), cor)
            self.render.retangulo((cx - dx, cy + dy), (lado, lado), cor)

    def escrever_moedas(self, moedas: int, x: float, y: float, altura: float, cor: Cor,
                        alinhamento: str = 'esquerda') -> None:
        """O ícone de moeda e o número; o alinhamento vale para os dois juntos."""
        texto = str(moedas)
        raio = RAIO_ICONE_MOEDA * altura
        largura = 2 * raio + ESPACO_ICONE_MOEDA * altura + self.largura(texto, altura)
        x -= largura * ALINHAMENTOS[alinhamento]
        self.render.circulo((x + raio, y), raio, COR_MOEDA)
        self.escrever(texto, x + largura, y, altura, cor, 'direita')

    def desenhar_hud(self, pontos: int, moedas: int) -> None:
        """Pontos no canto de cima à esquerda e moedas à direita."""
        y = MEIA_ALTURA_TELA - 0.09
        self.escrever(str(pontos), -MEIA_LARGURA_TELA + 0.05, y, ALTURA_DIGITO_HUD, COR_PLACAR)
        self.desenhar_moedas(moedas, COR_MOEDA)

    def desenhar_moedas(self, moedas: int, cor: Cor) -> None:
        self.escrever_moedas(moedas, MEIA_LARGURA_TELA - 0.05, MEIA_ALTURA_TELA - 0.09,
                             ALTURA_DIGITO_HUD, cor, 'direita')

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

    def desenhar_loja(self, loja: Loja, escolhida: int, y: float, pulso: float,
                      tempo: float) -> None:
        """
        Uma skin por linha, a partir de `y` para baixo: o personagem com ela, o nome
        e o preço (USAR se já foi comprada, USANDO na escolhida). Embaixo, INICIO.
        A linha `escolhida` é a da seta, e `tempo` anima as estampas.
        """
        for i, skin in enumerate(SKINS):
            y_linha = y - ESPACO_LINHAS_LOJA * i
            cor = COR_DESTAQUE if i == escolhida else COR_PLACAR
            if i == escolhida:
                self.render.triangulo((-0.52, y_linha), 0.06 * pulso, cor)
            desenhar_personagem(self.render, (-0.39, y_linha), skin, tempo, escala=ESCALA_VITRINE)
            self.escrever(skin.nome, -0.26, y_linha, 0.055, cor)
            if skin == loja.escolhida:
                self.escrever("USANDO", 0.55, y_linha, 0.05, COR_DESTAQUE, 'direita')
            elif skin in loja.compradas:
                self.escrever("USAR", 0.55, y_linha, 0.05, COR_PLACAR, 'direita')
            else:
                cor_preco = COR_MOEDA if skin.preco <= loja.carteira.saldo else COR_FIM
                self.escrever_moedas(skin.preco, 0.55, y_linha, 0.055, cor_preco, 'direita')
        # Depois das skins vem o INICIO: a seta está nele quando escolhida == len(SKINS).
        self.desenhar_opcoes(["INICIO"], escolhida - len(SKINS),
                             y - ESPACO_LINHAS_LOJA * len(SKINS), 0.07, pulso)
