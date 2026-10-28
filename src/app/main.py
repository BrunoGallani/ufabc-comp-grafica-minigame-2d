"""
Pula-Pula: minigame 2D vertical. O personagem quica sozinho nas plataformas,
a tela so sobe e cair pela borda de baixo encerra a partida.

Executar:
    python src/app/main.py

Teclas:
    ESQUERDA / DIREITA ou A / D   movem o personagem
    ENTER ou ESPACO               comeca a partida / joga de novo no fim
    P                             pausa e retoma
    R                             reinicia (volta ao inicio)
    V                             liga e desliga o vsync (fps na barra de titulo)
    ESC                           sai
"""
from jogo import Jogo


def main():
    Jogo().executar()


if __name__ == "__main__":
    main()
