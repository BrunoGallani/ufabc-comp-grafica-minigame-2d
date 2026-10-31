# Minigame 2D: Pula-pula

Projeto de minigame 2D desenvolvido em Python e OpenGL para a atividade 3 da disciplina de Computação Gráfica, cursada na UFABC no terceiro quadrimestre letivo do ano de 2026.

## Pula-Pula (protótipo)

Jogo vertical no estilo *Doodle Jump*: o personagem quica sozinho nas plataformas e o jogador o guia para os lados. A tela só sobe, e cair pela borda de baixo encerra a partida. O mundo é infinito e fica mais difícil com a altura e com o tempo.

Algumas plataformas têm uma mola: pisando nela, ela estica e lança o personagem quase uma tela para cima. No fim da partida aparece a tabela com as 5 melhores pontuações, com a da partida atual em destaque; os recordes ficam salvos em `recordes.json`, na raiz do projeto.

O jogo abre num menu com o nome do jogo e as opções INICIAR, RECORDES e SAIR. No meio da partida, o ESC abre um diálogo com CONTINUAR, INICIO (volta ao menu) e SAIR. Quem volta ao menu deixa a partida guardada e pode retomá-la de onde parou pela opção CONTINUAR, que só aparece nesse caso. Se escolher INICIAR, a partida guardada é descartada e não entra nos recordes. Na tela de fim de jogo, JOGAR começa outra partida e INICIO volta ao menu.

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
| ↑ / ↓ | escolhem a opção nos menus |
| ENTER | confirma a opção escolhida |
| ← / → ou A / D | movem o personagem |
| P | pausa e retoma |
| R | reinicia (começa outra partida na hora) |
| V | liga e desliga o vsync (fps na barra de título) |
| ESC | abre o diálogo CONTINUAR / INICIO / SAIR; ESC de novo volta para onde estava. Nos recordes, volta ao menu |
