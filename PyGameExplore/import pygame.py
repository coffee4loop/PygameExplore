import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 200, 250
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Falling Balls")

# Colors
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
RED        = (255, 0, 0)
PINK       = (255, 192, 203)
BLUE_DARK  = (25, 25, 112)    # midnight blue
BLUE_LIGHT = (176, 224, 230)  # powder blue
BROWN      = (139, 69, 19)
GOLD       = (255, 215, 0)

# Ball settings
BALL_RADIUS = 16
BALL_SPEED  = 1

# Player settings
PLAYER_RADIUS = 16

# Font for fraction counter
font = pygame.font.SysFont(None, 24)

# Utility: linear interpolation between two colors
def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.image = pygame.Surface((BALL_RADIUS*2, BALL_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.color = color

    def update(self):
        self.rect.y += BALL_SPEED
        if self.rect.y > HEIGHT:
            self.kill()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect(0, 0, PLAYER_RADIUS*2, PLAYER_RADIUS*2)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom  = HEIGHT - 5
        self.blue_catches  = 0
        self.red_catches   = 0
        self.brown_catches = 0

    def update(self, move_left, move_right, move_up, move_down):
        speed = 1 + self.blue_catches
        if move_left and self.rect.left > 0:
            self.rect.x -= speed
        if move_right and self.rect.right < WIDTH:
            self.rect.x += speed
        if self.blue_catches >= 15:
            if move_up and self.rect.top > 0:
                self.rect.y -= speed
            if move_down and self.rect.bottom < HEIGHT:
                self.rect.y += speed

    def draw(self, surface):
        cx, cy = self.rect.center
        has_blue = self.blue_catches > 0
        has_red  = self.red_catches > 0

        # Draw brown border outside original radius
        if self.brown_catches > 0:
            t_b = min(self.brown_catches, 25) / 25.0
            border_color = lerp_color(BROWN, GOLD, t_b)
            border_w = int(1 + t_b * 9)
            outer_r = PLAYER_RADIUS + border_w
            pygame.draw.circle(surface, border_color, (cx, cy), outer_r)
        else:
            border_w = 0

        r = PLAYER_RADIUS

        if not has_blue and not has_red:
            pygame.draw.circle(surface, WHITE, (cx, cy), r)
            return

        half_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)

        if has_blue and not has_red:
            t_blue = min(self.blue_catches, 25) / 25.0
            left_color = lerp_color(BLUE_DARK, BLUE_LIGHT, t_blue)
            pygame.draw.circle(half_surf, left_color, (r, r), r)
            overlay = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, WHITE, (r, r), r)
            overlay.fill((0,0,0,0), rect=(0,0,r,r*2))
            half_surf.blit(overlay, (0,0))
            surface.blit(half_surf, (cx-r, cy-r))
            return

        if has_red and not has_blue:
            t_red = min(self.red_catches, 25) / 25.0
            right_color = lerp_color(RED, PINK, t_red)
            pygame.draw.circle(half_surf, WHITE, (r, r), r)
            overlay = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, right_color, (r, r), r)
            overlay.fill((0,0,0,0), rect=(0,0,r,r*2))
            half_surf.blit(overlay, (0,0))
            surface.blit(half_surf, (cx-r, cy-r))
            return

        t_blue = min(self.blue_catches, 25) / 25.0
        t_red  = min(self.red_catches, 25) / 25.0
        left_color = lerp_color(BLUE_DARK, BLUE_LIGHT, t_blue)
        right_color= lerp_color(RED, PINK, t_red)
        pygame.draw.circle(half_surf, left_color, (r, r), r)
        overlay = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(overlay, right_color, (r, r), r)
        overlay.fill((0,0,0,0), rect=(0,0,r,r*2))
        half_surf.blit(overlay, (0,0))
        surface.blit(half_surf, (cx-r, cy-r))

# Sprite groups
all_sprites = pygame.sprite.Group()
balls      = pygame.sprite.Group()
player     = Player()
all_sprites.add(player)

# Spawn tracking
spawn_count = 1
first_blue = Ball(BLUE_DARK)
first_blue.rect.center = (WIDTH//2, 0)
balls.add(first_blue)
all_sprites.add(first_blue)

def add_new_balls():
    global spawn_count
    if len(balls) < 10 and spawn_count < 150:
        spawn_count += 1
        color = random.choice([RED, BLUE_DARK, BROWN])
        ball = Ball(color)
        ball.rect.x = random.randint(0, WIDTH - BALL_RADIUS*2)
        ball.rect.y = random.randint(-HEIGHT, 0)
        balls.add(ball)
        all_sprites.add(ball)

running         = True
white_filling   = False
player_can_move = False
caught_red      = False
blue_budget     = 1
red_budget      = 1
extra_credits   = 0

clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    mv_l, mv_r = keys[pygame.K_LEFT], keys[pygame.K_RIGHT]
    mv_u, mv_d = keys[pygame.K_UP], keys[pygame.K_DOWN]
    if player_can_move:
        player.update(mv_l, mv_r, mv_u, mv_d)

    for b in balls:
        b.update()

    for b in pygame.sprite.spritecollide(player, balls, False):
        if b.color == BROWN:
            if caught_red:
                player.brown_catches += 1
                extra_credits += 1
                balls.remove(b); all_sprites.remove(b)
            continue
        if b.color == BLUE_DARK:
            can = (player.blue_catches < blue_budget) or (extra_credits > 0)
            if can:
                if player.blue_catches >= blue_budget:
                    extra_credits -= 1
                player.blue_catches += 1
                balls.remove(b); all_sprites.remove(b)
            continue
        if b.color == RED:
            can = (player.red_catches < red_budget) or (extra_credits > 0)
            if can:
                if player.red_catches >= red_budget:
                    extra_credits -= 1
                player.red_catches += 1
                caught_red = True
                balls.remove(b); all_sprites.remove(b)
            continue

    if not player_can_move and pygame.sprite.collide_rect(player, first_blue):
        player_can_move = True

    if player_can_move:
        add_new_balls()

    if spawn_count >= 150 and len(balls) == 0:
        white_filling = True

    for b in balls:
        screen.blit(b.image, b.rect)
    player.draw(screen)

    if white_filling:
        screen.fill(WHITE, (0, 0, WIDTH, HEIGHT // 4))

    if player.brown_catches > 0:
        num = player.blue_catches + player.red_catches
        den = blue_budget + red_budget + player.brown_catches
        txt = font.render(f"{num}/{den}", True, WHITE)
        screen.blit(txt, (5,5))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
