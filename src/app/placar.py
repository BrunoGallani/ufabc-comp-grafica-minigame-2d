from config import (
    ALTURA_DIGITO_HUD, COR_MOEDA, COR_PLACAR, MEIA_ALTURA_TELA, MEIA_LARGURA_TELA,
    MOEDAS_ATIVAS,
)

# display de 7 segmentos: a topo, b/c direita, d base, e/f esquerda, g meio
SEGMENTOS = {
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
    '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
    'A': 'abcefg', 'B': 'cdefg', 'C': 'adef', 'D': 'bcdeg', 'E': 'adefg',
    'F': 'aefg', 'G': 'acdef', 'H': 'bcefg', 'I': 'ef', 'J': 'bcde',
    'L': 'def', 'N': 'ceg', 'O': 'abcdef', 'P': 'abefg', 'R': 'eg',
    'S': 'acdfg', 'T': 'defg', 'U': 'bcdef', 'Y': 'bcdfg', '-': 'g', ' ': '',
}

# proporcoes em relacao a altura do caractere
LARGURA_CARACTERE = 0.55
ESPESSURA_SEGMENTO = 0.16
ESPACO_CARACTERES = 0.30


def segmentos(cx, cy, altura):
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
    def __init__(self, render):
        self.render = render

    @staticmethod
    def largura(texto, altura):
        n = len(texto)
        return (n * LARGURA_CARACTERE + max(0, n - 1) * ESPACO_CARACTERES) * altura

    def escrever(self, texto, x, y, altura, cor, alinhamento='esquerda'):
        if alinhamento == 'centro':
            x -= self.largura(texto, altura) / 2
        elif alinhamento == 'direita':
            x -= self.largura(texto, altura)
        passo = (LARGURA_CARACTERE + ESPACO_CARACTERES) * altura
        for i, caractere in enumerate(texto.upper()):
            cx = x + LARGURA_CARACTERE * altura / 2 + i * passo
            posicoes = segmentos(cx, y, altura)
            for segmento in SEGMENTOS.get(caractere, ''):
                centro, tamanho = posicoes[segmento]
                self.render.retangulo(centro, tamanho, cor)

    def desenhar_hud(self, pontos, moedas):
        y = MEIA_ALTURA_TELA - 0.09
        self.escrever(str(pontos), -MEIA_LARGURA_TELA + 0.05, y, ALTURA_DIGITO_HUD, COR_PLACAR)
        if MOEDAS_ATIVAS:
            x = MEIA_LARGURA_TELA - 0.05
            self.escrever(str(moedas), x, y, ALTURA_DIGITO_HUD, COR_MOEDA, 'direita')
            x_icone = x - self.largura(str(moedas), ALTURA_DIGITO_HUD) - 0.045
            self.render.circulo((x_icone, y), 0.028, COR_MOEDA)
