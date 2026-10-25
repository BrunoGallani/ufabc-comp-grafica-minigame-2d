import random

import numpy as np

from colisao import circulo_toca_retangulo, cruzou_topo, sobrepoe_intervalo
from config import (
    ALTURA_DIFICULDADE_MAX, ALTURA_JOGADOR, ALTURA_MOEDA, BONUS_MOEDA, CAMERA_ACELERACAO,
    CAMERA_ATRASO, CAMERA_VEL_MAX, CHANCE_FRAGIL, CHANCE_MOEDA, CHANCE_MOVEL, COR_GRADE,
    ESPACO_GRADE, ESPACO_MAX, ESPACO_MIN, LARGURA_JOGADOR, LARGURA_PLATAFORMA,
    LINHA_CAMERA, MARGEM_GERACAO, MEIA_ALTURA_TELA, MEIA_LARGURA_TELA, MOEDAS_ATIVAS,
    PONTOS_POR_UNIDADE, RAIO_MOEDA, VEL_MOVEL, Y_BASE,
)
from entidades import Jogador, Moeda, Plataforma


def interpolar(par, t):
    facil, dificil = par
    return facil + (dificil - facil) * t


class Partida:
    def __init__(self, semente=None):
        self.aleatorio = random.Random(semente)
        self.tempo = 0.0
        self.camera_y = 0.0
        self.altura_max = 0.0
        self.moedas_coletadas = 0
        self.terminou = False

        base = Plataforma(0.0, Y_BASE, 2 * MEIA_LARGURA_TELA)
        self.plataformas = [base]
        self.moedas = []
        self.jogador = Jogador(0.0, base.topo + ALTURA_JOGADOR / 2)
        self.y_inicial = self.jogador.y
        self.y_ultima = base.y
        self._gerar_acima()

    @property
    def pontuacao(self):
        return int(self.altura_max * PONTOS_POR_UNIDADE) + BONUS_MOEDA * self.moedas_coletadas

    def dificuldade(self, y):
        return min(1.0, max(0.0, (y - Y_BASE) / ALTURA_DIFICULDADE_MAX))

    def velocidade_camera(self):
        return min(CAMERA_VEL_MAX, max(0.0, self.tempo - CAMERA_ATRASO) * CAMERA_ACELERACAO)

    def atualizar(self, dt, direcao):
        self.tempo += dt
        for plataforma in self.plataformas:
            plataforma.atualizar(dt)
        for moeda in self.moedas:
            moeda.atualizar(dt)

        pe_antes = self.jogador.pe
        self.jogador.atualizar(dt, direcao)
        self._testar_pouso(pe_antes)
        self._testar_moedas()

        self.camera_y = max(self.camera_y + self.velocidade_camera() * dt,
                            self.jogador.y - LINHA_CAMERA)
        self._gerar_acima()
        self._descartar_abaixo()

        self.altura_max = max(self.altura_max, self.jogador.y - self.y_inicial)
        if self.jogador.y + ALTURA_JOGADOR / 2 < self.camera_y - MEIA_ALTURA_TELA:
            self.terminou = True

    def _testar_pouso(self, pe_antes):
        j = self.jogador
        tocadas = [p for p in self.plataformas
                   if cruzou_topo(pe_antes, j.pe, p.topo)
                   and sobrepoe_intervalo(j.x, LARGURA_JOGADOR, p.x, p.largura)]
        if not tocadas:
            return
        plataforma = max(tocadas, key=lambda p: p.topo)  # a primeira tocada na queda
        j.quicar(plataforma.topo)
        if plataforma.tipo == Plataforma.FRAGIL:
            plataforma.quebrada = True

    def _testar_moedas(self):
        corpo = (self.jogador.x, self.jogador.y)
        tamanho = (LARGURA_JOGADOR, ALTURA_JOGADOR)
        for moeda in self.moedas:
            if circulo_toca_retangulo(moeda.centro, RAIO_MOEDA, corpo, tamanho):
                moeda.coletada = True
                self.moedas_coletadas += 1

    def _gerar_acima(self):
        while self.y_ultima < self.camera_y + MEIA_ALTURA_TELA + MARGEM_GERACAO:
            d = self.dificuldade(self.y_ultima)
            y = self.y_ultima + self.aleatorio.uniform(interpolar(ESPACO_MIN, d),
                                                       interpolar(ESPACO_MAX, d))
            largura = interpolar(LARGURA_PLATAFORMA, d)
            limite = MEIA_LARGURA_TELA - largura / 2
            x = self.aleatorio.uniform(-limite, limite)

            sorte = self.aleatorio.random()
            chance_movel = interpolar(CHANCE_MOVEL, d)
            if sorte < chance_movel:
                velocidade = interpolar(VEL_MOVEL, d) * self.aleatorio.choice((-1.0, 1.0))
                plataforma = Plataforma(x, y, largura, Plataforma.MOVEL, velocidade)
            elif sorte < chance_movel + interpolar(CHANCE_FRAGIL, d):
                plataforma = Plataforma(x, y, largura, Plataforma.FRAGIL)
            else:
                plataforma = Plataforma(x, y, largura)
            self.plataformas.append(plataforma)
            self.y_ultima = y

            if MOEDAS_ATIVAS and self.aleatorio.random() < CHANCE_MOEDA:
                self.moedas.append(Moeda(x, y + ALTURA_MOEDA, self.aleatorio.uniform(0.0, 3.0)))

    def _descartar_abaixo(self):
        limite = self.camera_y - MEIA_ALTURA_TELA - MARGEM_GERACAO
        self.plataformas = [p for p in self.plataformas if p.y > limite and not p.quebrada]
        self.moedas = [m for m in self.moedas if m.y > limite and not m.coletada]

    def desenhar(self, render):
        render.usar_camera(self.camera_y)
        primeira = int(np.floor((self.camera_y - MEIA_ALTURA_TELA) / ESPACO_GRADE))
        ultima = int(np.ceil((self.camera_y + MEIA_ALTURA_TELA) / ESPACO_GRADE))
        for k in range(primeira, ultima + 1):
            render.retangulo((0.0, k * ESPACO_GRADE), (2 * MEIA_LARGURA_TELA, 0.004), COR_GRADE)
        for plataforma in self.plataformas:
            plataforma.desenhar(render)
        for moeda in self.moedas:
            moeda.desenhar(render)
        self.jogador.desenhar(render)
