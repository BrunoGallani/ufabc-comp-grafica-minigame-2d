"""
Uma partida: o mundo infinito (plataformas geradas acima da tela e descartadas
abaixo), a física do jogador, as colisões e a câmera.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np

from colisao import circulo_toca_retangulo, cruzou_topo, sobrepoe_intervalo
from config import (
    ALTURA_DIFICULDADE_MAX, ALTURA_JOGADOR, ALTURA_MOEDA, BONUS_MOEDA, CAMERA_ACELERACAO,
    CAMERA_ATRASO, CAMERA_VEL_MAX, CHANCE_FRAGIL, CHANCE_MOEDA, CHANCE_MOLA, CHANCE_MOVEL,
    COR_GRADE, ESPACO_GRADE, ESPACO_MAX, ESPACO_MIN, LARGURA_JOGADOR, LARGURA_MOLA,
    LARGURA_PLATAFORMA, LINHA_CAMERA, MARGEM_GERACAO, MEIA_ALTURA_TELA, MEIA_LARGURA_TELA,
    MOEDAS_ATIVAS, PONTOS_POR_UNIDADE, RAIO_MOEDA, VEL_MOVEL, Y_BASE, Par,
)
from entidades import Jogador, Moeda, Mola, Plataforma, TipoPlataforma

if TYPE_CHECKING:
    from renderizador import Renderizador


def interpolar(par: Par, t: float) -> float:
    """Valor entre o (fácil, difícil) do par; t vai de 0 a 1."""
    facil, dificil = par
    return facil + (dificil - facil) * t


class Partida:
    def __init__(self, semente: int | None = None) -> None:
        self.aleatorio = random.Random(semente)
        self.tempo = 0.0
        self.camera_y = 0.0
        self.altura_max = 0.0
        self.moedas_coletadas = 0
        self.terminou = False

        base = Plataforma(0.0, Y_BASE, 2 * MEIA_LARGURA_TELA)
        self.plataformas = [base]
        self.moedas: list[Moeda] = []
        self.jogador = Jogador(0.0, base.topo + ALTURA_JOGADOR / 2)
        self.y_inicial = self.jogador.y
        self.y_ultima = base.y
        self._gerar_acima()

    @property
    def pontuacao(self) -> int:
        return int(self.altura_max * PONTOS_POR_UNIDADE) + BONUS_MOEDA * self.moedas_coletadas

    def dificuldade(self, y: float) -> float:
        """De 0 na base a 1 em ALTURA_DIFICULDADE_MAX."""
        return min(1.0, max(0.0, (y - Y_BASE) / ALTURA_DIFICULDADE_MAX))

    def velocidade_camera(self) -> float:
        """Parada até CAMERA_ATRASO, depois cresce com o tempo até CAMERA_VEL_MAX."""
        return min(CAMERA_VEL_MAX, max(0.0, self.tempo - CAMERA_ATRASO) * CAMERA_ACELERACAO)

    def atualizar(self, dt: float, direcao: float) -> None:
        self.tempo += dt
        for plataforma in self.plataformas:
            plataforma.atualizar(dt)
        for moeda in self.moedas:
            moeda.atualizar(dt)

        y_antes, pe_antes = self.jogador.y, self.jogador.pe
        self.jogador.atualizar(dt, direcao)
        self._testar_pouso(pe_antes)
        self._testar_moedas(y_antes)

        # A câmera só sobe: sozinha ou acompanhando o jogador.
        self.camera_y = max(self.camera_y + self.velocidade_camera() * dt,
                            self.jogador.y - LINHA_CAMERA)
        self._gerar_acima()
        self._descartar_abaixo()

        self.altura_max = max(self.altura_max, self.jogador.y - self.y_inicial)
        if self.jogador.y + ALTURA_JOGADOR / 2 < self.camera_y - MEIA_ALTURA_TELA:
            self.terminou = True

    def _testar_pouso(self, pe_antes: float) -> None:
        j = self.jogador
        # A mola fica acima da plataforma, então na queda ela é tocada primeiro.
        superficies = self.plataformas + [p.mola for p in self.plataformas if p.mola]
        tocadas = [s for s in superficies
                   if cruzou_topo(pe_antes, j.pe, s.topo)
                   and sobrepoe_intervalo(j.x, LARGURA_JOGADOR, s.x, s.largura)]
        if tocadas:
            max(tocadas, key=lambda s: s.topo).pisar(j)   # a primeira tocada na queda

    def _testar_moedas(self, y_antes: float) -> None:
        # Corpo varrido entre o quadro anterior e o atual: no impulso da mola o passo
        # vertical passa do tamanho da moeda, e sem isso ela poderia ser atravessada.
        y = self.jogador.y
        corpo = (self.jogador.x, (y_antes + y) / 2)
        tamanho = (LARGURA_JOGADOR, ALTURA_JOGADOR + abs(y - y_antes))
        for moeda in self.moedas:
            if circulo_toca_retangulo(moeda.centro, RAIO_MOEDA, corpo, tamanho):
                moeda.coletada = True
                self.moedas_coletadas += 1

    def _gerar_acima(self) -> None:
        while self.y_ultima < self.camera_y + MEIA_ALTURA_TELA + MARGEM_GERACAO:
            d = self.dificuldade(self.y_ultima)
            y = self.y_ultima + self.aleatorio.uniform(interpolar(ESPACO_MIN, d),
                                                       interpolar(ESPACO_MAX, d))
            plataforma = self._sortear_plataforma(y, d)
            self.plataformas.append(plataforma)
            self.y_ultima = y

            if MOEDAS_ATIVAS and self.aleatorio.random() < CHANCE_MOEDA:
                fase = self.aleatorio.uniform(0.0, 3.0)
                self.moedas.append(Moeda(plataforma.x, y + ALTURA_MOEDA, fase))

    def _sortear_plataforma(self, y: float, d: float) -> Plataforma:
        largura = interpolar(LARGURA_PLATAFORMA, d)
        limite = MEIA_LARGURA_TELA - largura / 2
        x = self.aleatorio.uniform(-limite, limite)

        sorte = self.aleatorio.random()
        chance_movel = interpolar(CHANCE_MOVEL, d)
        if sorte < chance_movel:
            velocidade = interpolar(VEL_MOVEL, d) * self.aleatorio.choice((-1.0, 1.0))
            plataforma = Plataforma(x, y, largura, TipoPlataforma.MOVEL, velocidade)
        elif sorte < chance_movel + interpolar(CHANCE_FRAGIL, d):
            return Plataforma(x, y, largura, TipoPlataforma.FRAGIL)   # frágil não tem mola
        else:
            plataforma = Plataforma(x, y, largura)

        if self.aleatorio.random() < interpolar(CHANCE_MOLA, d):
            folga = (largura - LARGURA_MOLA) / 2
            plataforma.mola = Mola(plataforma, self.aleatorio.uniform(-folga, folga))
        return plataforma

    def _descartar_abaixo(self) -> None:
        limite = self.camera_y - MEIA_ALTURA_TELA - MARGEM_GERACAO
        self.plataformas = [p for p in self.plataformas if p.y > limite and not p.quebrada]
        self.moedas = [m for m in self.moedas if m.y > limite and not m.coletada]

    def desenhar(self, render: Renderizador) -> None:
        render.usar_camera(self.camera_y)
        primeira = int(np.floor((self.camera_y - MEIA_ALTURA_TELA) / ESPACO_GRADE))
        ultima = int(np.ceil((self.camera_y + MEIA_ALTURA_TELA) / ESPACO_GRADE))
        for k in range(primeira, ultima + 1):
            render.retangulo((0.0, k * ESPACO_GRADE), (2 * MEIA_LARGURA_TELA, 0.004), COR_GRADE)
        for objeto in (*self.plataformas, *self.moedas, self.jogador):
            objeto.desenhar(render)
