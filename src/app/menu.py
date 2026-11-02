"""Lista de opções das telas: CIMA e BAIXO escolhem e ENTER ou ESPAÇO executa a escolhida."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from config import COR_DESTAQUE, COR_PLACAR

if TYPE_CHECKING:
    from display import Display
    from renderizador import Renderizador

Opcao = tuple[str, Callable[[], None]]   # (texto na tela, ação)
ENTRELINHA = 2.0   # de uma opção para a outra, em alturas do texto


@dataclass
class Menu:
    opcoes: list[Opcao]
    escolhida: int = 0

    @property
    def textos(self) -> list[str]:
        return [texto for texto, _ in self.opcoes]

    def mover(self, passo: int) -> None:
        """Passando da última opção, volta para a primeira (e vice-versa)."""
        self.escolhida = (self.escolhida + passo) % len(self.opcoes)

    def confirmar(self) -> None:
        _, acao = self.opcoes[self.escolhida]
        acao()


def desenhar_opcoes(render: Renderizador, display: Display, textos: list[str], escolhida: int,
                    y: float, altura: float, pulso: float) -> None:
    """
    Uma opção por linha, a partir de `y` para baixo, alinhadas à esquerda e com o
    bloco centrado na tela. A escolhida ganha a cor de destaque e uma seta pulsando.
    """
    x = -max(display.largura(texto, altura) for texto in textos) / 2
    for i, texto in enumerate(textos):
        y_linha = y - ENTRELINHA * altura * i
        cor = COR_DESTAQUE if i == escolhida else COR_PLACAR
        display.escrever(texto, x, y_linha, altura, cor)
        if i == escolhida:
            render.triangulo((x - 1.5 * altura, y_linha), altura * pulso, cor)
