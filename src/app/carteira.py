"""As moedas guardadas entre as partidas, num JSON que tem só o número."""
import json
import sys
from pathlib import Path

from config import ARQUIVO_MOEDAS


class Carteira:
    def __init__(self, arquivo: Path = ARQUIVO_MOEDAS) -> None:
        self.arquivo = arquivo
        self.saldo = self._ler()

    def _ler(self) -> int:
        try:
            return max(0, int(json.loads(self.arquivo.read_text(encoding="utf-8"))))
        except FileNotFoundError:   # nenhuma moeda guardada ainda
            return 0
        except (OSError, ValueError, TypeError) as erro:   # arquivo estragado: começa do zero
            print(f"moedas ignoradas ({self.arquivo}): {erro}", file=sys.stderr)
            return 0

    def _gravar(self) -> None:
        try:
            self.arquivo.write_text(json.dumps(self.saldo), encoding="utf-8")
        except OSError as erro:   # sem salvar, o saldo ainda vale nesta execução
            print(f"não foi possível salvar as moedas em {self.arquivo}: {erro}", file=sys.stderr)

    def depositar(self, moedas: int) -> None:
        """Lê o número do arquivo, soma as moedas da partida e grava de volta."""
        if moedas > 0:
            self.saldo = self._ler() + moedas
            self._gravar()

    def gastar(self, moedas: int) -> bool:
        """Desconta do arquivo, se houver moedas suficientes. Devolve se deu."""
        self.saldo = self._ler()
        if moedas > self.saldo:
            return False
        self.saldo -= moedas
        self._gravar()
        return True
