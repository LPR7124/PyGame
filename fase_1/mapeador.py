"""
Módulo Utilitário - Mapeador de Pistas.
Este script foi desenvolvido com o suporte de IA (Google Gemini) para auxiliar
no mapeamento de coordenadas geográficas das pistas. Ele permite capturar os cliques
do mouse para gerar as matrizes numéricas brutas utilizadas no cálculo de trajetórias.
"""
import os
import pygame

# Configuração de caminhos (mesma do seu main.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Use the repository-level img folder (one level up) instead of a local fase_1/img
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
IMG_PATH = os.path.join(ROOT_DIR, "img")
pygame.init()
# Tente carregar a pista 1 (mude aqui se quiser mapear a fase 2)
# Substitua "pista.png" pelo nome exato do seu arquivo de imagem da pista
NOME_DA_PISTA = "pista.png"
try:
    caminho_img = os.path.join(IMG_PATH, NOME_DA_PISTA)
    track_img = pygame.image.load(caminho_img)
except FileNotFoundError:
    print(f"Erro: Não foi possível encontrar a imagem em {caminho_img}")
    print("Verifique se o nome do arquivo está correto e tente novamente.")
    pygame.quit()
    exit()
WIDTH, HEIGHT = track_img.get_size()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mapeador de Pista - Clique para marcar")
pontos_pct = []  # Vai guardar as porcentagens (x, y)
def draw():
    WIN.blit(track_img, (0, 0))

    pontos_pixel = [(int(x * WIDTH), int(y * HEIGHT)) for x, y in pontos_pct]

    # Desenha as linhas conectando os pontos
    if len(pontos_pixel) > 1:
        pygame.draw.lines(WIN, (255, 255, 0), False, pontos_pixel, 3)

    # Desenha as bolinhas
    for px, py in pontos_pixel:
        pygame.draw.circle(WIN, (255, 0, 0), (px, py), 5)

    pygame.display.update()

def imprimir_codigo():
    print("\n" + "="*40)
    print("COPIE O CÓDIGO ABAIXO E COLE NO SEU MAIN.PY:")
    print("="*40)
    print("raw = [")
    for px, py in pontos_pct:
        print(f"    ({px:.2f}, {py:.2f}),")
    print("]")
    print("="*40 + "\n")

run = True
clock = pygame.time.Clock()

print("\n--- INSTRUÇÕES ---")
print("1. Clique com o botão ESQUERDO para adicionar um ponto no centro da pista.")
print("2. Clique com o botão DIREITO para apagar o último ponto (Desfazer).")
print("3. Pressione ESPAÇO ou ENTER para gerar o código no terminal.")
print("------------------\n")

while run:
    clock.tick(60)
    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo: Adiciona ponto
                mx, my = pygame.mouse.get_pos()
                pontos_pct.append((mx / WIDTH, my / HEIGHT))
            elif event.button == 3:  # Botão direito: Remove último ponto
                if pontos_pct:
                    pontos_pct.pop()

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                imprimir_codigo()

pygame.quit()