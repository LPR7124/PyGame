"""Funções utilitárias para o jogo de Pygame."""

import pygame

def scale_image(image: pygame.Surface, scale_factor: float) -> pygame.Surface:
    """Redimensiona uma imagem mantendo a proporção."""
    width = int(image.get_width() * scale_factor)
    height = int(image.get_height() * scale_factor)
    return pygame.transform.scale(image, (width, height))

def blit_rotate_center(
    surface: pygame.Surface,
    image: pygame.Surface,
    center_pos: tuple[int, int],
    angle: float
) -> pygame.Rect:
    """Rotaciona a imagem e a desenha centralizada na coordenada passada."""
    # Rotaciona a imagem original
    rotated_image = pygame.transform.rotate(image, angle)
    # Pega o rect da imagem rotacionada e posiciona o centro dele no ponto central do trilho
    new_rect = rotated_image.get_rect(center=center_pos)
    # Desenha na tela usando o canto superior esquerdo calculado pelo rect
    surface.blit(rotated_image, new_rect.topleft)
    return new_rect
def check_exit(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        raise SystemExit

    if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
        pygame.quit()
        raise SystemExit