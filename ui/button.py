import os

import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, text: str, x: int, y: int, *groups):
        super().__init__(*groups)
        self.font_16_pt = pygame.font.Font(os.path.join("assets", "fonts", "Tengoku.ttf"), 16)

        self.font_color = "#DDDDDD"
        self.hover_color = "#FFFFFF"
        self.color = self.font_color

        self.hovering = False
        self.text = text

        self.image = pygame.Surface(self.font_16_pt.size(self.text))
        self.rect = self.image.get_rect(center=(x, y))
        self.image.blit(self.font_16_pt.render(self.text, True, "#FFFFFF"), (0, 0))

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def update(self):
        self.color = self.hover_color if self.hovering else self.font_color
        self.image.blit(self.font_16_pt.render(self.text, True, self.color), (0, 0))

