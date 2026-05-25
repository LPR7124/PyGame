import os
import sys
import importlib.util
from pathlib import Path
import pygame
import inspect
import ctypes

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from fase_2.utils import check_exit

def chamar_resultado_modulo(modulo, fase, vencedor, nome1, nome2, voltas1, voltas2):
    """
    Chama a função de resultado do módulo da fase.
    Aceita nomes diferentes de função para evitar erro de compatibilidade.
    """
    if hasattr(modulo, "show_results"):
        return modulo.show_results(fase, vencedor, nome1, nome2, voltas1, voltas2)
    elif hasattr(modulo, "show_phase_result"):
        return modulo.show_phase_result(fase, vencedor, nome1, nome2, voltas1, voltas2)
    elif hasattr(modulo, "show_message"):
        texto_vencedor = nome1 if vencedor == 1 else nome2
        return modulo.show_message(
            f"Resultado da Fase {fase}",
            [
                f"Vencedor: {texto_vencedor}",
                f"{nome1}: {voltas1} voltas",
                f"{nome2}: {voltas2} voltas",
            ],
        )
    else:
        print(f"Fase {fase} encerrada.")
        return None

# resolução da tela do monitor
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
WIDTH = 1200
HEIGHT = 825
# centraliza horizontalmente
x = (screen_width - WIDTH) // 2
# define altura manual
y = 0
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
pygame.init()
pygame.font.init()
pygame.mixer.init() # INICIA O ÁUDIO AQUI PARA CARREGAR OS EFEITOS

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

FASE1_PATH = ROOT_DIR / "fase_1" / "mainfase1.py"
FASE2_PATH = ROOT_DIR / "fase_2" / "mainfase2.py"

WIDTH, HEIGHT = 1200, 825
FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Autorama Arcade - Menu Principal")

IMG_PATH = ROOT_DIR / "img"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 180, 75)
YELLOW = (255, 215, 0)
DARK = (20, 20, 20)

FONT_BIG = pygame.font.SysFont("arial", 54, bold=True)
FONT_MED = pygame.font.SysFont("arial", 34, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 24)

# --- CARREGADOR DO EFEITO SONORO DO MENU ---
try:
    caminho_sfx = ROOT_DIR / "music" / "escolher_carro.mp3"
    SFX_BOTAO = pygame.mixer.Sound(str(caminho_sfx))
    SFX_BOTAO.set_volume(1.0)
except Exception as e:
    print(f"Aviso: Não foi possível carregar o efeito sonoro. Erro: {e}")
    SFX_BOTAO = None

def tocar_sfx_menu():
    """Toca o som de clique do menu se o arquivo tiver sido carregado com sucesso."""
    if SFX_BOTAO:
        SFX_BOTAO.play()
# -------------------------------------------

def load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o módulo em: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fase1_module = load_module("mainfase1", FASE1_PATH)
fase2_module = load_module("mainfase2", FASE2_PATH)

CAR_OPTIONS = [
    {"label": "GOLF MK2", "screen": "escolha-gol.png", "sprite": "gol.png"},
    {"label": "LEXUS LFA", "screen": "escolha-lfa.png", "sprite": "lfa.png"},
    {"label": "MAZDA MX-5", "screen": "escolha-miata.png", "sprite": "miata.png"},
    {"label": "ROLLS CULLINAN", "screen": "escolha-rolls.png", "sprite": "rolls.png"},
    {"label": "MAZDA RX-7", "screen": "escolha-rx7.png", "sprite": "rx7.png"},
]


def call_compat(func, *args):
    """
    Chama uma função passando apenas a quantidade de argumentos
    que ela realmente aceita.
    """
    sig = inspect.signature(func)
    params = [
        p for p in sig.parameters.values()
        if p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]

    if any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values()):
        return func(*args)

    return func(*args[:len(params)])


def center_text(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)


def tela_capa_jogo():
    """Desenha a capa do jogo e aguarda ENTER ou clique no botão iniciar."""
    clock = pygame.time.Clock()

    fundo_capa = pygame.image.load(str(IMG_PATH / "capa-jogo.png"))
    fundo_capa = pygame.transform.smoothscale(fundo_capa, (WIDTH, HEIGHT))

    x_original, y_original = 365, 460
    largura_original, altura_original = 470, 105

    x_ajustado = int(x_original * (WIDTH / 1200))
    y_ajustado = int(y_original * (HEIGHT / 900))
    largura_ajustada = int(largura_original * (WIDTH / 1200))
    altura_ajustada = int(altura_original * (HEIGHT / 900))

    retangulo_iniciar = pygame.Rect(
        x_ajustado, y_ajustado, largura_ajustada, altura_ajustada
    )

    while True:
        clock.tick(FPS)
        WIN.blit(fundo_capa, (0, 0))

        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    tocar_sfx_menu()  # Toca o SFX
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retangulo_iniciar.collidepoint(event.pos):
                    tocar_sfx_menu()  # Toca o SFX
                    return

        pygame.display.update()


def tela_escolha_carros():
    clock = pygame.time.Clock()

    previews = []
    for option in CAR_OPTIONS:
        img = pygame.image.load(str(IMG_PATH / option["screen"])).convert()
        img = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
        previews.append(img)

    selected_p1 = None
    selected_p2 = None
    current = 0

    left_btn = pygame.Rect(80, 300, 180, 220)
    right_btn = pygame.Rect(WIDTH - 260, 300, 180, 220)
    start_btn = pygame.Rect((WIDTH - 340) // 2, 470, 340, 95)

    stage = 1  # 1 = P1 escolhe, 2 = P2 escolhe

    while True:
        clock.tick(FPS)
        WIN.blit(previews[current], (0, 0))

        if stage == 1:
            hint_text = "P1: use <- -> e clique em INICIAR para confirmar"
        else:
            hint_text = "P2: use A/D e clique em INICIAR para confirmar"

        info1 = FONT_SMALL.render(
            f"1P: {selected_p1['label'] if selected_p1 else 'não escolhido'}",
            True,
            WHITE,
        )
        info2 = FONT_SMALL.render(
            f"2P: {selected_p2['label'] if selected_p2 else 'não escolhido'}",
            True,
            WHITE,
        )
        hint = FONT_SMALL.render(hint_text, True, YELLOW)

        current_name = FONT_MED.render(CAR_OPTIONS[current]["label"], True, WHITE)

        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if stage == 1:
                    if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                        tocar_sfx_menu()  # Toca o SFX
                        if event.key == pygame.K_RIGHT:
                            current = (current + 1) % len(CAR_OPTIONS)
                        else:
                            current = (current - 1) % len(CAR_OPTIONS)

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        tocar_sfx_menu()  # Toca o SFX
                        selected_p1 = CAR_OPTIONS[current]
                        stage = 2
                        current = 0

                elif stage == 2:
                    if event.key in (pygame.K_d, pygame.K_a):
                        tocar_sfx_menu()  # Toca o SFX
                        if event.key == pygame.K_d:
                            current = (current + 1) % len(CAR_OPTIONS)
                        else:
                            current = (current - 1) % len(CAR_OPTIONS)

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        tocar_sfx_menu()  # Toca o SFX
                        selected_p2 = CAR_OPTIONS[current]
                        return selected_p1["sprite"], selected_p2["sprite"]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if left_btn.collidepoint(event.pos):
                    tocar_sfx_menu()  # Toca o SFX
                    current = (current - 1) % len(CAR_OPTIONS)

                elif right_btn.collidepoint(event.pos):
                    tocar_sfx_menu()  # Toca o SFX
                    current = (current + 1) % len(CAR_OPTIONS)

                elif start_btn.collidepoint(event.pos):
                    tocar_sfx_menu()  # Toca o SFX
                    if stage == 1:
                        selected_p1 = CAR_OPTIONS[current]
                        stage = 2
                        current = 0
                    else:
                        selected_p2 = CAR_OPTIONS[current]
                        return selected_p1["sprite"], selected_p2["sprite"]

        pygame.display.update()


def exibir_instrucao(nome_imagem):
    """Exibe uma imagem de instrução em tela cheia e aguarda ENTER."""
    clock = pygame.time.Clock()

    fundo_instrucao = pygame.image.load(str(IMG_PATH / nome_imagem)).convert()
    fundo_instrucao = pygame.transform.smoothscale(fundo_instrucao, (WIDTH, HEIGHT))

    while True:
        clock.tick(FPS)
        WIN.blit(fundo_instrucao, (0, 0))

        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    tocar_sfx_menu()  # Toca o SFX
                    return

        pygame.display.update()


def main_geral():
    caminho_musica_menu = ROOT_DIR / "music" / "principal.mp3"
    try:
        pygame.mixer.music.load(str(caminho_musica_menu))
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a música do menu. Erro: {e}")

    tela_capa_jogo()
    exibir_instrucao("tela de instrucoes_escolha_carros.png")
    car1_sprite, car2_sprite = tela_escolha_carros()
    player1_name, player2_name = fase1_module.ask_player_names()
    exibir_instrucao("tela de instrucoes_jogar.png")

    caminho_musica = ROOT_DIR / "music" / "principal_sixdays.mp3"
    try:
        pygame.mixer.music.load(str(caminho_musica))
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a música da corrida. Erro: {e}")

    pygame.event.clear()
    pygame.time.wait(200)
    WIN.fill(BLACK)
    pygame.display.update()

    fase1_module.start_screen()

    phase1_winner, laps1_p1, laps1_p2 = call_compat(
        fase1_module.run_phase,
        1,
        player1_name,
        player2_name,
        car1_sprite,
        car2_sprite,
    )

    chamar_resultado_modulo(
        fase1_module,
        1,
        phase1_winner,
        player1_name,
        player2_name,
        laps1_p1,
        laps1_p2,
    )

    phase2_winner, laps2_p1, laps2_p2 = call_compat(
        fase2_module.run_phase_2,
        player1_name,
        player2_name,
        car1_sprite,
        car2_sprite,
    )

    resultado_final = fase2_module.show_results(
    2,
    phase2_winner,
    player1_name,
    player2_name,
    laps2_p1,
    laps2_p2,
)

    if resultado_final == "restart":
        return main_geral()

if __name__ == "__main__":
    main_geral()
pygame.quit()
sys.exit()