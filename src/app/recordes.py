"""
As melhores pontuações: guardadas em JSON, para sobreviverem entre execuções, e
mostradas numa tabela.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from config import ARQUIVO_RECORDES, COR_DESTAQUE, COR_PLACAR, TEXTO_RECORDES, TOTAL_RECORDES

if TYPE_CHECKING:
    from display import Display
    from renderizador import Renderizador


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

    def desenhar(self, render: Renderizador, display: Display, destaque: int | None, y: float,
                 pulso: float) -> None:
        """
        Tabela com as posições vazias como "-". A linha `destaque` (a da partida que
        acabou) ganha a cor de destaque e uma seta pulsando.
        """
        display.escrever(TEXTO_RECORDES, 0.0, y, 0.07, COR_DESTAQUE, 'centro')
        for i in range(TOTAL_RECORDES):
            y_linha = y - 0.16 - 0.12 * i
            cor = COR_DESTAQUE if i == destaque else COR_PLACAR
            texto = str(self.pontos[i]) if i < len(self.pontos) else '-'
            display.escrever(str(i + 1), -0.28, y_linha, 0.06, cor)
            display.escrever(texto, 0.32, y_linha, 0.06, cor, 'direita')
            if i == destaque:
                render.triangulo((-0.38, y_linha), 0.07 * pulso, cor)
