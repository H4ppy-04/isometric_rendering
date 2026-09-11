"""
A small pygame tech demo.

Features:
- A diagonal, two-tone scrolling background.
- A tile "world" (loaded from map.txt) that gently bobs up and down and
  can be shaken (e.g. as a hit/impact effect).
- A glowing particle trail that follows the player.
- Mouse-triggered "spark" bursts plus a constant spark emitter in the corner of
  the screen.
- An intro dialogue box: letterbox bars slide in, the intro line types
  itself out character by character with a little pop animation, then
  everything fades out after a few seconds.

Controls:
- Arrow keys to move.
- Hold the mouse button to emit sparks from the cursor.
- Space bar to trigger a screen shake.
- Escape to quit.
"""

import math
import os
import random
import sys
from typing import Sequence

import pygame
from pygame.locals import BLEND_RGB_ADD

from ui import *

pygame.init()

Vector2 = list[float]
Color = tuple[int, int, int] | tuple[int, int, int, int]

TWO_PI = math.tau
HALF_PI = math.pi / 2

DEFAULT_SCALE = 1.0
DEFAULT_DRAW_OFFSET = (0.0, 0.0)

SPEED_DECELERATION = 0.1

SPARK_HEAD_LENGTH = 1.0
SPARK_TAIL_LENGTH = 3.5
SPARK_WIDTH = 0.3

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
FRAMERATE = 60

BACKGROUND_SURFACE_HEIGHT = 900
BACKGROUND_STRIPE_THICKNESS = 50
BACKGROUND_SCROLL_SPEED = 0.1  # pixels per millisecond
BACKGROUND_COLOR_A = "#3a002c"
BACKGROUND_COLOR_B = "#000000"

WORLD_SURFACE_SIZE = 300
WORLD_BOB_SPEED = 0.05
WORLD_BOB_AMPLITUDE = 10

TILE_SIZE = 16

FONT_PATH = os.path.join("assets", "fonts", "Tengoku.ttf")
UI_FONT_SIZE = 19
# NOTE: this bigger font is loaded but never actually used for rendering -
# the dialogue box below is drawn with the smaller UI font instead. Kept
# in case that's meant to change; safe to delete if it really is unused.
DIALOGUE_FONT_SIZE = 32

INTRO_TEXT = "The new world awaits...."
TEXT_REVEAL_SPEED = 20
LETTER_POP_DURATION = 0.15
TEXT_FADE_SPEED = 300
INTRO_HOLD_FRAMES = 150

DIALOGUE_BAR_OPEN_HEIGHT = 120
DIALOGUE_BAR_EASE = 0.1

SCREEN_SHAKE_DEFAULT_MAGNITUDE = 5

# NOTE: the x-range is (0.3, 0.3) so it's currently always exactly 0.3 -
# probably meant to vary like the y-range does. Left as in the original.
PARTICLE_VELOCITY_X_RANGE = (0.3, 0.3)
PARTICLE_VELOCITY_Y_RANGE = (-1.0, 0.3)
PARTICLE_RADIUS_RANGE = (1.5, 2.0)
PARTICLE_GRAVITY = 0.15
PARTICLE_SHRINK_RATE = 0.1
PARTICLE_GLOW_SCALE = 2
PARTICLE_GLOW_COLOR = (20, 20, 20)

SPARK_COLOR = (255, 255, 255)
SPARK_WIDTH = 2
SPARK_SPEED_RANGE = (3, 6)
CORNER_SPARK_POS = (SCREEN_WIDTH - 50, 50)


INVENTORY_SLOT_COUNT = 8
INVENTORY_SLOT_SIZE = 32

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCORE_TEXT_COLOR = (200, 250, 180)


def load_sprite(filename, use_alpha=False, colorkey="#000000"):
    """Load an image from the sprites/ folder. By default, black is treated
    as transparent; pass use_alpha=True for images with their own alpha
    channel instead."""
    path = os.path.join("assets", "sprites", filename)
    if use_alpha:
        return pygame.image.load(path).convert_alpha()
    image = pygame.image.load(path).convert()
    image.set_colorkey(colorkey)
    return image


def make_glow_surface(radius, color):
    """A soft filled circle used as an additive 'glow' behind particles."""
    radius = max(1, int(radius))
    surface = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surface, color, (radius, radius), radius)
    surface.set_colorkey(BLACK)
    return surface


def load_map_grid(path):
    """Read a text file of single-digit rows into a 2D list of ints."""
    with open(os.path.join("data", "maps", path)) as f:
        return [[int(char) for char in line] for line in f.read().split("\n")]


def build_background_surface():
    """A tall surface tiled with diagonal two-tone stripes, scrolled during play."""
    surface = pygame.Surface((SCREEN_WIDTH, BACKGROUND_SURFACE_HEIGHT))
    stripe_positions = range(
        -BACKGROUND_SURFACE_HEIGHT * 2,
        BACKGROUND_SURFACE_HEIGHT,
        BACKGROUND_STRIPE_THICKNESS,
    )
    for i, offset in enumerate(stripe_positions):
        color = BACKGROUND_COLOR_A if i % 2 == 0 else BACKGROUND_COLOR_B
        pygame.draw.line(
            surface,
            color,
            (SCREEN_WIDTH * 2, offset),
            (-SCREEN_WIDTH, SCREEN_HEIGHT + offset),
            BACKGROUND_STRIPE_THICKNESS,
        )
    return surface


def build_world_surface(map_grid, grass_sprite, teleporter_sprite):
    """Bake the static tile layer (grass / teleporters) into one surface."""
    surface = pygame.Surface((WORLD_SURFACE_SIZE, WORLD_SURFACE_SIZE))
    for y, row in enumerate(map_grid):
        for x, tile in enumerate(row):
            tile_pos = (150 + x * 10 - y * 10, 100 + x * 5 + y * 5)
            if tile == 1:
                surface.blit(grass_sprite, tile_pos)
            elif tile == 2:
                surface.blit(teleporter_sprite, tile_pos)
    surface.set_colorkey(BLACK)
    return surface


class Spark:
    """A small directional particle that gradually loses speed over time."""

    def __init__(
        self,
        location: Vector2,
        angle: float,
        speed: float,
        color: Color,
        scale: float = DEFAULT_SCALE,
    ) -> None:
        """
        Initialise a spark.

        Args:
            location: The spark's [x, y] position.
            angle: Direction of travel in radians.
            speed: Initial movement speed.
            color: RGB or RGBA colour used when drawing the spark.
            scale: Multiplier applied to the spark's rendered size.
        """
        self.location = location
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def point_towards(self, target_angle: float, rotation_rate: float) -> None:
        """
        Rotate the spark towards a target angle.

        The spark will rotate by at most ``rotation_rate`` radians per call
        and will take the shortest path around the circle.

        Args:
            target_angle: Angle to rotate towards, in radians.
            rotation_rate: Maximum rotation per update, in radians.
        """
        angle_difference = (
            (target_angle - self.angle + math.pi * 3) % TWO_PI
        ) - math.pi

        if angle_difference == 0:
            return

        rotation_direction = math.copysign(1.0, angle_difference)

        if abs(angle_difference) < rotation_rate:
            self.angle = target_angle
        else:
            self.angle += rotation_rate * rotation_direction

    def calculate_movement(self, dt: float) -> Vector2:
        """
        Calculate the spark's movement for the current frame.

        Args:
            dt: Delta time since the previous update.

        Returns:
            The [x, y] movement to apply this frame.
        """
        return [
            math.cos(self.angle) * self.speed * dt,
            math.sin(self.angle) * self.speed * dt,
        ]

    def velocity_adjust(
        self,
        friction: float,
        force: float,
        terminal_velocity: float,
        dt: float,
    ) -> None:
        """
        Adjust the spark's direction based on gravity/force and friction.

        Note:
            This method currently changes the spark's angle but does not
            update its speed to match the resulting velocity vector.

        Args:
            friction: Multiplier applied to horizontal movement.
            force: Vertical force applied per second.
            terminal_velocity: Maximum downward velocity.
            dt: Delta time since the previous update.
        """
        movement = self.calculate_movement(dt)

        movement[1] = min(
            terminal_velocity,
            movement[1] + force * dt,
        )
        movement[0] *= friction

        self.angle = math.atan2(movement[1], movement[0])

    def move(self, dt: float) -> None:
        """
        Move the spark and reduce its speed.

        Args:
            dt: Delta time since the previous update.
        """
        movement = self.calculate_movement(dt)

        self.location[0] += movement[0]
        self.location[1] += movement[1]

        # Optional movement behaviours:
        #
        # self.point_towards(math.pi / 2, 0.02)
        # self.velocity_adjust(0.975, 0.2, 8, dt)
        # self.angle += 0.1

        self.speed -= SPEED_DECELERATION

        if self.speed <= 0:
            self.speed = 0
            self.alive = False

    def draw(
        self,
        surface: pygame.Surface,
        offset: Sequence[float] = DEFAULT_DRAW_OFFSET,
    ) -> None:
        """
        Draw the spark as a directional polygon.

        Args:
            surface: Pygame surface to draw onto.
            offset: [x, y] offset applied to the spark's position.
        """
        if not self.alive:
            return

        x = self.location[0] + offset[0]
        y = self.location[1] + offset[1]

        forward_x = math.cos(self.angle)
        forward_y = math.sin(self.angle)

        perpendicular_x = math.cos(self.angle + HALF_PI)
        perpendicular_y = math.sin(self.angle + HALF_PI)

        head_distance = self.speed * self.scale * SPARK_HEAD_LENGTH
        tail_distance = self.speed * self.scale * SPARK_TAIL_LENGTH
        width = self.speed * self.scale * SPARK_WIDTH

        points = [
            [
                x + forward_x * head_distance,
                y + forward_y * head_distance,
            ],
            [
                x + perpendicular_x * width,
                y + perpendicular_y * width,
            ],
            [
                x - forward_x * tail_distance,
                y - forward_y * tail_distance,
            ],
            [
                x - perpendicular_x * width,
                y - perpendicular_y * width,
            ],
        ]

        pygame.draw.polygon(surface, self.color, points)


class Player:
    def __init__(self, pos=(250, 250), speed=0.8):
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2()
        self.speed = speed

    def update(self):
        # NOTE: movement isn't scaled by dt, so it's tied to the frame rate
        # rather than real time. That's fine as long as FRAMERATE stays fixed.
        if self.direction.length_squared() > 0:
            self.direction.normalize_ip()
        self.pos += self.direction * self.speed


class ScreenShake:
    """Call start() to kick off a shake, then update() once per frame to get
    the (x, y) render offset to apply while it's active."""

    def __init__(self, magnitude=SCREEN_SHAKE_DEFAULT_MAGNITUDE):
        self.timer = 0
        self.magnitude = magnitude

    def start(self, duration, magnitude=SCREEN_SHAKE_DEFAULT_MAGNITUDE):
        self.timer = duration
        self.magnitude = magnitude

    def update(self):
        if self.timer <= 0:
            return [0, 0]
        self.timer -= 1
        return [random.randint(-self.magnitude, self.magnitude) for _ in range(2)]


class Particle:
    """A small glowing dot spawned at the player's position, used as a trail."""

    def __init__(self, pos):
        self.pos = [pos[0], pos[1]]
        self.velocity = [
            random.uniform(*PARTICLE_VELOCITY_X_RANGE),
            random.uniform(*PARTICLE_VELOCITY_Y_RANGE),
        ]
        self.radius = random.uniform(*PARTICLE_RADIUS_RANGE)

    @property
    def alive(self):
        return self.radius > 0

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.velocity[1] += PARTICLE_GRAVITY
        self.radius -= PARTICLE_SHRINK_RATE

    def draw(self, surface):
        center = (int(self.pos[0]), int(self.pos[1]))
        pygame.draw.circle(surface, WHITE, center, int(self.radius))

        glow_radius = self.radius * PARTICLE_GLOW_SCALE
        glow = make_glow_surface(glow_radius, PARTICLE_GLOW_COLOR)
        surface.blit(
            glow,
            (int(self.pos[0] - glow_radius), int(self.pos[1] - glow_radius)),
            special_flags=BLEND_RGB_ADD,
        )


class IntroSplasher:
    """
    Introductory screen displaying pygame logo.
    """

    def __init__(self):
        self.alpha = 0.0
        self.is_fading_out = False
        self.is_fading_in = True
        self.frames_elapsed = 0
        self.active = True

        self.pygame_logo = pygame.transform.scale_by(
            load_sprite("pygame_logo.png", use_alpha=True), 0.5
        )

    def update(self):
        if self.is_fading_in:
            if self.alpha < 255.0:
                self.alpha += 5.0
            if self.alpha > 255.0:
                self.alpha = 255.0
            self.pygame_logo.set_alpha(self.alpha)
        if self.is_fading_out:
            self.is_fading_in = False
            # print(f"faidng out ({self.alpha}) - frames={self.frames_elapsed}")
            if self.alpha > 0.0:
                self.alpha -= 5.0
            if self.alpha < 0.0:
                self.alpha = 0.0
            else:
                self.is_fading_out = False
            self.pygame_logo.set_alpha(self.alpha)
        else:
            if self.frames_elapsed > 200:
                self.is_fading_out = True
            if self.frames_elapsed > 300:
                self.active = False

        self.frames_elapsed += 1

    def draw(self, surface: pygame.Surface):
        surface.fill("#000000")
        surface.blit(
            self.pygame_logo,
            self.pygame_logo.get_rect(
                center=pygame.display.get_surface().get_rect().center
            ),
        )
        pygame.display.update()


class IntroDialogue:
    """
    Letterbox bars plus a typewriter-style intro line.

    The bars ease open, the text reveals one character at a time (each new
    character "pops" in with a brief scale/offset animation), and after
    INTRO_HOLD_FRAMES frames the bars close again and the whole box fades out.
    """

    def __init__(self, font, text=INTRO_TEXT):
        self.font = font
        self.text = text

        self.visible_char_count = 0
        self.reveal_timer = 0.0
        self.pop_timer = 0.0

        self.bar_height = 0.0
        self.target_bar_height = DIALOGUE_BAR_OPEN_HEIGHT

        self.alpha = 255.0
        self.is_fading_out = False
        self.frames_elapsed = 0

    def update(self, dt):
        dt_seconds = dt / 1000

        self.bar_height += (
            self.target_bar_height - self.bar_height
        ) * DIALOGUE_BAR_EASE

        if self.visible_char_count < len(self.text):
            self.reveal_timer += dt_seconds
            if self.reveal_timer >= 1 / TEXT_REVEAL_SPEED:
                self.reveal_timer = 0.0
                self.visible_char_count += 1
                self.pop_timer = 0.0

        self.pop_timer += dt_seconds

        self.frames_elapsed += 1
        if self.frames_elapsed > INTRO_HOLD_FRAMES:
            self.target_bar_height = 0
            self.is_fading_out = True

        if self.is_fading_out:
            # Bug fix: this used to subtract `300 * dt` where dt is in
            # milliseconds (pygame.Clock.tick() returns ms), so alpha
            # dropped from 255 to 0 within a single frame instead of
            # fading smoothly. Converting dt to seconds first makes
            # TEXT_FADE_SPEED behave as "alpha units removed per second".
            self.alpha -= TEXT_FADE_SPEED * dt_seconds
            self.alpha = max(0.0, self.alpha)

    def draw(self, surface, x=50, y=800):
        pygame.draw.rect(surface, BLACK, (0, 0, SCREEN_WIDTH, int(self.bar_height)))
        pygame.draw.rect(
            surface,
            BLACK,
            (
                0,
                SCREEN_HEIGHT - int(self.bar_height),
                SCREEN_WIDTH,
                int(self.bar_height),
            ),
        )

        if self.visible_char_count == 0:
            return

        alpha = int(self.alpha)

        # Every character except the newest one, already fully "popped in".
        settled_text = self.text[: self.visible_char_count - 1]
        settled_surface = self.font.render(settled_text, True, WHITE)
        # Bug fix: previously only the newest character had alpha applied
        # to it, so the rest of the sentence never faded along with it.
        # Applying it here too makes the whole line fade out together.
        settled_surface.set_alpha(alpha)
        surface.blit(settled_surface, (x, y))

        # The newest character pops in with a quick scale + rise animation.
        newest_char = self.text[self.visible_char_count - 1]
        progress = min(self.pop_timer / LETTER_POP_DURATION, 1)
        offset_y = -30 * (1 - progress) ** 2
        scale = 1 + 0.3 * (1 - progress)

        char_surface = self.font.render(newest_char, True, WHITE)
        w, h = char_surface.get_size()
        char_surface = pygame.transform.smoothscale(
            char_surface, (max(1, int(w * scale)), max(1, int(h * scale)))
        )
        char_surface.set_alpha(alpha)

        surface.blit(char_surface, (x + settled_surface.get_width(), y + offset_y))


class Game:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption("Isometric Render and Graphics Testing")
        self.clock = pygame.time.Clock()

        self.ui_font = pygame.font.Font(FONT_PATH, size=UI_FONT_SIZE)
        self.dialogue_font = pygame.font.Font(FONT_PATH, size=DIALOGUE_FONT_SIZE)

        self.background = build_background_surface()
        self.bg_scroll = 0.0

        self.grass_sprite = load_sprite("grass.png")
        self.teleporter_sprite = load_sprite("teleporter.png")
        # Loaded but not drawn anywhere yet - reserved for a future inventory bar.
        self.inventory_frame_sprite = load_sprite("inventory_frame.png", use_alpha=True)

        map_grid = load_map_grid("map.txt")
        self.world_tiles = build_world_surface(
            map_grid, self.grass_sprite, self.teleporter_sprite
        )
        self.world_surface = pygame.Surface((WORLD_SURFACE_SIZE, WORLD_SURFACE_SIZE))
        self.world_surface.set_colorkey(BLACK)
        self.world_bob_phase = 0.0
        self.world_offset_y = 0

        self.player = Player()
        self.particles = []

        self.sparks = []
        self.mouse_pos = (0, 0)
        self.mouse_spark_active = False

        self.screen_shake = ScreenShake()
        self.screen_shake.start(8)
        self.render_offset = [0, 0]

        self.splash = IntroSplasher()
        self.dialogue = IntroDialogue(self.ui_font)

        self.score = 0
        self.dt = 0.0
        self.running = True

        self.reset_button = Button("Reset", SCREEN_WIDTH - 100, 100)

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.dt = self.clock.tick(FRAMERATE)

        pygame.quit()
        sys.exit()

    def reset(self):
        self.bg_scroll = 0.0
        self.render_offset = [0, 0]
        # self.splash = IntroSplasher()
        self.dialogue = IntroDialogue(self.ui_font)
        self.world_bob_phase = 0.0
        self.world_offset_y = 0

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_spark_active = True
                if self.reset_button.rect.collidepoint(self.mouse_pos):
                    self.reset()
                    break
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_spark_active = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event.key)

    def _handle_keydown(self, key):
        if self.splash.active:
            self.splash.active = False
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.screen_shake.start(5)
        elif key == pygame.K_UP:
            self.player.direction.y = -1
        elif key == pygame.K_DOWN:
            self.player.direction.y = 1
        elif key == pygame.K_LEFT:
            self.player.direction.x = -1
        elif key == pygame.K_RIGHT:
            self.player.direction.x = 1

    def _handle_keyup(self, key):
        if key in (pygame.K_UP, pygame.K_DOWN):
            self.player.direction.y = 0
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.player.direction.x = 0

    def _update(self):
        if self.splash.active:
            self.splash.update()
            return
        self.particles.append(Particle(self.player.pos))
        self.player.update()

        self.dialogue.update(self.dt)
        self.render_offset = self.screen_shake.update()

        self.bg_scroll = (
            self.bg_scroll - BACKGROUND_SCROLL_SPEED * self.dt
        ) % BACKGROUND_SURFACE_HEIGHT

        self.world_bob_phase = (self.world_bob_phase + WORLD_BOB_SPEED) % (2 * math.pi)
        self.world_offset_y = round(
            -math.sin(self.world_bob_phase) * WORLD_BOB_AMPLITUDE
        )

        if self.mouse_spark_active:
            self.sparks.append(self._make_spark(list(self.mouse_pos)))
        # self.sparks.append(self._make_spark(list(CORNER_SPARK_POS)))
        for spark in self.sparks:
            spark.move(1)

        for particle in self.particles[:]:
            particle.update()
            if not particle.alive:
                self.particles.remove(particle)
        
        self.reset_button.update()

    @staticmethod
    def _make_spark(pos):
        angle = math.radians(random.randint(0, 360))
        speed = random.randint(*SPARK_SPEED_RANGE)
        return Spark(pos, angle, speed, SPARK_COLOR, SPARK_WIDTH)

    def _draw(self):
        if self.splash.active:
            self.splash.draw(self.display)
            return

        self.display.blit(
            self.background, (0, self.bg_scroll - BACKGROUND_SURFACE_HEIGHT)
        )
        self.display.blit(self.background, (0, self.bg_scroll))

        self.world_surface.fill(BLACK)
        self.world_surface.blit(self.world_tiles, (0, 0))
        for particle in self.particles:
            particle.draw(self.world_surface)

        self.display.blit(
            pygame.transform.scale(self.world_surface, self.display.get_size()),
            (self.render_offset[0], self.world_offset_y + self.render_offset[1]),
        )

        for i in reversed(range(len(self.sparks))):
            spark = self.sparks[i]
            spark.draw(self.display)
            if not spark.alive:
                self.sparks.pop(i)

        self.display.blit(
            self.ui_font.render(f"Score: {self.score}", True, SCORE_TEXT_COLOR),
            (30 + self.render_offset[0], 50 - self.world_offset_y),
        )
        self.display.blit(
            self.ui_font.render(
                f"FPS: {round(self.clock.get_fps(), 2)}", True, SCORE_TEXT_COLOR
            ),
            (30 + self.render_offset[0], 80 - self.world_offset_y),
        )

        self.reset_button.draw(self.display)
        self.dialogue.draw(self.display)


if __name__ == "__main__":
    Game().run()
