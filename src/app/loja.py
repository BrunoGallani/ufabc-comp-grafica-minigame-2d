"""
A loja: compra skins com as moedas da carteira, guarda as compradas e a
escolhida em JSON, para sobreviverem entre execuções, e desenha a vitrine.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from carteira import Carteira
from config import ARQUIVO_SKINS, COR_DESTAQUE, COR_FIM, COR_MOEDA, COR_PLACAR, ESCALA_VITRINE
from entidades import desenhar_personagem
from menu import desenhar_opcoes
from skins import SKIN_PADRAO, SKINS, Skin

if TYPE_CHECKING:
    from display import Display
    from renderizador import Renderizador

POR_NOME = {skin.nome: skin for skin in SKINS}
ESPACO_LINHAS = 0.21   # entre as skins da vitrine


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

    def desenhar(self, render: Renderizador, display: Display, escolhida: int, y: float,
                 pulso: float, tempo: float) -> None:
        """
        A vitrine: uma skin por linha, a partir de `y` para baixo, com o personagem
        vestido, o nome e o preço (USAR se já foi comprada, USANDO na escolhida).
        Embaixo, INICIO. A linha `escolhida` é a da seta, e `tempo` anima as estampas.
        """
        for i, skin in enumerate(SKINS):
            y_linha = y - ESPACO_LINHAS * i
            cor = COR_DESTAQUE if i == escolhida else COR_PLACAR
            if i == escolhida:
                render.triangulo((-0.52, y_linha), 0.06 * pulso, cor)
            desenhar_personagem(render, (-0.39, y_linha), skin, tempo, escala=ESCALA_VITRINE)
            display.escrever(skin.nome, -0.26, y_linha, 0.055, cor)
            if skin == self.escolhida:
                display.escrever("USANDO", 0.55, y_linha, 0.05, COR_DESTAQUE, 'direita')
            elif skin in self.compradas:
                display.escrever("USAR", 0.55, y_linha, 0.05, COR_PLACAR, 'direita')
            else:
                cor_preco = COR_MOEDA if skin.preco <= self.carteira.saldo else COR_FIM
                display.escrever_moedas(skin.preco, 0.55, y_linha, 0.055, cor_preco, 'direita')
        # Depois das skins vem o INICIO: a seta está nele quando escolhida == len(SKINS).
        desenhar_opcoes(render, display, ["INICIO"], escolhida - len(SKINS),
                        y - ESPACO_LINHAS * len(SKINS), 0.07, pulso)
