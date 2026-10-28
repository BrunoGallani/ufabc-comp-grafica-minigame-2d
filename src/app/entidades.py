import numpy as np

from config import (
    ALTURA_JOGADOR, ALTURA_PLATAFORMA, COR_FRAGIL, COR_FRAGIL_BORDA, COR_JOGADOR,
    COR_MOEDA, COR_MOEDA_MIOLO, COR_MOVEL, COR_NORMAL, COR_OLHO, COR_PUPILA,
    FLUTUACAO_MOEDA, GRAVIDADE, LARGURA_JOGADOR, MEIA_LARGURA_TELA, RAIO_MOEDA,
    VEL_GIRO_MOEDA, VEL_HORIZONTAL, VEL_PULO, VEL_QUEDA_MAX,
)


class Jogador:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vy = 0.0
        self.ultima_direcao = 1.0

    @property
    def pe(self):
        return self.y - ALTURA_JOGADOR / 2

    def atualizar(self, dt, direcao):
        self.x += direcao * VEL_HORIZONTAL * dt
        if direcao:
            self.ultima_direcao = direcao
        limite = MEIA_LARGURA_TELA + LARGURA_JOGADOR / 2
        if self.x > limite:
            self.x = -limite
        elif self.x < -limite:
            self.x = limite

        # velocidade media do passo: exata com aceleracao constante, entao a
        # altura do pulo nao depende do fps
        vy_nova = max(self.vy - GRAVIDADE * dt, -VEL_QUEDA_MAX)
        self.y += 0.5 * (self.vy + vy_nova) * dt
        self.vy = vy_nova

    def quicar(self, topo):
        self.y = topo + ALTURA_JOGADOR / 2
        self.vy = VEL_PULO

    def desenhar(self, render):
        render.retangulo((self.x, self.y), (LARGURA_JOGADOR, ALTURA_JOGADOR), COR_JOGADOR)
        olhar_x = 0.008 * self.ultima_direcao
        olhar_y = 0.006 * max(-1.0, min(1.0, self.vy / VEL_PULO))
        for lado in (-1.0, 1.0):
            olho = (self.x + lado * 0.026, self.y + 0.025)
            render.circulo(olho, 0.02, COR_OLHO)
            render.circulo((olho[0] + olhar_x, olho[1] + olhar_y), 0.01, COR_PUPILA)


class Plataforma:
    NORMAL, MOVEL, FRAGIL = "normal", "movel", "fragil"

    def __init__(self, x, y, largura, tipo=NORMAL, velocidade=0.0):
        self.x, self.y = x, y
        self.largura = largura
        self.tipo = tipo
        self.velocidade = velocidade
        self.quebrada = False

    @property
    def topo(self):
        return self.y + ALTURA_PLATAFORMA / 2

    def atualizar(self, dt):
        if self.tipo != Plataforma.MOVEL:
            return
        self.x += self.velocidade * dt
        limite = MEIA_LARGURA_TELA - self.largura / 2
        if abs(self.x) > limite:
            self.x = max(-limite, min(limite, self.x))
            self.velocidade = -self.velocidade

    def desenhar(self, render):
        tamanho = (self.largura, ALTURA_PLATAFORMA)
        if self.tipo == Plataforma.FRAGIL:
            render.retangulo((self.x, self.y), tamanho, COR_FRAGIL)
            render.contorno((self.x, self.y), tamanho, COR_FRAGIL_BORDA)
        else:
            cor = COR_MOVEL if self.tipo == Plataforma.MOVEL else COR_NORMAL
            render.retangulo((self.x, self.y), tamanho, cor)


class Moeda:
    def __init__(self, x, y, fase=0.0):
        self.x, self.y = x, y
        self.tempo = fase
        self.coletada = False

    def atualizar(self, dt):
        self.tempo += dt

    @property
    def centro(self):
        return (self.x, self.y + FLUTUACAO_MOEDA * np.sin(2.0 * self.tempo))

    def desenhar(self, render):
        giro = max(0.15, abs(np.cos(VEL_GIRO_MOEDA * self.tempo)))
        render.elipse(self.centro, (RAIO_MOEDA * giro, RAIO_MOEDA), COR_MOEDA)
        render.elipse(self.centro, (0.55 * RAIO_MOEDA * giro, 0.55 * RAIO_MOEDA),
                      COR_MOEDA_MIOLO)
