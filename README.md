# Minigame 2D: Pula-pula

Projeto de minigame 2D desenvolvido em Python e OpenGL para a atividade 3 da disciplina de Computação Gráfica, cursada na UFABC no terceiro quadrimestre letivo do ano de 2026.

## Pula-Pula (protótipo)

Jogo vertical no estilo *Doodle Jump*: o personagem quica sozinho nas plataformas e o jogador o guia para os lados. A tela só sobe, e cair pela borda de baixo encerra a partida. O mundo é infinito e fica mais difícil com a altura e com o tempo.

Algumas plataformas têm uma mola: pisando nela, ela estica e lança o personagem quase uma tela para cima. No fim da partida aparece a tabela com as 5 melhores pontuações, com a da partida atual em destaque; os recordes ficam salvos em `recordes.json`, na raiz do projeto.

Cada moeda coletada vale 10 pontos e fica guardada. Quando a partida acaba, o jogo lê o número de moedas de `moedas.json` (um arquivo que tem só esse número, na raiz do projeto), soma as moedas da partida e grava de volta. Só a partida que chega ao fim guarda as moedas: se ela for abandonada no meio (R, INICIAR com a partida guardada, SAIR ou fechar a janela), o arquivo continua com o que já tinha.

As moedas guardadas compram skin na LOJA do menu: GALAXIA (50 moedas), BRASIL (75), ARCO-IRIS (80), OURO (150) e PLATINA (300). Na loja, ENTER compra a skin escolhida e já passa a usá-la; numa skin já comprada, só troca. Quem não comprou nenhuma usa a skin PADRAO. As compras e a skin em uso ficam em `skins.json`, também na raiz.

O jogo abre num menu com o nome do jogo e as opções INICIAR, LOJA, RECORDES e SAIR. No meio da partida, o ESC abre um diálogo com CONTINUAR, INICIO (volta ao menu) e SAIR. Quem volta ao menu deixa a partida guardada e pode retomá-la de onde parou pela opção CONTINUAR, que só aparece nesse caso. Se escolher INICIAR, a partida guardada é descartada: não entra nos recordes nem guarda as moedas. Na tela de fim de jogo, JOGAR começa outra partida e INICIO volta ao menu.

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
| ↑ / ↓ | escolhem a opção nos menus e a skin na loja |
| ENTER | confirma a opção escolhida (na loja, compra ou usa a skin) |
| ← / → ou A / D | movem o personagem |
| P | pausa e retoma |
| R | reinicia (começa outra partida na hora) |
| V | liga e desliga o vsync (fps na barra de título) |
| F | liga e desliga a tela cheia |
| ESC | abre o diálogo CONTINUAR / INICIO / SAIR; ESC de novo volta para onde estava. Nos recordes e na loja, volta ao menu |
