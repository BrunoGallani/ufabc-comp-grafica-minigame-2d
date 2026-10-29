"""Testes de colisão do jogo, em funções puras (sem estado, fáceis de testar)."""
from config import Par


def sobrepoe_intervalo(centro1: float, largura1: float, centro2: float, largura2: float) -> bool:
    """Dois intervalos (centro, largura) num mesmo eixo se sobrepõem?"""
    return abs(centro1 - centro2) < (largura1 + largura2) / 2


def cruzou_topo(pe_antes: float, pe_agora: float, topo: float) -> bool:
    """
    Teste de varredura: o pé desceu através do topo neste passo? Pega a travessia
    mesmo quando v * dt passa da espessura da plataforma, e ignora quem sobe.
    """
    return pe_antes >= topo > pe_agora


def circulo_toca_retangulo(centro: Par, raio: float, centro_ret: Par, tamanho_ret: Par) -> bool:
    meia_largura, meia_altura = tamanho_ret[0] / 2, tamanho_ret[1] / 2
    # Ponto do retângulo mais próximo do centro do círculo.
    px = max(centro_ret[0] - meia_largura, min(centro[0], centro_ret[0] + meia_largura))
    py = max(centro_ret[1] - meia_altura, min(centro[1], centro_ret[1] + meia_altura))
    dx, dy = centro[0] - px, centro[1] - py
    return dx * dx + dy * dy < raio * raio
