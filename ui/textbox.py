import pygame


class TextBox:
    """Input text"""

    def __init__(self):
        WIDTH = 900
        HEIGHT = 800
        self.active = False  # Is there text being typed?
        font_16_pt = pygame.font.Font("Tengoku.ttf", 16)
        self.font = font_16_pt
        self.value = ""
        self.image = pygame.Surface(self.font.size(" "))
        self.bg = "#EEEEEE"
        self.image.fill(self.bg)
        self.rect = self.image.get_rect(center=(WIDTH // 5, HEIGHT // 2))

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
        _outline = pygame.Rect(
            self.rect.x - 2, self.rect.y - 2, self.rect.w + 4, self.rect.h + 4
        )
        pygame.draw.rect(
            surface, (0, 200, 0) if self.active else (200, 0, 0), _outline, 2
        )

    def render(self):
        self.image = pygame.Surface(self.font.size(self.value))
        self.image.fill(self.bg)
        self.image.blit(self.font.render(self.value, True, "#000000"), (0, 0))
        self.rect.size = self.image.get_rect().size

    def append(self, t):
        if self.active:
            self.value += t
            self.render()

    def delete(self):
        if self.active:
            if len(self.value) >= 1:
                self.value = self.value[:-1]
            self.render()

    def wipe(self):
        if self.active:
            self.value = ""
            self.render()
            self.image = pygame.Surface(self.font.size(" "))
            self.image.fill("#FFFFFF")
            self.rect.width = self.image.get_rect().w
            self.rect.height = self.image.get_rect().h


