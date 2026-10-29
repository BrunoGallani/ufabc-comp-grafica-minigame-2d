# Minigame 2D: Pula-pula

Projeto de minigame 2D desenvolvido em Python e OpenGL para a atividade 3 da disciplina de Computação Gráfica, cursada na UFABC no terceiro quadrimestre letivo do ano de 2026.

## Pula-Pula (protótipo)

Jogo vertical no estilo *Doodle Jump*: o personagem quica sozinho nas plataformas e o jogador o guia para os lados. A tela só sobe, e cair pela borda de baixo encerra a partida. O mundo é infinito e fica mais difícil com a altura e com o tempo.

Algumas plataformas têm uma mola: pisando nela, ela estica e lança o personagem quase uma tela para cima. No fim da partida aparece a tabela com as 5 melhores pontuações, com a da partida atual em destaque; os recordes ficam salvos em `recordes.json`, na raiz do projeto.

## Como executar

Com Python 3.11, na raiz do repositório:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/app/main.py
```

Também dá para rodar pelo botão de executar do editor, com o arquivo `src/app/main.py` aberto.

## Teclas

| Tecla | Ação |
| --- | --- |
| ← / → ou A / D | movem o personagem |
| ENTER ou ESPAÇO | começa a partida / joga de novo no fim |
| P | pausa e retoma |
| R | reinicia (volta ao início) |
| V | liga e desliga o vsync (fps na barra de título) |
| ESC | sai |
