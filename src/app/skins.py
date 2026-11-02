"""
Skins do personagem: o catálogo da loja e o desenho de cada estampa.

Uma skin é desenhada como todo o resto do jogo: o quadrado e o círculo do
Renderizador, com posição, tamanho e cor por uniforms, em camadas (quem é
desenhado depois fica por cima). As posições dentro do corpo são frações do
tamanho dele: x e y vão de -0.5 a 0.5, e o centro é (0, 0).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import numpy as np

from config import (
    COR_FAISCA, COR_JOGADOR, CORES_ARCO_IRIS, CORES_BRASIL, CORES_GALAXIA, CORES_OURO,
    CORES_PLATINA, PRECO_ARCO_IRIS, PRECO_BRASIL, PRECO_GALAXIA, PRECO_OURO, PRECO_PLATINA,
    Cor, Par,
)

if TYPE_CHECKING:
    from renderizador import Renderizador


class Estampa(Enum):
    LISA = "lisa"
    GALAXIA = "galaxia"
    FAIXAS = "faixas"
    METAL = "metal"


@dataclass(frozen=True)
class Skin:
    nome: str                # o que aparece na loja e vai para o arquivo
    preco: int
    estampa: Estampa
    cores: tuple[Cor, ...]   # quantas e para quê depende da estampa


SKINS = (
    Skin("PADRAO", 0, Estampa.LISA, (COR_JOGADOR,)),
    Skin("GALAXIA", PRECO_GALAXIA, Estampa.GALAXIA, CORES_GALAXIA),
    Skin("BRASIL", PRECO_BRASIL, Estampa.FAIXAS, CORES_BRASIL),
    Skin("ARCO-IRIS", PRECO_ARCO_IRIS, Estampa.FAIXAS, CORES_ARCO_IRIS),
    Skin("OURO", PRECO_OURO, Estampa.METAL, CORES_OURO),
    Skin("PLATINA", PRECO_PLATINA, Estampa.METAL, CORES_PLATINA),
)
SKIN_PADRAO = SKINS[0]   # de graça: é a de quem ainda não comprou nenhuma

# Estrelas da galáxia: (x, y), longe dos olhos, e a fase do piscar de cada uma.
ESTRELAS = (
    (-0.34, 0.43, 0.0), (0.28, 0.42, 1.9), (0.38, -0.06, 3.7), (-0.12, -0.10, 5.1),
    (-0.36, -0.30, 2.6), (0.14, -0.30, 4.3), (0.34, -0.42, 0.8), (-0.10, -0.43, 3.0),
)
RAIO_ESTRELA = 0.05      # em frações da largura do corpo

# Brilho do metal, que se repete a cada PERIODO_BRILHO segundos: primeiro um
# lampejo atravessa o corpo e depois faíscas aparecem nos cantos, uma de cada vez.
PERIODO_BRILHO = 2.5
DURACAO_LAMPEJO = 0.5    # segundos para a faixa atravessar o corpo
LARGURA_LAMPEJO = 0.16   # em frações da largura do corpo
FATIAS_LAMPEJO = 12
# Faíscas: (x, y), quando aparecem (segundos depois do começo do brilho) e o tamanho.
FAISCAS = ((0.45, 0.45, 0.30, 1.0), (-0.45, -0.45, 0.50, 0.8), (-0.45, 0.45, 0.70, 0.65))
DURACAO_FAISCA = 0.45


def _ponto(centro: Par, tamanho: Par, fx: float, fy: float) -> Par:
    """O ponto (fx, fy) do corpo, em frações do tamanho dele, levado para o mundo."""
    return centro[0] + fx * tamanho[0], centro[1] + fy * tamanho[1]


def desenhar_corpo(render: Renderizador, centro: Par, tamanho: Par, skin: Skin,
                   tempo: float) -> None:
    """O corpo do personagem com a estampa da skin. `tempo` anima as estrelas e o brilho."""
    match skin.estampa:
        case Estampa.LISA:
            render.retangulo(centro, tamanho, skin.cores[0])
        case Estampa.GALAXIA:
            _galaxia(render, centro, tamanho, skin.cores, tempo)
        case Estampa.FAIXAS:
            _faixas(render, centro, tamanho, skin.cores)
        case Estampa.METAL:
            _metal(render, centro, tamanho, skin.cores, tempo)


def _galaxia(render: Renderizador, centro: Par, tamanho: Par, cores: tuple[Cor, ...],
             tempo: float) -> None:
    """Fundo azul-escuro com mini estrelas que piscam."""
    fundo, estrela = cores
    render.retangulo(centro, tamanho, fundo)
    for fx, fy, fase in ESTRELAS:
        # Piscar é o raio crescer e encolher, cada estrela no seu ritmo.
        raio = RAIO_ESTRELA * tamanho[0] * (0.55 + 0.45 * np.sin(3.0 * tempo + fase))
        render.circulo(_ponto(centro, tamanho, fx, fy), raio, estrela)


def _faixas(render: Renderizador, centro: Par, tamanho: Par, cores: tuple[Cor, ...]) -> None:
    """Uma faixa por cor, todas da mesma altura, da primeira (em cima) até a última."""
    n = len(cores)
    for i, cor in enumerate(cores):
        render.retangulo(_ponto(centro, tamanho, 0.0, 0.5 - (i + 0.5) / n),
                         (tamanho[0], tamanho[1] / n), cor)


def _metal(render: Renderizador, centro: Par, tamanho: Par, cores: tuple[Cor, ...],
           tempo: float) -> None:
    """
    A cor do metal, lisa, com um chanfro fino: borda clara em cima e à esquerda,
    escura embaixo e à direita, como se a luz viesse de cima (volume). E brilha
    como um shiny: de tempos em tempos, um lampejo atravessa o corpo e faíscas
    aparecem nos cantos.
    """
    base, sombra, claro = cores
    largura, altura = tamanho
    render.retangulo(centro, tamanho, base)
    render.retangulo(_ponto(centro, tamanho, 0.0, 0.46), (largura, 0.08 * altura), claro)
    render.retangulo(_ponto(centro, tamanho, -0.46, 0.0), (0.08 * largura, altura), claro)
    render.retangulo(_ponto(centro, tamanho, 0.0, -0.46), (largura, 0.08 * altura), sombra)
    render.retangulo(_ponto(centro, tamanho, 0.46, 0.0), (0.08 * largura, altura), sombra)

    instante = tempo % PERIODO_BRILHO   # segundos desde o começo deste brilho
    if instante < DURACAO_LAMPEJO:
        _lampejo(render, centro, tamanho, instante / DURACAO_LAMPEJO)
    for fx, fy, inicio, tamanho_faisca in FAISCAS:
        progresso = (instante - inicio) / DURACAO_FAISCA   # de 0 a 1 enquanto ela aparece
        if 0.0 < progresso < 1.0:
            _faisca(render, centro, tamanho, fx, fy, tamanho_faisca * np.sin(np.pi * progresso))


def _lampejo(render: Renderizador, centro: Par, tamanho: Par, progresso: float) -> None:
    """
    Faixa clara e inclinada que atravessa o corpo da esquerda para a direita
    (`progresso` vai de 0 a 1). É uma pilha de fatias horizontais, cada uma mais à
    direita quanto mais alta, como degraus; de cada fatia, só se desenha a parte
    que cai dentro do corpo (a sobreposição de dois intervalos).
    """
    meio = -0.85 + 1.7 * progresso   # x da faixa na altura do centro do corpo
    altura_fatia = 1.0 / FATIAS_LAMPEJO
    for k in range(FATIAS_LAMPEJO):
        fy = -0.5 + (k + 0.5) * altura_fatia
        fx = meio + 0.5 * fy
        esquerda = max(-0.5, fx - LARGURA_LAMPEJO / 2)
        direita = min(0.5, fx + LARGURA_LAMPEJO / 2)
        if direita > esquerda:
            render.retangulo(_ponto(centro, tamanho, (esquerda + direita) / 2, fy),
                             ((direita - esquerda) * tamanho[0], altura_fatia * tamanho[1]),
                             COR_FAISCA)


def _faisca(render: Renderizador, centro: Par, tamanho: Par, fx: float, fy: float,
            s: float) -> None:
    """Estrelinha de quatro pontas: duas elipses finas, cruzadas, com as pontas do tamanho s."""
    meio = _ponto(centro, tamanho, fx, fy)
    render.elipse(meio, (0.26 * s * tamanho[0], 0.035 * tamanho[1]), COR_FAISCA)
    render.elipse(meio, (0.035 * tamanho[0], 0.22 * s * tamanho[1]), COR_FAISCA)
