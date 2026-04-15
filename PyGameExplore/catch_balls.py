import pygame
import random

def run_game():
    pygame.init()
    WIDTH, HEIGHT = 200, 250
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catch the Falling Balls (Tutorial)")

    # Configuration
    ROWS, COLS = 3, 4
    CELL_W, CELL_H = WIDTH // COLS, HEIGHT // ROWS
    safe_cols = {r: random.sample(range(COLS), 2) for r in range(ROWS)}

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    PINK = (255, 192, 203)
    BLUE_DARK = (25, 25, 112)
    BLUE_LIGHT = (176, 224, 230)
    BROWN = (139, 69, 19)
    GOLD = (255, 215, 0)

    # Settings
    BALL_RADIUS = 16
    BALL_SPEED = 4
    BASE_PLAYER_RADIUS = 16
    TARGET_TOTAL = 60
    SPAWN_LIMIT = 150

    # Fonts
    font_default = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 18)
    font_large = pygame.font.SysFont(None, 32)

    # Message state
    t_message = ""
    t_start = 0
    # MESSAGE_DURATION = 1500  # Remove this. Message stays until key press.
    game_paused = False
    first_blue_caught = False
    first_red_caught = False
    first_brown_caught = False
    show_counter = False

    # Linear interpolation
    def lerp_color(c1, c2, t):
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    class Ball(pygame.sprite.Sprite):
        def __init__(self, color, x_pos):
            super().__init__()
            self.color = color
            self.image = pygame.Surface((BALL_RADIUS*2, BALL_RADIUS*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
            self.rect = self.image.get_rect(x=x_pos, y=random.randint(-HEIGHT, -BALL_RADIUS))

        def update(self):
            self.rect.y += BALL_SPEED
            if self.rect.y > HEIGHT:
                self.kill()

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.blue_catches = 0
            self.red_catches = 0
            self.brown_catches = 0
            self.exiting = False
            self.radius = BASE_PLAYER_RADIUS
            self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
            self.rect.centerx = WIDTH // 2
            self.rect.bottom = HEIGHT - 5

        def update(self, ml, mr, mu, md):
            if self.exiting:
                self.rect.y -= 2
                return
            speed = 1 + self.blue_catches
            if ml and self.rect.left > 0:
                self.rect.x -= speed
            if mr and self.rect.right < WIDTH:
                self.rect.x += speed
            if self.blue_catches >= 15:
                if mu and self.rect.top > 0:
                    self.rect.y -= speed
                if md and self.rect.bottom < HEIGHT:
                    self.rect.y += speed

        def draw(self, surface):
            # update radius and rect
            # radius increases at half rate per brown catch
            self.radius = BASE_PLAYER_RADIUS + int(self.brown_catches * 0.2)
            cx, cy = self.rect.center
            self.rect.size = (self.radius*2, self.radius*2)
            self.rect.center = (cx, cy)

            # exit bar overlay
            if self.exiting:
                surface.fill(WHITE, (0, 0, WIDTH, HEIGHT//4))

            # second red phase: mix all
            wbr = 0  # Initialize wbr here
            if self.red_catches >= 2:  # Only calculate wbr if at least 2 red balls caught
                total = self.blue_catches + self.red_catches + self.brown_catches
                w_b = self.blue_catches / max(total, 1)
                w_r = self.red_catches / max(total, 1)
                wbr = self.brown_catches / max(total, 1)
                dark = tuple(int(BLUE_DARK[i]*w_b + RED[i]*w_r + BROWN[i]*wbr) for i in range(3))
                light = tuple(int(BLUE_LIGHT[i]*w_b + PINK[i]*w_r + GOLD[i]*wbr) for i in range(3))
                color = lerp_color(dark, light, min(total, TARGET_TOTAL)/TARGET_TOTAL)
                pygame.draw.circle(surface, color, (cx, cy), self.radius)
                return

            # base circle
            circ = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(circ, WHITE, (self.radius, self.radius), self.radius)

            # blue half
            if self.blue_catches > 0:
                t = min(self.blue_catches, TARGET_TOTAL) / TARGET_TOTAL
                cb = lerp_color(BLUE_DARK, BLUE_LIGHT, t)
                half = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(half, cb, (self.radius, self.radius), self.radius)
                half.fill((0,0,0,0), (self.radius,0,self.radius,2*self.radius))
                circ.blit(half, (0,0))

            # red half
            if self.red_catches > 0:
                t = min(self.red_catches, TARGET_TOTAL) / TARGET_TOTAL
                cr = lerp_color(RED, PINK, t)
                half = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(half, cr, (self.radius, self.radius), self.radius)
                half.fill((0,0,0,0), (0,0,self.radius,2*self.radius))
                circ.blit(half, (0,0))

            # brown border
            if self.brown_catches > 0:
                pygame.draw.circle(circ, BROWN, (self.radius, self.radius), self.radius, width=3)

            surface.blit(circ, (cx-self.radius, cy-self.radius))

    # setup sprites
    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    init_ball = Ball(BLUE_DARK, WIDTH//2)
    init_ball.rect.center = (WIDTH//2, 0)
    balls.add(init_ball)

    spawn_count = 1
    running = True
    can_move = False
    c_red = False
    b_budget, r_budget = 1, 1
    x_credit = 0
    clock = pygame.time.Clock()

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_paused and event.type == pygame.KEYDOWN:
                game_paused = False
                t_message = ""  # Clear message on key press

        keys = pygame.key.get_pressed()
        # only allow movement after catching initial ball and when not paused
        if (can_move or player.exiting) and not game_paused:
            player.update(keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN])

        # end-phase
        if player.exiting and player.rect.top <= HEIGHT//4:
            break

        if not game_paused:
            balls.update()
            for b in balls:
                screen.blit(b.image, b.rect)

            # collisions
            for b in pygame.sprite.spritecollide(player, balls, False):
                if b.color == BLUE_DARK and (player.blue_catches < b_budget or x_credit > 0):
                    if player.blue_catches >= b_budget:
                        x_credit -= 1
                    player.blue_catches += 1
                    if not first_blue_caught:
                        t_message = "Clue\nTo Act\nObtained\nPress left arrow key"; t_start = pygame.time.get_ticks(); game_paused = True; first_blue_caught = True
                    elif player.blue_catches == 15:
                        t_message = "To Act Lvl Up\nPress UP"; t_start = pygame.time.get_ticks(); game_paused = True
                    b.kill()
                elif b.color == RED and (player.red_catches < r_budget or x_credit > 0):
                    if player.red_catches >= r_budget:
                        x_credit -= 1
                    player.red_catches += 1; c_red = True
                    if not first_red_caught:
                        t_message = "Clue\nTo React\nObtained\nPress any key"; t_start = pygame.time.get_ticks(); game_paused = True; first_red_caught = True
                    elif player.red_catches == 1:
                        t_message = "To React\nObtained"; t_start = pygame.time.get_ticks()
                    b.kill()
                elif b.color == BROWN and c_red:
                    player.brown_catches += 1; x_credit += 1; show_counter = True
                    if not first_brown_caught:
                        t_message = "Clue\nTo Contain\nObtained\nCounter Displayed\nPress any key"; t_start = pygame.time.get_ticks(); game_paused = True; first_brown_caught = True
                    elif player.brown_catches == 1:
                        t_message = "To Contain\nObtained"; t_start = pygame.time.get_ticks()
                    b.kill()

            if not can_move and pygame.sprite.collide_rect(player, init_ball):
                can_move = True; init_ball.kill()

            if can_move and len(balls) < 10 and spawn_count < SPAWN_LIMIT:
                spawn_count += 1
                row = random.randint(0, ROWS-1)
                cols = [c for c in range(COLS) if c not in safe_cols[row]]
                x = random.choice(cols)*CELL_W + random.randint(0, CELL_W-2*BALL_RADIUS)
                balls.add(Ball(random.choice([RED, BLUE_DARK, BROWN]), x))

            if spawn_count >= SPAWN_LIMIT and not balls and not player.exiting:
                player.exiting = True

        player.draw(screen)
        if player.exiting:
            screen.fill(WHITE, (0,0,WIDTH,HEIGHT//4))

        # draw messages & counter...
        now = pygame.time.get_ticks()
        if t_message: # changed from  if t_message and now - t_start < MESSAGE_DURATION:
            lines = t_message.split("\n")
            surfs = []
            if len(lines) == 4:
                surfs.append(font_small.render(lines[0], True, WHITE))
                surfs.append(font_large.render(lines[1], True, WHITE))
                surfs.append(font_large.render(lines[2], True, WHITE))
                surfs.append(font_small.render(lines[3], True, WHITE))
            elif len(lines) == 2:
                surfs.append(font_large.render(lines[0], True, WHITE))
                surfs.append(font_small.render(lines[1], True, WHITE))
            elif len(lines) == 3:
                surfs.append(font_small.render(lines[0], True, WHITE))
                surfs.append(font_large.render(lines[1], True, WHITE))
                surfs.append(font_large.render(lines[2], True, WHITE))
            else:
                for line in lines:
                    if "Press any key" in line:
                        surfs.append(font_small.render(line, True, WHITE))  # Small for "Press any key"
                    else:
                        surfs.append(font_large.render(line, True, WHITE))  # Large for other messages

            h = sum(s.get_height() for s in surfs)
            y_offset = (HEIGHT - h) // 2
            for surf in surfs:
                x_off = (WIDTH - surf.get_width()) // 2
                screen.blit(surf, (x_off, y_offset))
                y_offset += surf.get_height()

        if show_counter and player.brown_catches > 0:
            cnt = f"{player.blue_catches + player.red_catches}/{b_budget + r_budget + player.brown_catches}"
            counter_surf = font_default.render(cnt, True, WHITE)
            counter_rect = counter_surf.get_rect(midtop=(WIDTH // 2, 5))  # Centered at the top
            screen.blit(counter_surf, counter_rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    # return final color and actual radius, plus counts
    if player.brown_catches > 0:
        t = min(player.brown_catches, TARGET_TOTAL) / TARGET_TOTAL
        final_color = lerp_color(BROWN, GOLD, t)
    elif player.red_catches >= 2:
        tot = player.blue_catches + player.red_catches + player.brown_catches
        wb = player.blue_catches / max(tot, 1)
        wr = player.red_catches / max(tot, 1)
        wbr = player.brown_catches / max(tot, 1)
        dark = tuple(int(BLUE_DARK[i]*wb + RED[i]*wr + BROWN[i]*wbr) for i in range(3))
        light = tuple(int(BLUE_LIGHT[i]*wb + PINK[i]*wr + GOLD[i]*wbr) for i in range(3))
        final_color = lerp_color(dark, light, min(tot, TARGET_TOTAL) / TARGET_TOTAL)
    elif player.blue_catches > 0:
        final_color = BLUE_DARK
    elif player.red_catches > 0:
        final_color = RED
    else:
        final_color = WHITE

    # Final radius matches last drawn size
    final_radius = BASE_PLAYER_RADIUS + int(player.brown_catches * 0.2)

    pygame.quit()
    return final_color, final_radius, player.blue_catches, player.red_catches, player.brown_catches
