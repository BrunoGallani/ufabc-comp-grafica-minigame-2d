"""
Display de 7 segmentos: letras e números feitos com o mesmo retângulo das
plataformas. Escreve o placar, os títulos e o texto de todas as telas.
"""
from config import COR_MOEDA, Cor, Par
from renderizador import Renderizador

# a topo, b/c direita, d base, e/f esquerda, g meio
SEGMENTOS = {
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
    '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
    'A': 'abcefg', 'B': 'cdefg', 'C': 'adef', 'D': 'bcdeg', 'E': 'adefg',
    'F': 'aefg', 'G': 'acdef', 'H': 'bcefg', 'I': 'ef', 'J': 'bcde',
    'L': 'def', 'N': 'ceg', 'O': 'abcdef', 'P': 'abefg', 'R': 'eg',
    'S': 'acdfg', 'T': 'defg', 'U': 'bcdef', 'Y': 'bcdfg', '-': 'g', ' ': '',
    'M': 'bcef',   # os lados; o meio vem de DIAGONAIS
}
# Em 7 segmentos o X sairia igual ao H, o V igual ao U, e o M nem existe: duas
# diagonais em escada completam o desenho. Os valores dizem onde elas terminam: o x
# em frações da meia largura (canto oposto -1, meio 0) e quanto descem, em frações da
# altura (até embaixo 1, até a metade 0.5).
DIAGONAIS = {'X': (-1.0, 1.0), 'V': (0.0, 1.0), 'M': (0.0, 0.5)}
DEGRAUS_DIAGONAL = 9
# As setas das teclas: um triângulo em fatias, com a ponta para o lado (dx, dy).
SETAS = {'←': (-1, 0), '→': (1, 0), '↑': (0, 1), '↓': (0, -1)}
FATIAS_SETA = 6

# Proporções em relação à altura do caractere.
LARGURA_CARACTERE = 0.55
ESPESSURA_SEGMENTO = 0.16
ESPACO_CARACTERES = 0.30
TAMANHO_SETA = 0.9
RAIO_ICONE_MOEDA = 0.4
ESPACO_ICONE_MOEDA = 0.25

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


class Display:
    def __init__(self, render: Renderizador) -> None:
        self.render = render

    @staticmethod
    def largura(texto: str, altura: float) -> float:
        n = len(texto)
        return (n * LARGURA_CARACTERE + max(0, n - 1) * ESPACO_CARACTERES) * altura

    def escrever(self, texto: str, x: float, y: float, altura: float, cor: Cor,
                 alinhamento: str = 'esquerda') -> None:
        """Escreve em coordenadas da tela; caractere desconhecido vira espaço."""
        x -= self.largura(texto, altura) * ALINHAMENTOS[alinhamento]
        primeiro = x + LARGURA_CARACTERE * altura / 2
        passo = (LARGURA_CARACTERE + ESPACO_CARACTERES) * altura
        for i, caractere in enumerate(texto.upper()):
            cx = primeiro + i * passo
            posicoes = segmentos(cx, y, altura)
            for segmento in SEGMENTOS.get(caractere, ''):
                self.render.retangulo(*posicoes[segmento], cor)
            if caractere in DIAGONAIS:
                self._diagonais(cx, y, altura, cor, *DIAGONAIS[caractere])
            if caractere in SETAS:
                self._seta(cx, y, altura, cor, SETAS[caractere])

    def _diagonais(self, cx: float, cy: float, altura: float, cor: Cor, fim: float,
                   descida: float) -> None:
        """
        Duas diagonais em escada, uma espelho da outra, com quadrados da espessura de
        um segmento. Descem dos cantos de cima até `fim` (fração da meia largura),
        percorrendo `descida` da altura.
        """
        lado = ESPESSURA_SEGMENTO * altura
        meia_largura, meia_altura = (LARGURA_CARACTERE * altura - lado) / 2, (altura - lado) / 2
        for k in range(DEGRAUS_DIAGONAL):
            t = k / (DEGRAUS_DIAGONAL - 1)   # de 0 (embaixo) a 1 (em cima)
            dx = meia_largura * (fim + (1.0 - fim) * t)
            dy = meia_altura * (1.0 - 2.0 * descida * (1.0 - t))
            self.render.retangulo((cx + dx, cy + dy), (lado, lado), cor)
            self.render.retangulo((cx - dx, cy + dy), (lado, lado), cor)

    def _seta(self, cx: float, cy: float, altura: float, cor: Cor,
              direcao: tuple[int, int]) -> None:
        """Triângulo em fatias do quadrado, cada uma mais estreita, da base até a ponta."""
        dx, dy = direcao
        tamanho = TAMANHO_SETA * altura
        espessura = tamanho / FATIAS_SETA
        for k in range(FATIAS_SETA):
            s = (k + 0.5) / FATIAS_SETA   # de perto da base (0) a perto da ponta (1)
            largura = tamanho * (1.0 - s)
            centro = (cx + dx * (s - 0.5) * tamanho, cy + dy * (s - 0.5) * tamanho)
            self.render.retangulo(centro, (espessura, largura) if dx else (largura, espessura),
                                  cor)

    def escrever_moedas(self, moedas: int, x: float, y: float, altura: float, cor: Cor,
                        alinhamento: str = 'esquerda') -> None:
        """O ícone de moeda e o número; o alinhamento vale para os dois juntos."""
        texto = str(moedas)
        raio = RAIO_ICONE_MOEDA * altura
        largura = 2 * raio + ESPACO_ICONE_MOEDA * altura + self.largura(texto, altura)
        x -= largura * ALINHAMENTOS[alinhamento]
        self.render.circulo((x + raio, y), raio, COR_MOEDA)
        self.escrever(texto, x + largura, y, altura, cor, 'direita')
