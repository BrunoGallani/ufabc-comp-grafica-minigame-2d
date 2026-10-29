"""As melhores pontuações, guardadas em JSON para sobreviverem entre execuções."""
import json
import sys
from pathlib import Path

from config import ARQUIVO_RECORDES, TOTAL_RECORDES


class Recordes:
    def __init__(self, arquivo: Path = ARQUIVO_RECORDES) -> None:
        self.arquivo = arquivo
        self.pontos = self._ler()   # da maior para a menor

    def _ler(self) -> list[int]:
        try:
            dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
            return sorted(map(int, dados), reverse=True)[:TOTAL_RECORDES]
        except FileNotFoundError:   # primeira partida
            return []
        except (OSError, ValueError, TypeError) as erro:   # arquivo estragado: começa do zero
            print(f"recordes ignorados ({self.arquivo}): {erro}", file=sys.stderr)
            return []

    def registrar(self, pontos: int) -> int | None:
        """Põe a pontuação na lista e devolve a posição (0 = melhor), ou None se não entrou."""
        if pontos <= 0:
            return None
        # Num empate, quem fez antes fica na frente.
        posicao = next((i for i, p in enumerate(self.pontos) if pontos > p), len(self.pontos))
        if posicao >= TOTAL_RECORDES:
            return None
        self.pontos.insert(posicao, pontos)
        del self.pontos[TOTAL_RECORDES:]
        try:
            self.arquivo.write_text(json.dumps(self.pontos), encoding="utf-8")
        except OSError as erro:   # sem salvar, o recorde ainda vale nesta execução
            print(f"não foi possível salvar os recordes em {self.arquivo}: {erro}", file=sys.stderr)
        return posicao
