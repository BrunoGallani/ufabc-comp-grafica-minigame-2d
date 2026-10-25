def sobrepoe_intervalo(centro1, largura1, centro2, largura2):
    return abs(centro1 - centro2) < (largura1 + largura2) / 2


def cruzou_topo(pe_antes, pe_agora, topo):
    # teste de varredura: detecta a travessia mesmo se v * dt passar da espessura
    return pe_antes >= topo > pe_agora


def circulo_toca_retangulo(centro, raio, centro_ret, tamanho_ret):
    meia_largura, meia_altura = tamanho_ret[0] / 2, tamanho_ret[1] / 2
    # ponto do retangulo mais proximo do centro do circulo
    px = max(centro_ret[0] - meia_largura, min(centro[0], centro_ret[0] + meia_largura))
    py = max(centro_ret[1] - meia_altura, min(centro[1], centro_ret[1] + meia_altura))
    dx, dy = centro[0] - px, centro[1] - py
    return dx * dx + dy * dy < raio * raio
