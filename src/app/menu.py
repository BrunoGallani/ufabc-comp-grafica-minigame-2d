"""Lista de opções das telas: as setas escolhem e o ENTER executa a escolhida."""
from collections.abc import Callable
from dataclasses import dataclass

Opcao = tuple[str, Callable[[], None]]   # (texto na tela, ação)


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
