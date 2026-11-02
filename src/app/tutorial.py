"""
Tela de tutorial: as teclas que controlam o jogo e o que cada uma faz, escritas com
o display de 7 segmentos e com o contorno do quadrado em volta de cada tecla.
"""
from config import COR_PLACAR
from display import Display
from renderizador import Renderizador

# As teclas de cada ação (separadas por espaço; "/" separa as alternativas, escritas
# com OU entre elas) e o que a ação faz. Primeiro as da partida, depois as dos menus
# e as da janela.
TECLAS = (
    ("← →/A D", "ANDA"), ("P", "PAUSA"), ("R", "REINICIA"), ("ESC", "SAIR"),
    ("↑ ↓", "NAVEGA"), ("ENTER/ESPACO", "CONFIRMA"), ("F", "TELA CHEIA"), ("V", "VSYNC"),
)
ESPACO_LINHAS = 0.16
X_TECLAS, X_ACOES = -0.52, 0.10
ALTURA_ACAO = 0.05
ALTURA_TECLA, ALTURA_NOME_TECLA, MARGEM_TECLA = 0.085, 0.04, 0.02
ESPACO_TECLAS = 0.025


def desenhar_tutorial(render: Renderizador, display: Display, y: float) -> None:
    """
    Uma ação por linha, a partir de `y` para baixo: as teclas, com OU entre as
    alternativas, e numa coluna à direita o que elas fazem.
    """
    for i, (teclas, acao) in enumerate(TECLAS):
        y_linha = y - ESPACO_LINHAS * i
        x = X_TECLAS   # borda esquerda da próxima tecla
        for j, alternativa in enumerate(teclas.split('/')):
            if j:
                display.escrever("OU", x, y_linha, ALTURA_ACAO, COR_PLACAR)
                x += display.largura("OU", ALTURA_ACAO) + ESPACO_TECLAS
            for nome in alternativa.split():
                x += _tecla(render, display, nome, x, y_linha) + ESPACO_TECLAS
        display.escrever(acao, X_ACOES, y_linha, ALTURA_ACAO, COR_PLACAR)


def _tecla(render: Renderizador, display: Display, nome: str, x: float, y: float) -> float:
    """Uma tecla com a borda esquerda em `x`: o contorno e o nome dentro. Devolve a largura."""
    largura = max(ALTURA_TECLA, display.largura(nome, ALTURA_NOME_TECLA) + 2 * MARGEM_TECLA)
    render.contorno((x + largura / 2, y), (largura, ALTURA_TECLA), COR_PLACAR)
    display.escrever(nome, x + largura / 2, y, ALTURA_NOME_TECLA, COR_PLACAR, 'centro')
    return largura
