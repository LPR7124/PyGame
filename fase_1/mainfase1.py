import ctypes
"""
Módulo Principal - Fase 1 do Autorama.
Este módulo é responsável por carregar os assets, inicializar a física dos carros, renderizar a pista e gerenciar o fluxo principal da corrida da Fase 1. Ele também fornece classes e funções utilitárias que foram reaproveitadas na fase 2 e podem ser aproveitadas por possíveis fases adicionais futuras.
"""
import importlib.util
import math
import os
import sys
import pygame
import ctypes

# Configurações de diretório
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PHASE2_DIR = os.path.join(ROOT_DIR, "fase_2")

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from utils import check_exit, scale_image, blit_rotate_center

# resolução da tela do monitor
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)

WIDTH = 1200
HEIGHT = 825
# centraliza horizontalmente
x = (screen_width - WIDTH) // 2
# define altura manual
y = 0
# Centraliza a janela do PyGame
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
pygame.init()
pygame.font.init()

# caminhos de arquivos
FILE_PATH = os.path.dirname(__file__)
IMG_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "img"))

# Carregamento inicial de assets básicos
GRASS = scale_image(pygame.image.load(os.path.join(IMG_PATH, "gramado.png")), 2.5)
TRACK = scale_image(pygame.image.load(os.path.join(IMG_PATH, "pista.png")), 1)

TRACK_BORDER = scale_image(pygame.image.load(os.path.join(IMG_PATH, "contorno.png")), 1)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

RED_CAR = scale_image(pygame.image.load(os.path.join(IMG_PATH, "mazda.png")), 0.070)
GREEN_CAR = scale_image(pygame.image.load(os.path.join(IMG_PATH, "lfa.png")), 0.070)

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
# Configurações da janela e visuais
WIDTH, HEIGHT = 1200,900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autorama 2 Jogadores")

FONT_BIG = pygame.font.SysFont("arial", 54, bold=True)
FONT_MED = pygame.font.SysFont("arial", 34, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 24)

FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 221, 0)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
CYAN = (0, 200, 200)
DARK = (20, 20, 20)
TOTAL_VOLTAS = 3

AJUSTE_ANGULO = 90


def load_image(filename: str, scale: float = 1.0, fallback: str | None = None) -> pygame.Surface:
    """
    Carrega e redimensiona uma imagem do diretório de assets.
    Args:
        filename (str): Nome do arquivo de imagem a ser carregado.
        scale (float): Fator de escala para redimensionar a imagem.
        fallback (str | None): Imagem reserva caso a principal não seja encontrada.
    Returns:
        pygame.Surface: A superfície da imagem carregada e escalonada.
    """
    path = os.path.join(IMG_PATH, filename)
    if not os.path.exists(path):
        if fallback is None:
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        path = os.path.join(IMG_PATH, fallback)
    image = pygame.image.load(path)
    return scale_image(image, scale)

def load_assets(level: int, car1_sprite=None, car2_sprite=None):
    """
    Carrega os assets específicos para a fase solicitada.
    Args:
        level (int): O número da fase (1 ou 2).
        car1_sprite (str): Nome do arquivo de sprite do jogador 1.
        car2_sprite (str): Nome do arquivo de sprite do jogador 2.
    Returns:
        tuple: Tupla contendo as superfícies (grama, pista, contorno, carro1, carro2).
    """
    if level == 2:
        grass = load_image("grass2.jpg", 2.5, fallback="gramado.png")
        track = load_image("track2.png", 1.0, fallback="pista.png")
        border = load_image("track2-border.png", 1.0, fallback="contorno.png")
    else:
        grass = load_image("gramado.png", 2.5, fallback="grass.jpg")
        track = load_image("pista.png", 1.0, fallback="track.png")
        border = load_image("contorno.png", 1.0, fallback="track-border.png")

    red_sprite = car1_sprite if car1_sprite else "mazda.png"
    green_sprite = car2_sprite if car2_sprite else "lfa.png"

    SCALE_MAP = {
        "gol.png": 0.075,
        "lfa.png": 0.070,
        "miata.png": 0.300,
        "rolls.png": 0.175,
        "mazda.png": 0.070,
    }

    red_scale = SCALE_MAP.get(red_sprite, 0.070)
    green_scale = SCALE_MAP.get(green_sprite, 0.070)

    red_car = load_image(red_sprite, red_scale, fallback="mazda.png")
    green_car = load_image(green_sprite, green_scale, fallback="lfa.png")
    return grass, track, border, red_car, green_car

def pct(w: int, h: int, x: float, y: float) -> tuple[int, int]:
    """
    Converte coordenadas relativas (0.0 a 1.0) para pixels absolutos.
    """
    return int(w * x), int(h * y)


def build_path(points: list[tuple[int, int]], density: int = 18) -> list[tuple[float, float]]:
    """
    Interpola pontos brutos para criar um caminho contínuo de alta resolução.
    Args:
        points: Lista de coordenadas (x, y) que definem os vértices do caminho.
        density: Número de pontos intermediários criados entre cada par de vértices originais.
    Returns:
        Lista de coordenadas interpoladas representando o caminho suave.
    """
    path: list[tuple[float, float]] = []
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        for step in range(density):
            t = step / density
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            path.append((x, y))
    return path


def normalize(x: float, y: float) -> tuple[float, float]:
    """
    Normaliza um vetor 2D para que tenha comprimento 1.
    """
    dist = math.hypot(x, y)
    if dist == 0:
        return 0.0, 0.0
    return x / dist, y / dist


def offset_closed_polyline(points: list[tuple[int, int]], offset: float) -> list[tuple[int, int]]:
    """
    Cria uma linha paralela a uma polilinha fechada original.
    Usado para gerar as faixas esquerda e direita a partir da linha central.
    Args:
        points: Lista de vértices da linha central.
        offset: Distância em pixels para deslocar a linha (positivo para direita, negativo para esquerda).
    Returns:
        Lista de vértices representando a nova faixa deslocada.
    """
    result: list[tuple[int, int]] = []
    n = len(points)

    for i in range(n):
        x, y = points[i]
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % n]

        v1x, v1y = normalize(x - px, y - py)
        v2x, v2y = normalize(nx - x, ny - y)

        n1x, n1y = -v1y, v1x
        n2x, n2y = -v2y, v2x

        ox, oy = normalize(n1x + n2x, n1y + n2y)
        if ox == 0 and oy == 0:
            ox, oy = n1x, n1y

        dot = ox * n1x + oy * n1y

        if dot > 0.1:
            length = offset / dot
            length = min(length, offset * 1.5)
        else:
            length = offset

        result.append((int(x + ox * length), int(y + oy * length)))
    return result

def centerline_points(level: int, track: pygame.Surface) -> list[tuple[int, int]]:
    """
    Fornece as coordenadas relativas brutas (x,y) da linha central para a fase atual.
    Args:
        level: Número da fase.
        track: Superfície da pista (usada para calcular as proporções).
    Returns:
        Lista de coordenadas absolutas em pixels da linha central.
    """
    w, h = track.get_width(), track.get_height()

    if level == 2:
        raw = [
            (0.12, 0.06), (0.42, 0.06), (0.54, 0.16), (0.54, 0.34),
            (0.80, 0.34), (0.88, 0.50), (0.81, 0.66), (0.60, 0.66),
            (0.60, 0.83), (0.43, 0.91), (0.18, 0.84), (0.09, 0.66),
            (0.09, 0.38), (0.18, 0.20),
        ]
    else:
        raw = [
            (0.50, 0.10), (0.56, 0.10), (0.59, 0.10), (0.64, 0.10),
            (0.69, 0.10), (0.72, 0.10), (0.75, 0.10), (0.79, 0.10),
            (0.82, 0.10), (0.84, 0.10), (0.86, 0.11), (0.88, 0.12),
            (0.90, 0.14), (0.90, 0.16), (0.90, 0.21), (0.90, 0.27),
            (0.90, 0.29), (0.89, 0.31), (0.87, 0.32), (0.86, 0.33),
            (0.80, 0.33), (0.74, 0.33), (0.60, 0.33), (0.57, 0.34),
            (0.56, 0.35), (0.54, 0.37), (0.54, 0.40), (0.54, 0.42),
            (0.54, 0.44), (0.56, 0.46), (0.57, 0.47), (0.59, 0.47),
            (0.61, 0.48), (0.84, 0.48), (0.86, 0.48), (0.88, 0.49),
            (0.88, 0.50), (0.89, 0.51), (0.90, 0.52), (0.90, 0.54),
            (0.90, 0.84), (0.90, 0.87), (0.88, 0.90), (0.86, 0.91),
            (0.84, 0.91), (0.82, 0.91), (0.80, 0.91), (0.77, 0.91),
            (0.75, 0.90), (0.73, 0.89), (0.72, 0.86), (0.71, 0.83),
            (0.71, 0.72), (0.70, 0.68), (0.68, 0.67), (0.66, 0.65),
            (0.64, 0.65), (0.60, 0.64), (0.58, 0.65), (0.57, 0.66),
            (0.55, 0.67), (0.54, 0.68), (0.53, 0.70), (0.52, 0.72),
            (0.52, 0.74), (0.52, 0.83), (0.51, 0.86), (0.49, 0.89),
            (0.47, 0.90), (0.45, 0.91), (0.41, 0.91), (0.38, 0.90),
            (0.36, 0.89), (0.35, 0.88), (0.10, 0.63), (0.09, 0.59),
            (0.09, 0.57), (0.10, 0.17), (0.11, 0.13), (0.13, 0.11),
            (0.15, 0.10), (0.17, 0.10), (0.19, 0.10), (0.20, 0.11),
            (0.22, 0.12), (0.23, 0.14), (0.23, 0.16), (0.24, 0.46),
            (0.25, 0.48), (0.27, 0.50), (0.29, 0.51), (0.32, 0.51),
            (0.33, 0.51), (0.36, 0.49), (0.37, 0.46), (0.38, 0.45),
            (0.38, 0.15), (0.40, 0.12), (0.42, 0.10), (0.45, 0.10),
            (0.46, 0.10), (0.48, 0.10), (0.50, 0.10),
        ]

    return [pct(w, h, x, y) for x, y in raw]


def build_lane_paths(track: pygame.Surface, level: int, lane_offset: int = 24):
    """
    Gera as trajetórias interpoladas para a faixa da esquerda e direita.
    """
    center = centerline_points(level, track)
    left_lane = build_path(offset_closed_polyline(center, -lane_offset), density=18)
    right_lane = build_path(offset_closed_polyline(center, lane_offset), density=18)
    return left_lane, right_lane


class SlotCar:
    """
    Representa um carro no jogo de autorama.
    Gerencia a física (aceleração, frenagem), posição no caminho e penalidades.
    """
    def __init__(self, image: pygame.Surface, path: list[tuple[float, float]]):
        self.img = image
        self.path = path

        self.max_vel = 10.0
        self.derail_vel = 8.0
        self.crashed = False
        self.crash_timer = 0
        self.PENALTY_FRAMES = 90

        self.vel = 0.0
        self.acceleration = 0.08
        self.angle = 0.0
        self.path_index = 0
        self.laps = 0
        self.locked = False

        if self.path:
            self.x, self.y = self.path[0]
            self.sync_angle()

    def sync_angle(self):
        """
        Alinha a rotação do sprite do carro com a direção do caminho inicial.
        """
        if len(self.path) > 1:
            nx, ny = self.path[1]
            self.angle = -math.degrees(math.atan2(ny - self.y, nx - self.x)) + AJUSTE_ANGULO

    def draw(self, win: pygame.Surface):
        """
        Renderiza o carro na tela, manipulando a piscada durante o crash.
        """
        if self.crashed:
            if (self.crash_timer // 5) % 2 == 0:
                return

        blit_rotate_center(win, self.img, (int(self.x), int(self.y)), self.angle)

        if self.crashed:
            aviso = FONT_MED.render("!", True, RED)
            win.blit(aviso, (int(self.x) - 10, int(self.y) - 40))

    def manage_penalty(self) -> bool:
        """
        Processa a contagem regressiva da penalidade de descarrilamento.
        """
        if self.crashed:
            self.crash_timer -= 1
            if self.crash_timer <= 0:
                self.crashed = False
            return True
        return False

    def advance(self, distance: float):
        """
        Move o carro ao longo do caminho calculado com base na distância percorrida no frame.
        Também gerencia a contagem de voltas.
        """
        remaining = distance

        while remaining > 0 and not self.locked:
            next_index = (self.path_index + 1) % len(self.path)
            next_x, next_y = self.path[next_index]

            dx = next_x - self.x
            dy = next_y - self.y
            dist = math.hypot(dx, dy)

            if dist < 0.001:
                self.x, self.y = next_x, next_y
                self.path_index = next_index
                if self.path_index == 0:
                    self.laps += 1
                    if self.laps >= 5:
                        self.locked = True
                        self.vel = 0.0
                        return
                continue

            step = min(remaining, dist)
            self.angle = -math.degrees(math.atan2(dy, dx)) + AJUSTE_ANGULO
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            remaining -= step

            if step >= dist - 0.001:
                self.path_index = next_index
                if self.path_index == 0:
                    self.laps += 1
                    if self.laps >= 5:
                        self.locked = True
                        self.vel = 0.0
                        return
            else:
                break

    def accelerate(self):
        """
        Aumenta a velocidade do carro. Pune se ultrapassar a vel_max.
        """
        if self.locked or self.manage_penalty():
            return

        self.vel += self.acceleration

        if self.vel > self.derail_vel:
            try:
                caminho_sfx = os.path.join(os.path.dirname(__file__), "..", "music", "carro_morrendo.mp3")
                pygame.mixer.Sound(caminho_sfx).play()
            except Exception as e:
                print(f"Aviso: Não foi possível tocar o som de batida na Fase 1. Erro: {e}")
            self.crashed = True
            self.crash_timer = self.PENALTY_FRAMES
            self.vel = 0.0
            return

        self.advance(self.vel)

    def brake(self):
        """
        Reduz a velocidade bruscamente quando o botão de freio é pressionado.
        """
        if self.locked or self.manage_penalty():
            return
        self.vel = max(self.vel - self.acceleration * 2, 0.0)
        if self.vel > 0:
            self.advance(self.vel)

    def coast(self):
        """
        Desaceleração gradual quando nenhum botão está pressionado.
        """
        if self.locked or self.manage_penalty():
            return
        self.vel = max(self.vel - self.acceleration * 0.35, 0.0)
        if self.vel > 0:
            self.advance(self.vel)

# Funções de interface do usuário (UI)
def center_text(surface, text, font, color, y):
    """
    Utilitário para centralizar texto na tela em um dado eixo Y."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)


def draw_button(surface, rect, text, active=False):
    """
    Desenha botões da interface.
    """
    color = YELLOW if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=14)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=14)
    label = FONT_SMALL.render(text, True, BLACK)
    surface.blit(label, label.get_rect(center=rect.center))


def start_screen():
    """
    Tela de introdução da Fase 1.
    """
    clock = pygame.time.Clock()
    fundo_fase1 = pygame.image.load(os.path.join(IMG_PATH, "fase1.png"))
    fundo_fase1 = pygame.transform.scale(fundo_fase1, (WIDTH, HEIGHT))

    largura_botao = 340
    altura_botao = 75
    x_botao = (WIDTH - largura_botao) // 2
    y_botao = 485

    retangulo_iniciar = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)

    while True:
        clock.tick(FPS)
        WIN.blit(fundo_fase1, (0, 0))
        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    posicao_mouse = event.pos
                    if retangulo_iniciar.collidepoint(posicao_mouse):
                        return

        pygame.display.update()


def ask_player_names():
    """
    Tela para entrada de dados (nomes dos jogadores).
    """
    clock = pygame.time.Clock()
    name1 = ""
    name2 = ""
    active = 1

    fundo_nomes = pygame.image.load(os.path.join(IMG_PATH, "nome-jogadores.png"))
    fundo_nomes = pygame.transform.scale(fundo_nomes, (WIDTH, HEIGHT))

    largura_caixa = 550
    altura_caixa = 52
    x_caixas = (WIDTH - largura_caixa) // 2

    box1 = pygame.Rect(x_caixas, 355, largura_caixa, altura_caixa)
    box2 = pygame.Rect(x_caixas, 515, largura_caixa, altura_caixa)

    largura_botao = 340
    altura_botao = 75
    x_botao = (WIDTH - largura_botao) // 2

    retangulo_iniciar = pygame.Rect(x_botao, 805, largura_botao, altura_botao)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    try:
                        pygame.mixer.Sound(os.path.join(IMG_PATH, "..", "music", "escolher_carro.mp3")).play()
                    except:
                        pass
                    active = 2 if active == 1 else 1
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    try:
                        pygame.mixer.Sound(os.path.join(IMG_PATH, "..", "music", "escolher_carro.mp3")).play()
                    except:
                        pass
                    return name1.strip() or "Player 1", name2.strip() or "Player 2"
                elif event.key == pygame.K_BACKSPACE:
                    if active == 1:
                        name1 = name1[:-1]
                    else:
                        name2 = name2[:-1]
                else:
                    if event.unicode.isprintable() and len(event.unicode) == 1:
                        if active == 1 and len(name1) < 16:
                            name1 += event.unicode
                        elif active == 2 and len(name2) < 16:
                            name2 += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos_mouse = event.pos
                if box1.collidepoint(pos_mouse):
                    active = 1
                elif box2.collidepoint(pos_mouse):
                    active = 2
                elif retangulo_iniciar.collidepoint(pos_mouse):
                    return name1.strip() or "Player 1", name2.strip() or "Player 2"

        WIN.blit(fundo_nomes, (0, 0))

        text1 = FONT_MED.render(name1 or "Digite o nome...", True, (200, 200, 200) if not name1 else WHITE)
        text2 = FONT_MED.render(name2 or "Digite o nome...", True, (200, 200, 200) if not name2 else WHITE)

        WIN.blit(text1, (box1.x + 20, box1.y + (box1.height - text1.get_height()) // 2))
        WIN.blit(text2, (box2.x + 20, box2.y + (box2.height - text2.get_height()) // 2))

        pygame.display.update()


def show_message_screen(title, lines, footer="Pressione ENTER para continuar", allow_restart=True):
    """
    Utilitário para exibir telas de aviso e transição.
    """
    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "continue"
                if allow_restart and event.key == pygame.K_TAB:
                    return "restart"

        WIN.fill(DARK)
        center_text(WIN, title, FONT_BIG, WHITE, 110)

        y = 240
        for line in lines:
            center_text(WIN, line, FONT_MED, WHITE, y)
            y += 50

        center_text(WIN, footer, FONT_SMALL, YELLOW, WIN.get_height() - 70)
        pygame.display.update()

# Loop principal da fase
def run_phase(level: int, player1_name: str, player2_name: str, car1_sprite=None, car2_sprite=None):
    """
    Controla o Game Loop principal da fase atual.
    Inicia os carros, processa a entrada do jogador, movimenta os objetos e renderiza a cena.
    Returns:
        tuple: (ID do vencedor (1 ou 2), voltas completadas pelo Player 1, voltas completadas pelo Player 2).
    """
    global WIN

    DEBUG_PATHS = False

    grass, track, border, red_car_img, green_car_img = load_assets(level, car1_sprite, car2_sprite)

    os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
    WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

    lane_offset = 22

    grass = pygame.transform.scale(grass, (WIDTH, HEIGHT))
    track = pygame.transform.scale(track, (WIDTH, HEIGHT))
    border = pygame.transform.scale(border, (WIDTH, HEIGHT))

    # Criação das faixas virtuais com base no centro
    center_raw_points = centerline_points(level, track)
    lane_left, lane_right = build_lane_paths(track, level, lane_offset)
    center_path = build_path(center_raw_points, density=18)
    # Instanciamento dos corredores
    car1 = SlotCar(red_car_img, lane_left)
    car2 = SlotCar(green_car_img, lane_right)

    clock = pygame.time.Clock()
    winner = None
    # Loop
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        # Processamento de input (Player 1 -> W/S ; Player 2 -> UP/DOWN)
        keys = pygame.key.get_pressed()

        # Player 1 = setas
        if keys[pygame.K_UP]:
            car1.accelerate()
        elif keys[pygame.K_DOWN]:
            car1.brake()
        else:
            car1.coast()

        # Player 2 = WASD
        if keys[pygame.K_w]:
            car2.accelerate()
        elif keys[pygame.K_s]:
            car2.brake()
        else:
            car2.coast()
        # Checagem de vitória
        if car1.laps >= 3 and winner is None:
            winner = 1
        if car2.laps >= 3 and winner is None:
            winner = 2
        # Renderização do cenário
        WIN.blit(grass, (0, 0))
        WIN.blit(track, (0, 0))
        WIN.blit(border, (0, 0))

        if DEBUG_PATHS:
            if len(center_path) > 1:
                pygame.draw.lines(WIN, YELLOW, True, center_path, 2)
            if len(lane_left) > 1:
                pygame.draw.lines(WIN, RED, True, lane_left, 2)
            if len(lane_right) > 1:
                pygame.draw.lines(WIN, GREEN, True, lane_right, 2)
        # Renderização dos carros
        car1.draw(WIN)
        car2.draw(WIN)
        # Renderização do HUD (Placar)
        laps_1 = FONT_SMALL.render(f"{player1_name}: {car1.laps}/3", True, WHITE)
        laps_2 = FONT_SMALL.render(f"{player2_name}: {car2.laps}/3", True, WHITE)
        phase_label = FONT_SMALL.render(f"Fase {level}", True, CYAN)

        WIN.blit(laps_1, (20, 18))
        WIN.blit(laps_2, (20, 46))
        WIN.blit(phase_label, (WIN.get_width() - 110, 18))

        pygame.display.update()
        # Finaliza o loop retornando os dados
        if winner is not None:
            return winner, car1.laps, car2.laps


def load_phase2_module():
    """
    Importa dinamicamente a Fase 2 localizada em outra pasta.
    """
    phase2_path = os.path.join(PHASE2_DIR, "main.py")
    spec = importlib.util.spec_from_file_location("fase2_main_module", phase2_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar fase_2/main.py")

    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, PHASE2_DIR)
    spec.loader.exec_module(module)
    return module


def show_phase_result(phase, winner_id, player1_name, player2_name, laps_1, laps_2):
    global WIN
    clock = pygame.time.Clock()
    fundo_final = pygame.image.load(os.path.join(IMG_PATH, "final-fase1.png"))
    fundo_final = pygame.transform.scale(fundo_final, (WIDTH, HEIGHT))

    while True:
        clock.tick(FPS)
        WIN.blit(fundo_final, (0, 0))
        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return
        pygame.display.update()
    """
    Formata e exibe o resultado da fase recém concluída.
    """
    winner_name = player1_name if winner_id == 1 else player2_name
    show_message_screen(
        f"Fase {phase} concluída",
        [
            f"Vencedor: {winner_name}",
            f"{player1_name}: {laps_1} voltas",
            f"{player2_name}: {laps_2} voltas",
        ],
    )


def show_final_screen(phase1_winner, phase2_winner, player1_name, player2_name):
    """
    Calcula a pontuação geral das duas fases e exibe o grande campeão.
    """
    score1 = (1 if phase1_winner == 1 else 0) + (1 if phase2_winner == 1 else 0)
    score2 = (1 if phase1_winner == 2 else 0) + (1 if phase2_winner == 2 else 0)

    if score1 > score2:
        champ = f"Campeão geral: {player1_name}"
    elif score2 > score1:
        champ = f"Campeão geral: {player2_name}"
    else:
        champ = "Empate geral!"

    show_message_screen(
        "Resultado final",
        [
            champ,
            f"Fase 1: {'carro vermelho' if phase1_winner == 1 else 'carro verde'}",
            f"Fase 2: {'carro vermelho' if phase2_winner == 1 else 'carro verde'}",
        ],
        footer="Pressione ENTER para sair",
    )


def main():
    """
    Ponto de entrada do jogo (caso executado diretamente a partir deste módulo).
    """
    start_screen()
    player1_name, player2_name = ask_player_names()
    # Roda Fase 1
    phase1_winner, laps1_p1, laps1_p2 = run_phase(1, player1_name, player2_name)

    show_phase_result(1, phase1_winner, player1_name, player2_name, laps1_p1, laps1_p2)

    try:
        phase2_module = load_phase2_module()
        phase2_winner, laps2_p1, laps2_p2 = phase2_module.run_phase_2(player1_name, player2_name)
        show_phase_result(2, phase2_winner, player1_name, player2_name, laps2_p1, laps2_p2)
    except Exception as e:
        print(f"Não foi possível carregar a fase 2. Erro: {e}")
        phase2_winner, laps2_p1, laps2_p2 = 0, 0, 0

    pygame.quit()


if __name__ == "__main__":
    main()