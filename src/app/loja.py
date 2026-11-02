"""
A loja: compra skins com as moedas da carteira e guarda as compradas e a
escolhida em JSON, para sobreviverem entre execuções.
"""
import json
import sys
from pathlib import Path

from carteira import Carteira
from config import ARQUIVO_SKINS
from skins import SKIN_PADRAO, SKINS, Skin

POR_NOME = {skin.nome: skin for skin in SKINS}


class Loja:
    def __init__(self, carteira: Carteira, arquivo: Path = ARQUIVO_SKINS) -> None:
        self.carteira = carteira
        self.arquivo = arquivo
        self.compradas, self.escolhida = self._ler()

    def _ler(self) -> tuple[set[Skin], Skin]:
        try:
            dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
            # Nome que não está no catálogo é ignorado.
            compradas = {SKIN_PADRAO} | {POR_NOME[nome] for nome in dados["compradas"]
                                         if nome in POR_NOME}
            escolhida = POR_NOME.get(dados["escolhida"], SKIN_PADRAO)
            return compradas, escolhida if escolhida in compradas else SKIN_PADRAO
        except FileNotFoundError:   # nada comprado ainda
            pass
        except (OSError, ValueError, TypeError, KeyError) as erro:   # arquivo estragado
            print(f"skins ignoradas ({self.arquivo}): {erro}", file=sys.stderr)
        return {SKIN_PADRAO}, SKIN_PADRAO

    def _gravar(self) -> None:
        dados = {"compradas": [skin.nome for skin in SKINS if skin in self.compradas],
                 "escolhida": self.escolhida.nome}
        try:
            self.arquivo.write_text(json.dumps(dados), encoding="utf-8")
        except OSError as erro:   # sem salvar, a compra ainda vale nesta execução
            print(f"não foi possível salvar as skins em {self.arquivo}: {erro}", file=sys.stderr)

    def escolher(self, skin: Skin) -> bool:
        """Passa a usar a skin, comprando antes se ainda não é dela. False se faltaram moedas."""
        if skin not in self.compradas:
            if not self.carteira.gastar(skin.preco):
                return False
            self.compradas.add(skin)
        self.escolhida = skin
        self._gravar()
        return True
