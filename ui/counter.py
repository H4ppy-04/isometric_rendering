import pygame


class Counter:
    def __init__(self, x: int, y: int):
        self.counter = 0
        self.font_32_pt = pygame.font.Font("Tengoku.ttf", 32)
        self.image = pygame.Surface(self.font_32_pt.size(str(self.counter)))
        self.image.fill((0, 0, 0))
        self.image.blit(self.font_32_pt.render(str(self.counter), True, "#FFFFFF"), (0, 0))
        self.rect = self.image.get_rect(center=(x, y))

    def render(self):
        self.image = pygame.Surface(self.font_32_pt.size(str(self.counter)))
        self.image.fill((0, 0, 0))
        self.image.blit(self.font_32_pt.render(str(self.counter), True, "#FFFFFF"), (0, 0))

    def increment(self):
        self.counter += 1
        self.render()

    def decrement(self):
        self.counter -= 1
        self.render()

    def reset(self):
        self.counter = 0
        self.render()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


