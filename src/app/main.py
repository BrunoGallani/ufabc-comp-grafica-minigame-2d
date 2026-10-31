"""
Pula-Pula: minigame 2D vertical. O personagem quica sozinho nas plataformas,
a tela só sobe e cair pela borda de baixo encerra a partida.

Executar:
    python src/app/main.py

Teclas:
    CIMA / BAIXO                  escolhem a opção nos menus
    ENTER                         confirma a opção escolhida
    ESQUERDA / DIREITA ou A / D   movem o personagem
    P                             pausa e retoma
    R                             reinicia (começa outra partida na hora)
    V                             liga e desliga o vsync (fps na barra de título)
    ESC                           abre o diálogo CONTINUAR / INICIO / SAIR (ESC de novo volta);
                                  nos recordes, volta ao menu
"""
import sys

import glfw
import moderngl

from config import ALTURA_JANELA, DT_MAXIMO, LARGURA_JANELA, NOME_JOGO
from jogo import Jogo


def erro_glfw(codigo: int, descricao: str) -> None:
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


def criar_janela() -> 'glfw._GLFWwindowPointerT':
    """Abre a janela com OpenGL 4.0 Core e deixa o contexto ativo. Se falhar, encerra."""
    glfw.set_error_callback(erro_glfw)
    if not glfw.init():
        sys.exit("FALHA: glfw não inicializou")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)   # sem isso não roda no macOS
    glfw.window_hint(glfw.SAMPLES, 4)                         # antialiasing
    glfw.window_hint(glfw.RESIZABLE, False)

    janela = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, NOME_JOGO, None, None)
    if not janela:
        glfw.terminate()
        sys.exit("FALHA: não foi possível criar a janela (o driver suporta OpenGL 4.0 Core?)")
    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    return janela


def executar(jogo: Jogo, janela: 'glfw._GLFWwindowPointerT') -> None:
    """Laço principal: Δt medido e limitado, e o fps na barra de título a cada 0,5 s."""
    instante_anterior = marco = glfw.get_time()
    quadros = 0
    while not glfw.window_should_close(janela):
        agora = glfw.get_time()
        # Medido em todo quadro, inclusive na pausa: o tempo pausado não entra no dt.
        dt = min(agora - instante_anterior, DT_MAXIMO)
        instante_anterior = agora

        jogo.atualizar(dt)
        jogo.desenhar()
        glfw.swap_buffers(janela)
        glfw.poll_events()   # é aqui que o GLFW chama jogo.tecla

        quadros += 1
        if agora - marco >= 0.5:
            glfw.set_window_title(janela, jogo.titulo(quadros / (agora - marco)))
            quadros, marco = 0, agora


def main() -> None:
    janela = criar_janela()
    jogo = Jogo(moderngl.create_context(), janela)
    glfw.set_key_callback(janela, jogo.tecla)
    try:
        executar(jogo, janela)
    finally:   # libera a GPU e fecha a janela mesmo se der erro no meio
        jogo.liberar()
        glfw.terminate()


if __name__ == "__main__":
    main()
