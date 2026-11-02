"""
Constantes ajustáveis do jogo.

Distâncias em unidades do mundo (a tela tem 2 de altura) e velocidades em
unidades por segundo. Os pares (fácil, difícil) são interpolados pela dificuldade.
"""
from pathlib import Path

Par = tuple[float, float]
Cor = tuple[float, float, float, float]

NOME_JOGO = "Pula-Pula"
LARGURA_JANELA, ALTURA_JANELA = 480, 800
MEIA_ALTURA_TELA = 1.0
MEIA_LARGURA_TELA = MEIA_ALTURA_TELA * LARGURA_JANELA / ALTURA_JANELA
PIXEL = 2 * MEIA_ALTURA_TELA / ALTURA_JANELA   # 1 pixel em unidades do mundo
DT_MAXIMO = 0.05

LARGURA_JOGADOR, ALTURA_JOGADOR = 0.11, 0.13
GRAVIDADE = 8.0
VEL_PULO = 3.35
VEL_QUEDA_MAX = 3.8
VEL_HORIZONTAL = 1.3
ALTURA_PULO = VEL_PULO ** 2 / (2.0 * GRAVIDADE)

LINHA_CAMERA = 0.15
CAMERA_ATRASO = 8.0
CAMERA_ACELERACAO = 0.004
CAMERA_VEL_MAX = 0.45   # 0 desliga a subida automática

ALTURA_PLATAFORMA = 0.035
Y_BASE = -0.9
MARGEM_GERACAO = 0.5
ALTURA_DIFICULDADE_MAX = 120.0
LARGURA_PLATAFORMA = (0.28, 0.16)
ESPACO_MIN = (0.16, 0.36)
ESPACO_MAX = (0.28, 0.58)
CHANCE_MOVEL = (0.0, 0.45)
VEL_MOVEL = (0.25, 0.75)
CHANCE_FRAGIL = (0.0, 0.25)
CHANCE_MOLA = (0.10, 0.06)   # só em plataformas normais e móveis

# A mola fica em cima da plataforma e, pisada, estica e lança o personagem.
VEL_MOLA = 5.4   # sobe ~1.8, quase uma tela (o pulo normal sobe ~0.7)
LARGURA_MOLA = 0.07
ALTURA_MOLA, ALTURA_MOLA_ESTICADA = 0.04, 0.08
ESPIRAS_MOLA = 3
ESPESSURA_TAMPA_MOLA = 0.012

CHANCE_MOEDA = 0.25
RAIO_MOEDA = 0.04
ALTURA_MOEDA = 0.16
VEL_GIRO_MOEDA = 4.0
FLUTUACAO_MOEDA = 0.015
BONUS_MOEDA = 10

# Loja: as moedas guardadas compram skins para o personagem.
PRECO_GALAXIA, PRECO_BRASIL, PRECO_ARCO_IRIS = 50, 75, 80
PRECO_OURO, PRECO_PLATINA = 150, 300
ESCALA_VITRINE = 1.3     # o personagem na loja, em relação ao tamanho no jogo
AVISO_SEM_SALDO = 0.8    # segundos com o saldo em vermelho quando faltam moedas

PONTOS_POR_UNIDADE = 10
ALTURA_DIGITO_HUD = 0.07
TEXTO_PAUSA, TEXTO_FIM = "PAUSA", "PERDEU"
TEXTO_RECORDES, TEXTO_LOJA, TEXTO_TUTORIAL = "RECORDES", "LOJA", "TUTORIAL"
TOTAL_RECORDES = 5
# Arquivos na raiz do projeto (src/app/config.py -> src/app -> src -> raiz).
RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_RECORDES = RAIZ / "recordes.json"
ARQUIVO_MOEDAS = RAIZ / "moedas.json"   # só o número de moedas guardadas
ARQUIVO_SKINS = RAIZ / "skins.json"    # as skins compradas e a escolhida
ATENUACAO_FORA_DO_JOGO = 0.4
ESPACO_GRADE = 0.25

FUNDO = (0.04, 0.05, 0.09, 1.0)
COR_FAIXAS = (0.0, 0.0, 0.0, 1.0)   # sobras dos lados na tela cheia
COR_GRADE = (0.09, 0.11, 0.18, 1.0)
COR_JOGADOR = (0.95, 0.35, 0.60, 1.0)
COR_OLHO = (1.0, 1.0, 1.0, 1.0)
COR_PUPILA = (0.05, 0.05, 0.05, 1.0)
COR_NORMAL = (0.30, 0.75, 0.35, 1.0)
COR_MOVEL = (0.30, 0.55, 0.95, 1.0)
COR_FRAGIL = (0.35, 0.22, 0.12, 1.0)
COR_FRAGIL_BORDA = (0.95, 0.60, 0.25, 1.0)
COR_MOLA = (0.55, 0.60, 0.68, 1.0)
COR_MOLA_TAMPA = (0.88, 0.90, 0.94, 1.0)
COR_MOEDA = (1.0, 0.82, 0.20, 1.0)
COR_MOEDA_MIOLO = (0.85, 0.60, 0.10, 1.0)
# Skins: as cores de cada estampa.
CORES_GALAXIA = ((0.03, 0.05, 0.22, 1.0),    # fundo azul-escuro
                 (1.0, 1.0, 0.92, 1.0))      # estrelas
CORES_BRASIL = ((0.0, 0.61, 0.23, 1.0),      # faixa de cima
                (1.0, 0.87, 0.0, 1.0),       # do meio
                (0.0, 0.25, 0.62, 1.0))      # de baixo
CORES_ARCO_IRIS = ((0.90, 0.12, 0.14, 1.0),  # vermelho (em cima)
                   (1.0, 0.50, 0.05, 1.0),   # laranja
                   (1.0, 0.87, 0.0, 1.0),    # amarelo
                   (0.15, 0.70, 0.25, 1.0),  # verde
                   (0.10, 0.45, 0.95, 1.0),  # azul
                   (0.30, 0.20, 0.70, 1.0),  # anil
                   (0.62, 0.22, 0.82, 1.0))  # violeta (embaixo)
CORES_OURO = ((0.95, 0.72, 0.16, 1.0),       # base
              (0.74, 0.48, 0.07, 1.0),       # sombra
              (1.0, 0.86, 0.38, 1.0))        # claro
CORES_PLATINA = ((0.80, 0.82, 0.86, 1.0),
                 (0.58, 0.61, 0.67, 1.0),
                 (0.93, 0.94, 0.97, 1.0))
COR_FAISCA = (1.0, 1.0, 1.0, 1.0)           # o brilho que aparece no metal
COR_PLACAR = (0.95, 0.95, 0.95, 1.0)
COR_DESTAQUE = (0.45, 0.90, 0.55, 1.0)
COR_FIM = (0.95, 0.30, 0.30, 1.0)

assert max(ESPACO_MAX) < ALTURA_PULO, "plataforma fora do alcance do pulo"
assert VEL_MOLA > VEL_PULO, "a mola tem que pular mais alto que a plataforma"
# No eixo vertical a moeda usa o corpo varrido entre dois quadros, então não há
# tunelamento nem com a velocidade da mola.
assert VEL_HORIZONTAL * DT_MAXIMO < LARGURA_JOGADOR + 2 * RAIO_MOEDA, \
    "passo horizontal maior que a região de contato com a moeda (tunelamento)"
