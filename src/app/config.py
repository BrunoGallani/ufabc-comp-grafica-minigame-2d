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

MOEDAS_ATIVAS = True
CHANCE_MOEDA = 0.25
RAIO_MOEDA = 0.04
ALTURA_MOEDA = 0.16
VEL_GIRO_MOEDA = 4.0
FLUTUACAO_MOEDA = 0.015
BONUS_MOEDA = 25

PONTOS_POR_UNIDADE = 10
ALTURA_DIGITO_HUD = 0.07
TEXTO_INICIO, TEXTO_PAUSA, TEXTO_FIM = "PULE", "PAUSA", "PERDEU"
TEXTO_RECORDES = "RECORDES"
TEXTO_SAIR = "SAIR"
TOTAL_RECORDES = 5
# Na raiz do projeto (src/app/config.py -> src/app -> src -> raiz).
ARQUIVO_RECORDES = Path(__file__).resolve().parents[2] / "recordes.json"
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
COR_PLACAR = (0.95, 0.95, 0.95, 1.0)
COR_DESTAQUE = (0.45, 0.90, 0.55, 1.0)
COR_FIM = (0.95, 0.30, 0.30, 1.0)

assert max(ESPACO_MAX) < ALTURA_PULO, "plataforma fora do alcance do pulo"
assert VEL_MOLA > VEL_PULO, "a mola tem que pular mais alto que a plataforma"
# No eixo vertical a moeda usa o corpo varrido entre dois quadros (partida.py),
# então não há tunelamento nem com a velocidade da mola.
assert VEL_HORIZONTAL * DT_MAXIMO < LARGURA_JOGADOR + 2 * RAIO_MOEDA, \
    "passo horizontal maior que a região de contato com a moeda (tunelamento)"
