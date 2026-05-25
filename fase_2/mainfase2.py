"""
Módulo Principal - Fase 2 do Autorama.
Este módulo contém a lógica específica da segunda pista do jogo.
Ele gerencia o carregamento dos assets da Fase 2, a renderização da pista, o cálculo das curvas e o loop principal da corrida final.
"""

import math
import os
import sys
import pygame

# CONFIGURAÇÃO DE DIRETÓRIOS
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
IMG_PATH = os.path.join(ROOT_DIR, "img")
FASE1_DIR = os.path.join(ROOT_DIR, "fase_1")

# Permite importar o utils que está na Fase 1
if FASE1_DIR not in sys.path:
    sys.path.insert(0, FASE1_DIR)

from utils import check_exit, scale_image, blit_rotate_center

pygame.init()
pygame.font.init()

# CONSTANTES GERAIS
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 221, 0)
GREEN = (0, 200, 0)
CYAN = (0, 200, 200)
AJUSTE_ANGULO = 90

FONT_SMALL = pygame.font.SysFont("arial", 24)
FONT_MED = pygame.font.SysFont("arial", 34, bold=True)

# CONFIGURAÇÕES DA EQUIPE
TOTAL_VOLTAS = 3
WIDTH, HEIGHT = 1200, 825
WIN = None


def load_image(filename: str, scale: float = 1.0, fallback: str | None = None) -> pygame.Surface:
    """
    Carrega e redimensiona uma imagem do diretório de assets.
    Args:
        filename (str): Nome do arquivo de imagem a ser carregado.
        scale (float): Fator de escala para redimensionar a imagem.
        fallback (str | None): Imagem reserva caso a principal falhe.
    Returns:
        pygame.Surface: A superfície da imagem pronta para uso.
    """
    path = os.path.join(IMG_PATH, filename)
    if not os.path.exists(path):
        if fallback is None:
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        path = os.path.join(IMG_PATH, fallback)
    image = pygame.image.load(path)
    return scale_image(image, scale)

def load_phase2_assets(car1_sprite=None, car2_sprite=None):
    """
    Carrega especificamente os assets visuais da Fase 2 (Pista, Grama e Carros).
    Args:
        car1_sprite (str): Nome do arquivo do carro escolhido pelo P1.
        car2_sprite (str): Nome do arquivo do carro escolhido pelo P2.
    Returns:
        tuple: Tupla contendo as superfícies (grama, pista, carro1, carro2).
    """
    # Carrega as imagens e já as redimensiona para a nova resolução da equipe (1200x900)
    grass = load_image("grass2.jpg", 2.5, fallback="gramado.png")
    grass = pygame.transform.scale(grass, (WIDTH, HEIGHT))

    caminho_pista = os.path.join(IMG_PATH, "pista2.png")
    track_img = pygame.image.load(caminho_pista)
    track = pygame.transform.scale(track_img, (WIDTH, HEIGHT))

    # O sistema de carros que a equipe criou para manter a proporção correta
    red_sprite = car1_sprite if car1_sprite else "mazda.png"
    green_sprite = car2_sprite if car2_sprite else "lfa.png"

    SCALE_MAP = {
        "gol.png": 0.048,
        "lfa.png": 0.045,
        "miata.png": 0.193,
        "rolls.png": 0.112,
        "mazda.png": 0.045,
    }

    red_scale = SCALE_MAP.get(red_sprite, 0.070)
    green_scale = SCALE_MAP.get(green_sprite, 0.070)

    red_car = load_image(red_sprite, red_scale, fallback="mazda.png")
    green_car = load_image(green_sprite, green_scale, fallback="lfa.png")

    return grass, track, red_car, green_car

def pct(w: int, h: int, x: float, y: float) -> tuple[int, int]:
    """
    Converte proporções (0.0 a 1.0) em pixels absolutos da tela.
    """
    return int(w * x), int(h * y)

def build_path(points: list[tuple[int, int]], density: int = 18) -> list[tuple[float, float]]:
    """
    Suaviza a linha da pista criando pontos intermediários.
    Args:
        points: Coordenadas originais capturadas no mapeamento.
        density: Quantidade de subpontos gerados entre cada coordenada original.
    Returns:
        Lista densa de coordenadas para o carro fluir suavemente nas curvas.
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
    Normaliza um vetor 2D garantindo que seu comprimento seja 1.
    """
    dist = math.hypot(x, y)
    if dist == 0:
        return 0.0, 0.0
    return x / dist, y / dist

def offset_closed_polyline(points: list[tuple[int, int]], offset: float) -> list[tuple[int, int]]:
    """
    Lógica matemática para gerar as duas faixas independentes a partir da linha central.
    Ele calcula a normal (perpendicular) de cada segmento da pista e empurra a coordenada.
    Args:
        points: A lista de coordenadas que formam o eixo central da pista.
        offset: Valor em pixels para afastar a faixa (Positivo = Dir / Negativo = Esq).
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
    Mapeamento absoluto das coordenadas centrais da pista da Fase 2.
    Garante que os carros saibam exatamente o formato do asfalto.
    """
    w, h = track.get_width(), track.get_height()
    raw = [
        (0.80, 0.84), (0.39, 0.84), (0.37, 0.83), (0.34, 0.82),
        (0.33, 0.80), (0.31, 0.77), (0.29, 0.75), (0.27, 0.74),
        (0.26, 0.74), (0.24, 0.74), (0.21, 0.75), (0.20, 0.77),
        (0.18, 0.79), (0.16, 0.82), (0.14, 0.83), (0.12, 0.84),
        (0.10, 0.84), (0.08, 0.83), (0.07, 0.82), (0.06, 0.80),
        (0.05, 0.78), (0.05, 0.76), (0.05, 0.74), (0.05, 0.34),
        (0.05, 0.31), (0.06, 0.28), (0.06, 0.26), (0.07, 0.25),
        (0.08, 0.23), (0.09, 0.22), (0.10, 0.21), (0.12, 0.20),
        (0.14, 0.20), (0.15, 0.20), (0.17, 0.20), (0.18, 0.22),
        (0.18, 0.23), (0.19, 0.25), (0.19, 0.27), (0.19, 0.54),
        (0.20, 0.57), (0.20, 0.59), (0.22, 0.60), (0.23, 0.61),
        (0.25, 0.62), (0.39, 0.62), (0.41, 0.61), (0.42, 0.60),
        (0.43, 0.58), (0.43, 0.56), (0.43, 0.55), (0.41, 0.53),
        (0.40, 0.52), (0.39, 0.52), (0.31, 0.52), (0.30, 0.52),
        (0.29, 0.51), (0.28, 0.49), (0.28, 0.47), (0.28, 0.25),
        (0.28, 0.23), (0.28, 0.21), (0.29, 0.20), (0.31, 0.19),
        (0.33, 0.18), (0.35, 0.19), (0.88, 0.18), (0.90, 0.19),
        (0.92, 0.20), (0.93, 0.22), (0.93, 0.24), (0.92, 0.26),
        (0.90, 0.27), (0.88, 0.28), (0.59, 0.28), (0.56, 0.28),
        (0.54, 0.29), (0.53, 0.31), (0.52, 0.33), (0.51, 0.35),
        (0.51, 0.37), (0.52, 0.39), (0.53, 0.41), (0.55, 0.42),
        (0.56, 0.43), (0.58, 0.43), (0.60, 0.44), (0.61, 0.46),
        (0.61, 0.48), (0.61, 0.51), (0.59, 0.52), (0.58, 0.53),
        (0.56, 0.53), (0.54, 0.53), (0.52, 0.55), (0.51, 0.56),
        (0.50, 0.59), (0.51, 0.61), (0.52, 0.63), (0.53, 0.63),
        (0.55, 0.64), (0.57, 0.64), (0.60, 0.64), (0.63, 0.64),
        (0.65, 0.65), (0.66, 0.66), (0.68, 0.68), (0.69, 0.69),
        (0.71, 0.70), (0.73, 0.71), (0.74, 0.71), (0.89, 0.71),
        (0.90, 0.71), (0.92, 0.73), (0.93, 0.75), (0.94, 0.77),
        (0.93, 0.79), (0.93, 0.80), (0.92, 0.82), (0.91, 0.83),
        (0.89, 0.84), (0.88, 0.84), (0.80, 0.84)
    ]
    return [pct(w, h, x, y) for x, y in raw]

def build_lane_paths_phase2(track: pygame.Surface, lane_offset: int = 24):
    """
    Envolve todo o fluxo de cálculos geométricos para entregar as pistas prontas."""
    center = centerline_points(2, track)
    left_lane = build_path(offset_closed_polyline(center, -lane_offset), density=18)
    right_lane = build_path(offset_closed_polyline(center, lane_offset), density=18)
    return left_lane, right_lane, center

class SlotCarPhase2:
    """
    Classe base do veículo da Fase 2.
    Gerencia atributos físicos, sistema de punição e lógica de renderização
    isolada para respeitar as boas práticas de Orientação a Objetos.
    """
    def __init__(self, image: pygame.Surface, path: list[tuple[float, float]]):
        self.img = image
        self.path = path

        # Constantes Físicas do Veículo
        self.max_vel = 10.0
        self.derail_vel = 8.0 # Limite imposto. Acelerar além disso causa o crash.

        # Sistema de Penalidade
        self.crashed = False
        self.crash_timer = 0
        self.PENALTY_FRAMES = 90

        # Estado do Veículo em Tempo Real
        self.vel = 0.0
        self.acceleration = 0.08
        self.angle = 0.0
        self.path_index = 0
        self.laps = 0
        self.locked = False # Define se o carro terminou a corrida

        if self.path:
            self.x, self.y = self.path[0]
            self.sync_angle()

    def sync_angle(self):
        """
        Sincroniza o sprite inicial de acordo com a primeira curva da pista.
        """
        if len(self.path) > 1:
            nx, ny = self.path[1]
            self.angle = -math.degrees(math.atan2(ny - self.y, nx - self.x)) + AJUSTE_ANGULO

    def draw(self, win: pygame.Surface):
        """
        Renderiza o carro e aplica o efeito visual de 'piscar' quando punido.
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
        Gerencia o tempo restante em que o jogador deve aguardar após um acidente."""
        if self.crashed:
            self.crash_timer -= 1
            if self.crash_timer <= 0:
                self.crashed = False
            return True
        return False

    def advance(self, distance: float):
        """
        Move as coordenadas do carro garantindo que ele siga estritamente os
        pontos mapeados no `self.path`, e conta as voltas ao passar no índice [0].
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
                    if self.laps >= TOTAL_VOLTAS:
                        self.locked = True; self.vel = 0.0; return
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
                    if self.laps >= TOTAL_VOLTAS:
                        self.locked = True; self.vel = 0.0; return
            else:
                break

    def accelerate(self):
        """
        Aplica aceleração. Se o carro exceder o limite s
        """
        if self.locked or self.manage_penalty():
            return
        self.vel += self.acceleration

        if self.vel > self.derail_vel:
            # SOM DO CARRO MORRENDO
            try:
                caminho_sfx = os.path.join(os.path.dirname(__file__), "..", "music", "carro_morrendo.mp3")
                pygame.mixer.Sound(caminho_sfx).play()
            except Exception as e:
                print(f"Aviso: Não foi possível tocar o som de batida na Fase 2. Erro: {e}")

            self.crashed = True
            self.crash_timer = self.PENALTY_FRAMES
            self.vel = 0.0
            return

        self.advance(self.vel)

    def brake(self):
        """
        Reduz a velocidade rapidamente a pedido do usuário (Freio ativo).
        """
        if self.locked or self.manage_penalty():
            return
        self.vel = max(self.vel - self.acceleration * 2, 0.0)
        if self.vel > 0:
            self.advance(self.vel)

    def coast(self):
        """
        Desaceleração passiva pelo atrito (inércia do motor).
        """
        if self.locked or self.manage_penalty():
            return
        self.vel = max(self.vel - self.acceleration * 0.35, 0.0)
        if self.vel > 0:
            self.advance(self.vel)

def show_results(fase, vencedor, nome1, nome2, voltas1, voltas2):
    global WIN

    WIN = pygame.display.get_surface()
    if WIN is None:
        WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

    clock = pygame.time.Clock()

    fundo_final = pygame.image.load(os.path.join(IMG_PATH, "final-fase2.png"))
    fundo_final = pygame.transform.scale(fundo_final, (WIDTH, HEIGHT))

    vencedor_nome = nome1 if vencedor == 1 else nome2

    while True:
        clock.tick(FPS)
        WIN.blit(fundo_final, (0, 0))

        #titulo = FONT_MED.render("Resultado da Fase 2", True, WHITE)
        #nome_vencedor = FONT_MED.render(f"Vencedor: {vencedor_nome}", True, WHITE)
        #l1 = FONT_SMALL.render(f"{nome1}: {voltas1} voltas", True, WHITE)
        #l2 = FONT_SMALL.render(f"{nome2}: {voltas2} voltas", True, WHITE)
        #instrucao = FONT_SMALL.render("ENTER para continuar | ESC para reiniciar", True, YELLOW)

        #WIN.blit(titulo, titulo.get_rect(center=(WIDTH // 2, 120)))
        #WIN.blit(nome_vencedor, nome_vencedor.get_rect(center=(WIDTH // 2, 220)))
        #WIN.blit(l1, l1.get_rect(center=(WIDTH // 2, 300)))
        #WIN.blit(l2, l2.get_rect(center=(WIDTH // 2, 345)))
        #WIN.blit(instrucao, instrucao.get_rect(center=(WIDTH // 2, HEIGHT - 70)))

        for event in pygame.event.get():
            check_exit(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "continue"
                if event.key == pygame.K_ESCAPE:
                    return "restart"

        pygame.display.update()
# LOOP PRINCIPAL DA FASE
def run_phase_2(player1_name: str, player2_name: str, car1_sprite=None, car2_sprite=None):
    global WIN
    """
    Controlador principal (Game Loop) da Fase 2.
    Interpreta os inputs de teclado de ambos jogadores e renderiza o cenário em 60 FPS.
    """
    DEBUG_PATHS = False # Altere para True para ver as linhas matemáticas da pista desenhadas

    grass, track, red_car_img, green_car_img = load_phase2_assets(car1_sprite, car2_sprite)

    # Verifica o contexto atual da tela para não quebrar no macOS/Windows
    WIN = pygame.display.get_surface()
    if WIN is None or WIN.get_size() != (WIDTH, HEIGHT):
        WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

    lane_offset = 9 # Define a distância exata em pixels que os carros ficam separados

    lane_left, lane_right, center_raw = build_lane_paths_phase2(track, lane_offset)
    center_path = build_path(center_raw, density=18)

    # Instancia as classes dos veículos em suas respectivas faixas
    car1 = SlotCarPhase2(red_car_img, lane_left)
    car2 = SlotCarPhase2(green_car_img, lane_right)

    clock = pygame.time.Clock()
    winner = None

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            check_exit(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        # Processamento de Input Simultâneo (Teclado)
        keys = pygame.key.get_pressed()

        # Player 1 = setas
        # Input Player 1
        if keys[pygame.K_UP]:
            car1.accelerate()
        elif keys[pygame.K_DOWN]:
            car1.brake()
        else:
            car1.coast()

        # Player 2 = WASD
        # Input Player 2
        if keys[pygame.K_w]:
            car2.accelerate()
        elif keys[pygame.K_s]:
            car2.brake()
        else:
            car2.coast()

        # Condição de Fim de Corrida
        if car1.laps >= TOTAL_VOLTAS and winner is None:
            winner = 1
        if car2.laps >= TOTAL_VOLTAS and winner is None:
            winner = 2

        # Renderização Camada por Camada (Z-Index)
        WIN.blit(grass, (0, 0))
        WIN.blit(track, (0, 0))

        if DEBUG_PATHS:
            if len(center_path) > 1:
                pygame.draw.lines(WIN, YELLOW, True, center_path, 2)
            if len(lane_left) > 1:
                pygame.draw.lines(WIN, RED, True, lane_left, 2)
            if len(lane_right) > 1:
                pygame.draw.lines(WIN, GREEN, True, lane_right, 2)

        car1.draw(WIN)
        car2.draw(WIN)

        # Atualização em tempo real do Placar HUD
        laps_1 = FONT_SMALL.render(f"{player1_name}: {car1.laps}/{TOTAL_VOLTAS}", True, WHITE)
        laps_2 = FONT_SMALL.render(f"{player2_name}: {car2.laps}/{TOTAL_VOLTAS}", True, WHITE)
        phase_label = FONT_SMALL.render("Fase 2", True, CYAN)

        WIN.blit(laps_1, (20, 18))
        WIN.blit(laps_2, (20, 46))
        WIN.blit(phase_label, (WIN.get_width() - 110, 18))

        pygame.display.update()

        # Retorna o resultado para o Maestro central (main.py)
        if winner is not None:
            return winner, car1.laps, car2.laps

if __name__ == "__main__":
    pygame.display.set_mode((WIDTH, HEIGHT))
    run_phase_2("Corredor 1", "Corredor 2")
    pygame.quit()