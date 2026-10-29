"""
Tudo que aparece no mundo: jogador, plataformas, molas e moedas. Cada um se
atualiza e se desenha; quem decide quando é a Partida.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from config import (
    ALTURA_JOGADOR, ALTURA_MOLA, ALTURA_MOLA_ESTICADA, ALTURA_PLATAFORMA, COR_FRAGIL,
    COR_FRAGIL_BORDA, COR_JOGADOR, COR_MOEDA, COR_MOEDA_MIOLO, COR_MOLA, COR_MOLA_TAMPA,
    COR_MOVEL, COR_NORMAL, COR_OLHO, COR_PUPILA, ESPESSURA_TAMPA_MOLA, FLUTUACAO_MOEDA,
    GRAVIDADE, LARGURA_JOGADOR, LARGURA_MOLA, MEIA_LARGURA_TELA, PIXEL, RAIO_MOEDA,
    VEL_GIRO_MOEDA, VEL_HORIZONTAL, VEL_MOLA, VEL_PULO, VEL_QUEDA_MAX, Par,
)

if TYPE_CHECKING:
    from renderizador import Renderizador

# O jogador só reaparece do outro lado depois de sair inteiro da tela.
LIMITE_X_JOGADOR = MEIA_LARGURA_TELA + LARGURA_JOGADOR / 2


@dataclass(eq=False)
class Jogador:
    x: float
    y: float
    vy: float = 0.0
    ultima_direcao: float = 1.0   # para onde os olhos apontam

    @property
    def pe(self) -> float:
        return self.y - ALTURA_JOGADOR / 2

    def atualizar(self, dt: float, direcao: float) -> None:
        self.x += direcao * VEL_HORIZONTAL * dt
        if direcao:
            self.ultima_direcao = direcao
        if abs(self.x) > LIMITE_X_JOGADOR:
            self.x = -LIMITE_X_JOGADOR if self.x > 0 else LIMITE_X_JOGADOR

        # Velocidade média do passo: exata com aceleração constante, então a altura
        # do pulo não depende do fps.
        vy_nova = max(self.vy - GRAVIDADE * dt, -VEL_QUEDA_MAX)
        self.y += 0.5 * (self.vy + vy_nova) * dt
        self.vy = vy_nova

    def quicar(self, topo: float, velocidade: float = VEL_PULO) -> None:
        self.y = topo + ALTURA_JOGADOR / 2
        self.vy = velocidade

    def desenhar(self, render: Renderizador) -> None:
        render.retangulo((self.x, self.y), (LARGURA_JOGADOR, ALTURA_JOGADOR), COR_JOGADOR)
        olhar_x = 0.008 * self.ultima_direcao
        olhar_y = 0.006 * max(-1.0, min(1.0, self.vy / VEL_PULO))
        for lado in (-1.0, 1.0):
            olho = (self.x + lado * 0.026, self.y + 0.025)
            render.circulo(olho, 0.02, COR_OLHO)
            render.circulo((olho[0] + olhar_x, olho[1] + olhar_y), 0.01, COR_PUPILA)


class TipoPlataforma(Enum):
    NORMAL = "normal"
    MOVEL = "movel"
    FRAGIL = "fragil"


@dataclass(eq=False)
class Plataforma:
    """Também é uma superfície de pouso: tem `x`, `largura`, `topo` e `pisar`, como a Mola."""
    x: float
    y: float
    largura: float
    tipo: TipoPlataforma = TipoPlataforma.NORMAL
    velocidade: float = 0.0
    quebrada: bool = False
    mola: Mola | None = None

    @property
    def topo(self) -> float:
        return self.y + ALTURA_PLATAFORMA / 2

    def pisar(self, jogador: Jogador) -> None:
        jogador.quicar(self.topo)
        if self.tipo is TipoPlataforma.FRAGIL:
            self.quebrada = True

    def atualizar(self, dt: float) -> None:
        if self.tipo is not TipoPlataforma.MOVEL:
            return
        self.x += self.velocidade * dt
        limite = MEIA_LARGURA_TELA - self.largura / 2
        if abs(self.x) > limite:   # bateu na borda: volta
            self.x = max(-limite, min(limite, self.x))
            self.velocidade = -self.velocidade

    def desenhar(self, render: Renderizador) -> None:
        tamanho = (self.largura, ALTURA_PLATAFORMA)
        if self.tipo is TipoPlataforma.FRAGIL:
            render.retangulo((self.x, self.y), tamanho, COR_FRAGIL)
            render.contorno((self.x, self.y), tamanho, COR_FRAGIL_BORDA)
        else:
            cor = COR_MOVEL if self.tipo is TipoPlataforma.MOVEL else COR_NORMAL
            render.retangulo((self.x, self.y), tamanho, cor)
        if self.mola:
            self.mola.desenhar(render)


@dataclass(eq=False)
class Mola:
    """Presa a uma plataforma: anda junto com ela se for móvel."""
    plataforma: Plataforma
    deslocamento: float   # do centro da plataforma
    esticada: bool = False
    largura: ClassVar[float] = LARGURA_MOLA

    @property
    def x(self) -> float:
        return self.plataforma.x + self.deslocamento

    @property
    def topo(self) -> float:
        altura = ALTURA_MOLA_ESTICADA if self.esticada else ALTURA_MOLA
        return self.plataforma.topo + altura

    def pisar(self, jogador: Jogador) -> None:
        # Estica e continua esticada, como nos jogos do gênero.
        self.esticada = True
        jogador.quicar(self.topo, VEL_MOLA)

    def desenhar(self, render: Renderizador) -> None:
        base = self.plataforma.topo
        altura_espiras = self.topo - ESPESSURA_TAMPA_MOLA - base
        # O mesmo ziguezague, só com outra escala vertical, serve comprimido e
        # esticado; repetido 1 pixel acima, a linha fica com 2 de espessura.
        for dy in (0.0, PIXEL):
            centro = (self.x, base + altura_espiras / 2 + dy)
            render.ziguezague(centro, (0.8 * self.largura, altura_espiras), COR_MOLA)
        tampa_y = self.topo - ESPESSURA_TAMPA_MOLA / 2
        render.retangulo((self.x, tampa_y), (self.largura, ESPESSURA_TAMPA_MOLA), COR_MOLA_TAMPA)


@dataclass(eq=False)
class Moeda:
    x: float
    y: float
    tempo: float = 0.0   # começa numa fase sorteada, para as moedas não girarem juntas
    coletada: bool = False

    def atualizar(self, dt: float) -> None:
        self.tempo += dt

    @property
    def centro(self) -> Par:
        return self.x, self.y + FLUTUACAO_MOEDA * np.sin(2.0 * self.tempo)

    def desenhar(self, render: Renderizador) -> None:
        # O giro é só a largura encolhendo e voltando (|cos|).
        giro = max(0.15, abs(np.cos(VEL_GIRO_MOEDA * self.tempo)))
        render.elipse(self.centro, (RAIO_MOEDA * giro, RAIO_MOEDA), COR_MOEDA)
        render.elipse(self.centro, (0.55 * RAIO_MOEDA * giro, 0.55 * RAIO_MOEDA),
                      COR_MOEDA_MIOLO)
