import pygame
import random
import math

# --- Constants ---
TILE_SIZE = 20
GHOST_OSC_TILES = 2  # radius in tiles for circular motion
ROWS, COLS = 12, 28  # grid dimensions
FPS = 60
EXIT_X, EXIT_Y = COLS - 1, 0  # exit position (top-right corner)

# Build maze: solid border, empty interior, with entrance and exit
maze_list = [
    ['#' if x == 0 or x == COLS - 1 or y == 0 or y == ROWS - 1 else ' ' for x in range(COLS)]
    for y in range(ROWS)
]
# Open entrance & exit corridors
maze_list[ROWS - 1][0] = ' '
maze_list[ROWS - 2][0] = ' '
maze_list[0][COLS - 1] = ' '
maze_list[1][COLS - 1] = ' '
MAZE = ["".join(row) for row in maze_list]

# Colors
COLOR_BG = (0, 0, 0)
COLOR_WALL = (255, 255, 255)
COLOR_PLAYER_DEFAULT = (255, 255, 0)
COLOR_PLAYER_RED = (255, 0, 0)
# Ghosts now all green, varied shades
COLOR_GHOSTS = [(0, 255, 0), (0, 200, 0), (0, 150, 0), (0, 100, 0)]


class Entity:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.pix_x = x * TILE_SIZE + TILE_SIZE // 2
        self.pix_y = y * TILE_SIZE + TILE_SIZE // 2

    def draw(self, screen, color):
        pygame.draw.circle(
            screen, color,
            (int(self.pix_x), int(self.pix_y)),
            TILE_SIZE // 2 - 2
        )


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.can_move_flag = True  # Add a flag to control movement
        self.stop_duration = 0

    def move(self, dx, dy):
        if self.can_move_flag:  # Only move if allowed
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and MAZE[ny][nx] != '#':
                self.grid_x, self.grid_y = nx, ny
                self.pix_x = nx * TILE_SIZE + TILE_SIZE // 2
                self.pix_y = ny * TILE_SIZE + TILE_SIZE // 2

    def can_move(self, dx, dy):
        """Checks if the player can move to a new position."""
        nx, ny = self.grid_x + dx, self.grid_y + dy
        return 0 <= nx < COLS and 0 <= ny < ROWS and MAZE[ny][nx] != '#'

    def draw(self, screen, color, is_red=False):
        """Draws the player.  If is_red, draw with larger radius."""
        base_radius = TILE_SIZE // 2 - 2
        radius = base_radius * 2 if is_red else base_radius
        pygame.draw.circle(
            screen, color,
            (int(self.pix_x), int(self.pix_y)),
            radius
        )

    def red_radius(self):
        """Returns the radius of the player when red."""
        return (TILE_SIZE // 2 - 2) * 2


class Ghost(Entity):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.orig_pix_x = self.pix_x  # Store original position for orbit center
        self.orig_pix_y = self.pix_y
        self.color = color
        self.radius = TILE_SIZE // 2 - 2
        self.orbit_radius = GHOST_OSC_TILES * TILE_SIZE  # Orbit radius
        self.angle = random.uniform(0, 2 * math.pi)  # Random starting angle
        self.angular_speed = 0.03  # Speed of orbit

    def update(self):
        """Update ghost position for circular oscillation."""
        self.angle = (self.angle + self.angular_speed) % (2 * math.pi)
        self.pix_x = self.orig_pix_x + math.cos(self.angle) * self.orbit_radius
        self.pix_y = self.orig_pix_y + math.sin(self.angle) * self.orbit_radius



# Main entry point
def run_next_stage(red): # Changed to only accept red
    pygame.init()
    screen = pygame.display.set_mode((COLS * TILE_SIZE, ROWS * TILE_SIZE))
    pygame.display.set_caption("ASCII Maze – Exit After Reactions")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Tutorial screen
    reactions = red
    showing = True
    while showing:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                showing = False
        screen.fill(COLOR_BG)
        center_x = COLS * TILE_SIZE // 2
        center_y = ROWS * TILE_SIZE // 2
        lines = [
            (f"You have {reactions} reactions.", (center_x, center_y - 45)),
            ("PRESS SPACE to turn red and activate reaction.", (center_x, center_y - 15)),
            ("While red, you can consume a clue = +1 point.", (center_x, center_y + 15)),
            ("Press any key to start...", (center_x, center_y + 45)),
        ]
        for text, pos in lines:
            rendered_text = font.render(text, True, (255, 255, 255))
            text_rect = rendered_text.get_rect(center=pos)
            screen.blit(rendered_text, text_rect)
        pygame.display.flip()
        clock.tick(FPS)

    # Initialize game
    player = Player(0, ROWS - 1)
    player_color =  COLOR_PLAYER_DEFAULT
    is_red = False
    red_timer = 0
    score = 0
    red_balls = reactions
    exiting = False
    last_reaction = False
    stop_timer = 0
    remove_ghosts_timer = 0
    ghosts_removed = False
    hud_visible = True
    hud_start_time = pygame.time.get_ticks()
    HUD_DISPLAY_DURATION = 1000
    margin = GHOST_OSC_TILES
    spawn_cells = [
        (x, y)
        for y in range(1 + margin, ROWS - 1 - margin)
        for x in range(1 + margin, COLS - 1 - margin)
        if MAZE[y][x] != '#'
    ]
    ghosts = [Ghost(x, y, random.choice(COLOR_GHOSTS)) for x, y in random.sample(spawn_cells, 50)]

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                break
            elif e.type == pygame.KEYDOWN and not exiting:
                mapping = {pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_UP: (0, -1),
                           pygame.K_DOWN: (0, 1)}
                if e.key in mapping:
                    player.move(*mapping[e.key])
                if e.key == pygame.K_SPACE and red_balls > 0 and not is_red:
                    is_red = True
                    red_timer = FPS // 4
                    red_balls -= 1
                    hud_visible = True
                    hud_start_time = pygame.time.get_ticks()
                    if red_balls == 0:
                        last_reaction = True
                        player.can_move_flag = False
                        stop_timer = FPS // 2
                        remove_ghosts_timer = FPS // 4

        if red_balls <= 0 and not exiting:
            exiting = True

        if is_red:
            red_timer -= 1
            if red_timer <= 0:
                is_red = False

        if last_reaction:
            stop_timer -= 1
            if stop_timer <= 0:
                player.can_move_flag = True
                if not ghosts_removed:
                    ghosts.clear()
                    ghosts_removed = True

        if exiting and player.can_move_flag:
            if player.grid_x == EXIT_X and player.grid_y == EXIT_Y:
                break
            if player.can_move(0, -1):
                player.move(0, -1)
            elif player.can_move(1, 0):
                player.move(1, 0)
            else:
                break

        if not exiting:
            for g in ghosts[:]:
                g.update()
                if is_red:
                    dx = player.pix_x - g.pix_x
                    dy = player.pix_y - g.pix_y
                    if math.hypot(dx, dy) <= player.red_radius() + g.radius:
                        ghosts.remove(g)
                        score += 1
                        hud_visible = True
                        hud_start_time = pygame.time.get_ticks()

        screen.fill(COLOR_BG)
        for y, row in enumerate(MAZE):
            for x, ch in enumerate(row):
                if ch == '#':
                    pygame.draw.rect(screen, COLOR_WALL,
                                     (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        for g in ghosts:
            g.draw(screen, g.color)
        draw_color = COLOR_PLAYER_RED if is_red else  COLOR_PLAYER_DEFAULT
        player.draw(screen, draw_color, is_red)

        current_time = pygame.time.get_ticks()
        if hud_visible and current_time - hud_start_time < HUD_DISPLAY_DURATION:
            popup_w, popup_h = 180, 50
            popup_x = (COLS * TILE_SIZE - popup_w) // 2
            popup_y = (ROWS * TILE_SIZE - popup_h) // 2
            popup_surf = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
            popup_surf.fill((0, 0, 0, 180))
            pygame.draw.rect(popup_surf, (255, 255, 255), popup_surf.get_rect(), 2)
            screen.blit(popup_surf, (popup_x, popup_y))
            text_score = font.render(f"Score: {score}", True, (255, 255, 255))
            text_react = font.render(f"Reactions: {red_balls}", True, (255, 255, 255))
            screen.blit(text_score, (popup_x + 10, popup_y + 8))
            screen.blit(text_react, (popup_x + 10, popup_y + 28))
        elif current_time - hud_start_time >= HUD_DISPLAY_DURATION:
            hud_visible = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    return score
