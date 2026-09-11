import pygame


class DropdownMenu:
    """ Dropdown menu of values.

    TODO: 
     - implement a selection mechanism
     - move selected value to top
     - potentially highlighting on hover
    """

    def __init__(self, x, y):
        self.values = ["Foo", "Bar", "Baz", "Baz", "Bing", "Bang", "Bong"]
        self.index = 0

        self.dropped_down = False
        self.x, self.y = x, y
        self.font_16_pt = pygame.font.Font("Tengoku.ttf", 16)

        self.max_text_len = max([self.font_16_pt.size(i) for i in self.values])
        self.text_size = self.max_text_len
        self.image = pygame.Surface(self.text_size)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface: pygame.Surface):
        if self.dropped_down:
            h = self.text_size[1] * len(self.values)
            self.image = pygame.Surface((self.text_size[0], h))
            for k, v in enumerate(self.values):
                self.image.blit(
                    self.font_16_pt.render(v, True, "#FFFFFF"), (0, k * self.text_size[1])
                )
        else:
            self.image = pygame.Surface(self.text_size)
            self.image.blit(
                self.font_16_pt.render(self.values[self.index], True, "#FFFFFF"), (0, 0)
            )

        self.rect.size = self.image.get_rect().size
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

