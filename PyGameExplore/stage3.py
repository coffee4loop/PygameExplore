import pygame
import sys
import math

# --- Constants ---
FPS = 60
WINDOW_WIDTH = 560
WINDOW_HEIGHT = 480
GRID_SIZE = 61
DISPLAYED_GRID_SIZE = 3
CELL_SIZE_X = WINDOW_WIDTH // DISPLAYED_GRID_SIZE
CELL_SIZE_Y = WINDOW_HEIGHT // DISPLAYED_GRID_SIZE
# Define the target initial radius to fit the cell
INITIAL_PLAYER_RADIUS_FIT = min(CELL_SIZE_X, CELL_SIZE_Y) // 2 - 2  # e.g., 160 // 2 - 2 = 78
PLAYER_INIT_GRID_POS = (GRID_SIZE // 2, GRID_SIZE // 2)
INITIAL_DARKEN_ALPHA_BRIGHTEN = 20
INITIAL_PLAYER_COLOR = (255, 255, 0)
FINAL_PLAYER_COLOR = (255, 255, 255)
WHITE_BACKGROUND_THRESHOLD = 0.95
SIZE_CHANGE_SPEED = 1  # Integer clicks now
MOVEMENT_SPEED = 10

# Define Min/Max player radius clearly
MIN_PLAYER_RADIUS = 1
# Make max_player_radius large enough to fill screen diagonally approx.
MAX_PLAYER_RADIUS = int(math.sqrt(WINDOW_WIDTH**2 + WINDOW_HEIGHT**2) / 2) + 5

# Define click limits
UP_CLICKS_TO_MAX = 9
DOWN_CLICKS_TO_MIN = 9

# --- Colors ---
BLANK_COLOR = (50, 50, 50)
INITIAL_BACKGROUND_COLOR = (0, 0, 0)  # Start from black

# Define corner colors
COLOR_UP_CENTER = (128, 128, 128)
COLOR_LEFT_CENTER = (0, 0, 139)
COLOR_RIGHT_CENTER = (255, 0, 0)
COLOR_DOWN_CENTER = (101, 67, 33)

COLOR_UP_MAX = (173, 216, 230)
COLOR_LEFT_MAX = (224, 255, 255)
COLOR_RIGHT_MAX = (255, 182, 193)
COLOR_DOWN_MAX = (255, 223, 0)


def get_triangle_type(row, col):
    """Identifies the color quadrant for a grid cell."""
    center = GRID_SIZE // 2
    if row < center and abs(row - center) > abs(col - center):
        return "cloudy"
    elif row > center and abs(row - center) > abs(col - center):
        return "earthy"
    elif col < center and abs(col - center) >= abs(row - center):
        return "watery"
    elif col > center and abs(col - center) >= abs(row - center):
        return "fiery"
    else:
        return "blank"


def color_blend(color1, color2, factor):
    """Blend two colors based on a factor (0 to 1)."""
    # Ensure factor is clamped between 0 and 1
    factor = max(0.0, min(factor, 1.0))
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)


def get_pixelated_color(row, col):
    """Determines the color of a grid cell based on its position."""
    center = GRID_SIZE // 2
    # Avoid division by zero if GRID_SIZE is 1 or less (edge case)
    if center == 0:
        return BLANK_COLOR
    max_distance = float(center)  # Use float for normalization

    # Calculate raw distances to the four "corners" (center lines)
    dist_up = max(0, center - row)
    dist_down = max(0, row - center)
    dist_left = max(0, center - col)
    dist_right = max(0, col - center)

    # Handle the exact center case
    if dist_up == 0 and dist_down == 0 and dist_left == 0 and dist_right == 0:
        # Return the average of the center colors
        return (
            (COLOR_UP_CENTER[0] + COLOR_DOWN_CENTER[0] + COLOR_LEFT_CENTER[0] + COLOR_RIGHT_CENTER[0]) // 4,
            (COLOR_UP_CENTER[1] + COLOR_DOWN_CENTER[1] + COLOR_LEFT_CENTER[1] + COLOR_RIGHT_CENTER[1]) // 4,
            (COLOR_UP_CENTER[2] + COLOR_DOWN_CENTER[2] + COLOR_LEFT_CENTER[2] + COLOR_RIGHT_CENTER[2]) // 4,
        )

    # Normalize distances
    # Sum of normalized distances can be greater than 1 if closer to multiple centers,
    # but we use individual normalization relative to max_distance for blending.
    norm_up = dist_up / max_distance if max_distance > 0 else 0
    norm_down = dist_down / max_distance if max_distance > 0 else 0
    norm_left = dist_left / max_distance if max_distance > 0 else 0
    norm_right = dist_right / max_distance if max_distance > 0 else 0

    # Blend from center color towards max color based on normalized distance
    color_up = color_blend(COLOR_UP_CENTER, COLOR_UP_MAX, norm_up)
    color_down = color_blend(COLOR_DOWN_CENTER, COLOR_DOWN_MAX, norm_down)
    color_left = color_blend(COLOR_LEFT_CENTER, COLOR_LEFT_MAX, norm_left)
    color_right = color_blend(COLOR_RIGHT_CENTER, COLOR_RIGHT_MAX, norm_right)

    # Combine the colors. Weight by the *normalized* distances.
    # This approach assumes a weighted average based on how close a pixel is to each center line direction.
    # If a pixel is on a center line, its distance to that center line is 0 for that direction,
    # and its normalized distance is 0, resulting in no contribution from that direction's max color.
    # The blend towards center colors happens implicitly as normalized distances decrease.

    # Let's try a weighted average of the blended colors themselves, weighted by their normalized distances.
    # Need to ensure the weights sum to something non-zero if any blending is happening.
    # If total normalized distance is 0, we are at the center (handled above).
    # If total normalized distance is non-zero, use it for division.
    total_norm_dist = norm_up + norm_down + norm_left + norm_right

    if total_norm_dist == 0:  # Should be covered by the center check, but defensive
        return (
            (COLOR_UP_CENTER[0] + COLOR_DOWN_CENTER[0] + COLOR_LEFT_CENTER[0] + COLOR_RIGHT_CENTER[0]) // 4,
            (COLOR_UP_CENTER[1] + COLOR_DOWN_CENTER[1] + COLOR_LEFT_CENTER[1] + COLOR_RIGHT_CENTER[1]) // 4,
            (COLOR_UP_CENTER[2] + COLOR_DOWN_CENTER[2] + COLOR_LEFT_CENTER[2] + COLOR_RIGHT_CENTER[2]) // 4,
        )

    # Calculate weighted average of the blended colors
    final_color = (
        int((color_up[0] * norm_up + color_down[0] * norm_down + color_left[0] * norm_left + color_right[0] * norm_right) / total_norm_dist),
        int((color_up[1] * norm_up + color_down[1] * norm_down + color_left[1] * norm_left + color_right[1] * norm_right) / total_norm_dist),
        int((color_up[2] * norm_up + color_down[2] * norm_down + color_left[2] * norm_left + color_right[2] * norm_right) / total_norm_dist)
    )

    # Clamp color values to 0-255 just in case
    final_color = tuple(max(0, min(c, 255)) for c in final_color)

    return final_color


def display_player_coordinates(screen, player_grid_pos, font):
    """Display the player's coordinates on the screen."""
    x = player_grid_pos[1] - GRID_SIZE // 2
    y = player_grid_pos[0] - GRID_SIZE // 2
    coord_text = font.render(f"Coords: ({x}, {y})", True, (255, 255, 255))  # Shorter label
    coord_rect = coord_text.get_rect(topleft=(10, 50))  # Adjust position as needed
    screen.blit(coord_text, coord_rect)


class Player:
    def __init__(self, initial_grid_pos):
        self.grid_pos = list(initial_grid_pos)
        self.radius = INITIAL_PLAYER_RADIUS_FIT
        self.last_move_time = 0  # Track the last move time
        self.move_cooldown = 250  # Cooldown in milliseconds (1000 ms = 1 second)
        self.can_increase_size = True  # Flags to prevent holding key down causing instant max/min
        self.can_decrease_size = True

    def reset_size_change_flags(self):
        """Resets the flags that prevent continuous size change on key hold."""
        self.can_increase_size = True
        self.can_decrease_size = True

    def calculate_player_radius(self, size_change_clicks):
        """ Calculates player radius based on clicks.
            clicks = 0 -> INITIAL_PLAYER_RADIUS_FIT
            clicks = UP_CLICKS_TO_MAX -> MAX_PLAYER_RADIUS
            clicks = -DOWN_CLICKS_TO_MIN -> MIN_PLAYER_RADIUS
        """
        if size_change_clicks < 0:
            # Interpolate between MIN_PLAYER_RADIUS (at -DOWN_CLICKS_TO_MIN) and INITIAL_PLAYER_RADIUS_FIT (at 0)
            # Factor goes from 0 at -DOWN_CLICKS_TO_MIN to 1 at 0
            shrink_factor = (size_change_clicks + DOWN_CLICKS_TO_MIN) / DOWN_CLICKS_TO_MIN
            # Ensure factor is clamped [0, 1] due to potential float inaccuracies
            shrink_factor = max(0.0, min(shrink_factor, 1.0))
            self.radius = MIN_PLAYER_RADIUS + shrink_factor * (INITIAL_PLAYER_RADIUS_FIT - MIN_PLAYER_RADIUS)
        elif size_change_clicks > 0:
            # Interpolate between INITIAL_PLAYER_RADIUS_FIT (at 0) and MAX_PLAYER_RADIUS (at UP_CLICKS_TO_MAX)
            # Factor goes from 0+epsilon at 0 to 1 at UP_CLICKS_TO_MAX
            grow_factor = size_change_clicks / UP_CLICKS_TO_MAX
            # Ensure factor is clamped [0, 1]
            grow_factor = max(0.0, min(grow_factor, 1.0))
            self.radius = INITIAL_PLAYER_RADIUS_FIT + grow_factor * (MAX_PLAYER_RADIUS - INITIAL_PLAYER_RADIUS_FIT)
        else:  # size_change_clicks == 0
            self.radius = INITIAL_PLAYER_RADIUS_FIT

        # Ensure radius is within the absolute min/max bounds as a final safeguard
        self.radius = max(MIN_PLAYER_RADIUS, min(self.radius, MAX_PLAYER_RADIUS))

        return self.radius

    def move_player(self, keys_held, player_grid_pos):
        """Handles player movement based on keys held, respecting a cooldown."""
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if current_time - self.last_move_time < self.move_cooldown:
            return player_grid_pos  # Skip movement if cooldown hasn't passed

        new_grid_pos = list(player_grid_pos)  # Create a copy
        moved = False  # Flag to check if a move occurred
        # Use max/min to keep player within GRID_SIZE bounds
        if keys_held[pygame.K_w]:
            new_grid_pos[0] = max(0, new_grid_pos[0] - 1)  # Move 1 grid unit
            moved = True
        if keys_held[pygame.K_s]:
            new_grid_pos[0] = min(GRID_SIZE - 1, new_grid_pos[0] + 1)
            moved = True
        if keys_held[pygame.K_a]:
            new_grid_pos[1] = max(0, new_grid_pos[1] - 1)
            moved = True
        if keys_held[pygame.K_d]:
            new_grid_pos[1] = min(GRID_SIZE - 1, new_grid_pos[1] + 1)
            moved = True

        # Update the last move time only if the position actually changed
        if moved:
            self.last_move_time = current_time

        return new_grid_pos

    def draw_player(self, screen, player_grid_pos, start_row, start_col, size_change_clicks, final_color):
        """Draws the player on the screen."""
        # Player color depends on the zoom direction (size_change_clicks) and the final_color
        if size_change_clicks > 0:
            # Blend from INITIAL yellow towards FINAL_COLOR as clicks -> UP_CLICKS_TO_MAX
            brightness_factor = size_change_clicks / UP_CLICKS_TO_MAX
            brightness_factor = max(0.0, min(brightness_factor, 1.0))  # Clamp factor
            current_player_color = color_blend(INITIAL_PLAYER_COLOR, final_color, brightness_factor)
        elif size_change_clicks < 0:
            # Optional: Could blend towards a different color when shrinking, e.g., darker yellow
            # For now, keep initial yellow when shrinking or at 0
            current_player_color = INITIAL_PLAYER_COLOR
        else:  # clicks == 0
            current_player_color = INITIAL_PLAYER_COLOR

        # Calculate drawing position based on the displayed 3x3 grid
        player_draw_x = (player_grid_pos[1] - start_col + 0.5) * CELL_SIZE_X
        player_draw_y = (player_grid_pos[0] - start_row + 0.5) * CELL_SIZE_Y

        # Use the calculated self.radius (ensure it's an int for drawing)
        pygame.draw.circle(screen, current_player_color, (int(player_draw_x), int(player_draw_y)), int(self.radius))


class Background:
    def __init__(self):
        # current_background_color is determined frame-by-frame in draw_grid
        pass

    def draw_grid(self, screen, player_grid_pos, size_change_clicks):
        """Draws the background grid or solid color based on zoom level."""
        # --- Determine Background Color ---
        max_size_white = False
        if size_change_clicks >= UP_CLICKS_TO_MAX:
            current_background_color = (255, 255, 255)  # Max up -> White
            max_size_white = True
        elif size_change_clicks <= -DOWN_CLICKS_TO_MIN:
            current_background_color = (0, 0, 0)  # Max down -> Black
        else:
            # Interpolate background color based on clicks relative to INITIAL_BACKGROUND_COLOR
            if size_change_clicks > 0:
                # Blend from INITIAL (black) towards WHITE
                factor = size_change_clicks / UP_CLICKS_TO_MAX
                current_background_color = color_blend(INITIAL_BACKGROUND_COLOR, (255, 255, 255), factor)
            else:  # size_change_clicks < 0 (but > -DOWN_CLICKS_TO_MIN)
                # Blend from INITIAL (black) towards BLACK (stays black unless initial was different)
                # This part effectively keeps it black or dark grey when shrinking.
                factor = abs(size_change_clicks) / DOWN_CLICKS_TO_MIN  # Factor goes from 0 at 0 to 1 at -DOWN_CLICKS_TO_MIN
                current_background_color = color_blend(INITIAL_BACKGROUND_COLOR, (0, 0, 0), factor)  # Blending black with black
                # A more noticeable darkening might blend towards a very dark grey or use an alpha overlay

        screen.fill(current_background_color)

        # --- Calculate Displayed Grid ---
        # Center the 3x3 grid view around the player, clamping at world edges
        start_row = max(
            0, min(GRID_SIZE - DISPLAYED_GRID_SIZE, player_grid_pos[0] - DISPLAYED_GRID_SIZE // 2)
        )
        start_col = max(
            0, min(GRID_SIZE - DISPLAYED_GRID_SIZE, player_grid_pos[1] - DISPLAYED_GRID_SIZE // 2)
        )

        # --- Draw Grid Cells (only if background isn't fully white or black) ---
        if not (size_change_clicks <= -DOWN_CLICKS_TO_MIN or size_change_clicks >= UP_CLICKS_TO_MAX):
            for row_offset in range(DISPLAYED_GRID_SIZE):
                for col_offset in range(DISPLAYED_GRID_SIZE):
                    grid_row = start_row + row_offset
                    grid_col = start_col + col_offset

                    # Check bounds just in case (shouldn't be necessary with calculation above)
                    if 0 <= grid_row < GRID_SIZE and 0 <= grid_col < GRID_SIZE:
                        # Use the pre-calculated average for the exact center
                        if grid_row == GRID_SIZE // 2 and grid_col == GRID_SIZE // 2:
                            color = (
                                (COLOR_UP_CENTER[0] + COLOR_DOWN_CENTER[0] + COLOR_LEFT_CENTER[0] + COLOR_RIGHT_CENTER[0]) // 4,
                                (COLOR_UP_CENTER[1] + COLOR_DOWN_CENTER[1] + COLOR_LEFT_CENTER[1] + COLOR_RIGHT_CENTER[1]) // 4,
                                (COLOR_UP_CENTER[2] + COLOR_DOWN_CENTER[2] + COLOR_LEFT_CENTER[2] + COLOR_RIGHT_CENTER[2]) // 4,
                            )
                        else:
                            color = get_pixelated_color(grid_row, grid_col)

                        draw_x = col_offset * CELL_SIZE_X
                        draw_y = row_offset * CELL_SIZE_Y
                        pygame.draw.rect(screen, color, (draw_x, draw_y, CELL_SIZE_X, CELL_SIZE_Y))

        return start_row, start_col  # Return calculated values


# Modified function signature
def run_stage_3(final_color, score):
    """
    Displays a 3x3 grid view of a larger world.
    Player moves with WASD.
    Player size changes with UP/DOWN keys (single press).
    Initial size fits grid cell. 9 clicks UP = Max Size/White. 9 clicks DOWN = Min Size/Black.
    Receives the final player color from the previous stage.
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Stage 3: Exploration")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Font for timer, coords

    # --- Display Instructions ---
    instruction_font = pygame.font.Font(None, 30)
    line_height = 35
    y_offset = WINDOW_HEIGHT // 4 - 50  # Adjust starting position
    instructions = [
        f"You have {score} second(s) to explore.",  # Use score as time directly
        "Find a place and state you are comfortable with.",
        "",
        "Explore as far as u can",
        " W = Up, A = Left, S = Down, D = Right",
        "Or Explore yourself",
        " UP Key: Zoom In",
        " DOWN Key: Zoom Out",
        "",
        "Press any key to begin..."
    ]

    screen.fill((0, 0, 0))  # Black background for instructions
    for i, line in enumerate(instructions):
        text = instruction_font.render(line, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + i * line_height))
        screen.blit(text, text_rect)
    pygame.display.flip()

    start_wait_time = pygame.time.get_ticks()  # Record the time when the instructions are displayed
    waiting_for_input = True
    while waiting_for_input:
        current_time_wait = pygame.time.get_ticks()  # Get the current time
        # Check if 10 seconds have passed AND we are NOT already running the game loop
        # This prevents skipping the instructions if a key is pressed immediately.
        if current_time_wait - start_wait_time >= 10000: # Changed from 5000 to 10000 for 10s wait
            waiting_for_input = False  # Exit the loop after 10 seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the player closes the window
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # If the player presses any key
                waiting_for_input = False

        clock.tick(FPS)  # Keep pygame responsive

    player = Player(PLAYER_INIT_GRID_POS)
    background = Background()

    size_change_clicks = 0  # Start at 0 clicks, which corresponds to INITIAL_PLAYER_RADIUS_FIT

    # Key state tracking for movement
    keys_held = {
        pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False,
        # UP/DOWN not needed here as they are handled by single KEYDOWN events
    }
    # Debounce for UP/DOWN keys
    last_size_change_time = 0
    size_change_interval = 100  # milliseconds between size changes

    # Timer setup
    if isinstance(score, (int, float)) and score > 0:
        game_duration_seconds = score  # Use score directly as duration
    else:
        print(f"Warning: Invalid score ({score}) for timer. Defaulting to 60 seconds.")
        game_duration_seconds = 60  # Default duration if score is invalid

    start_time = pygame.time.get_ticks()  # Start the main game timer now
    time_left = game_duration_seconds
    running = True
    player_grid_pos = list(PLAYER_INIT_GRID_POS)  # Use a working copy for position

    while running:
        current_time_ticks = pygame.time.get_ticks()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in keys_held:  # Handle WASD down
                    keys_held[event.key] = True
                elif event.key == pygame.K_UP:
                    # Check debounce timer and bounds
                    if current_time_ticks - last_size_change_time > size_change_interval:
                        if size_change_clicks < UP_CLICKS_TO_MAX:
                            size_change_clicks += 1
                            last_size_change_time = current_time_ticks
                elif event.key == pygame.K_DOWN:
                    # Check debounce timer and bounds
                    if current_time_ticks - last_size_change_time > size_change_interval:
                        if size_change_clicks > -DOWN_CLICKS_TO_MIN:
                            size_change_clicks -= 1
                            last_size_change_time = current_time_ticks
            elif event.type == pygame.KEYUP:
                if event.key in keys_held:  # Handle WASD up
                    keys_held[event.key] = False
                # No reset needed for UP/DOWN flags as they are single press driven

        # --- Game Logic ---
        # Move player based on held keys
        player_grid_pos = player.move_player(keys_held, player_grid_pos)

        # Calculate player radius based on clicks
        # This now uses the new dual-interpolation logic
        player_radius = player.calculate_player_radius(size_change_clicks)

        # Update timer
        time_elapsed_seconds = (current_time_ticks - start_time) // 1000
        time_left = max(0, game_duration_seconds - time_elapsed_seconds)

        # Check end conditions
        if time_left == 0:
            running = False
        # Optional: Stop if player reaches max size? Your original code had this.
        # if size_change_clicks >= UP_CLICKS_TO_MAX:
        #     running = False

        # --- Drawing ---
        start_row, start_col = background.draw_grid(screen, player_grid_pos, size_change_clicks)

        # Apply screen brightness/darkness overlay (AFTER grid/background)
        # Only apply overlay if not at the fully white or black screen states
        if not (size_change_clicks <= -DOWN_CLICKS_TO_MIN or size_change_clicks >= UP_CLICKS_TO_MAX):
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))  # Use black overlay for both effects

            if size_change_clicks > 0:
                # Getting brighter: decrease overlay alpha
                brightness_factor = size_change_clicks / UP_CLICKS_TO_MAX
                alpha_value = int(max(0, INITIAL_DARKEN_ALPHA_BRIGHTEN - brightness_factor * INITIAL_DARKEN_ALPHA_BRIGHTEN))
                overlay.set_alpha(alpha_value)
                screen.blit(overlay, (0, 0))
            elif size_change_clicks < 0:
                # Getting darker: increase overlay alpha
                darkness_factor = abs(size_change_clicks) / DOWN_CLICKS_TO_MIN
                alpha_value = int(darkness_factor * 200)  # Scale alpha more strongly for darkness
                alpha_value = min(alpha_value, 255)  # Clamp to 255
                overlay.set_alpha(alpha_value)
                screen.blit(overlay, (0, 0))

        # Draw the player (on top of background - if not a solid color screen)
        # Player is always drawn unless the game has ended (running = False)
        player.draw_player(screen, player_grid_pos, start_row, start_col, size_change_clicks, final_color)

        # --- UI Elements ---
        # Display Timer
        timer_text = font.render(f"Time: {time_left}", True, (255, 255, 255))
        timer_rect = timer_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))  # Top right
        screen.blit(timer_text, timer_rect)

        # Display Coordinates
        #display_player_coordinates(screen, player_grid_pos, font)  # Top left

        # Display Size Clicks (for debugging/info)
        # clicks_text = font.render(f"Zoom: {size_change_clicks}", True, (255, 255, 255))
        # clicks_rect = clicks_text.get_rect(topleft=(10, 80))
        # screen.blit(clicks_text, clicks_rect)

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(FPS)
        # --- End of Game Loop ---

    # --- Game End Sequence ---
    final_player_pos = player_grid_pos  # Store the final position when loop ends
    final_player_radius = player.radius  # Store the final radius
    final_clicks = size_change_clicks  # Store the final click state

    # Display the final affinities
    screen.fill((0, 0, 0))  # Clear screen to black
    x = final_player_pos[1] - GRID_SIZE // 2
    y = -(final_player_pos[0] - GRID_SIZE // 2)  # Invert Y for typical Cartesian

    # --- Affinity Calculation Logic ---
    # Determines the major and minor elemental affinities based on the final player position (x, y).
    # (0,0) is the center of the grid.
    # +x direction is Fire, -x is Water.
    # +y direction is Air, -y is Earth.
    #
    # Logic:
    # 1. If at the exact center (0,0), major affinity is "Balance", no minor affinity.
    # 2. If exactly on an axis (one coordinate is zero, the other is non-zero):
    #    - Major affinity is the element corresponding to the non-zero axis.
    #    - Minor affinity is the *opposite* element on the *same* axis, with the *same* value as the major affinity.
    # 3. If on a diagonal or in a quadrant (both x and y non-zero):
    #    - Major affinity is the element corresponding to the axis with the larger absolute value.
    #    - Minor affinity is the element corresponding to the axis with the smaller absolute value.

    if x == 0 and y == 0:  # Case 1: Center
        affinity_major = "Balance"
        affinity_minor = "" # No minor affinity at the center
        major_val, minor_val = 0, 0
    elif (x != 0 and y == 0) or (x == 0 and y != 0): # Case 2: Exactly on an axis
        if x != 0: # On the horizontal axis (y is 0)
            affinity_major = "Fire" if x > 0 else "Water"
            major_val = abs(x)
            # Minor is the opposite on the same axis with the same value
            affinity_minor = "Water" if x > 0 else "Fire"
            minor_val = abs(x) # Minor value is the same as major value
        else: # On the vertical axis (x is 0, y != 0)
            affinity_major = "Air" if y > 0 else "Earth"
            major_val = abs(y)
            # Minor is the opposite on the same axis with the same value
            affinity_minor = "Earth" if y > 0 else "Air"
            minor_val = abs(y) # Minor value is the same as major value
    else: # Case 3: On a diagonal or in a quadrant (both x and y non-zero)
        if abs(x) > abs(y):
            affinity_major = "Fire" if x > 0 else "Water"
            affinity_minor = "Air" if y > 0 else "Earth"  # Minor based on the less dominant axis
            major_val, minor_val = abs(x), abs(y)
        elif abs(y) > abs(x):
            affinity_major = "Air" if y > 0 else "Earth"
            affinity_minor = "Fire" if x > 0 else "Water"  # Minor based on the less dominant axis
            major_val, minor_val = abs(y), abs(x)
        else: # abs(x) == abs(y) and x != 0 (Diagonal)
            # Treat diagonals as having equal influence, listing both as major/minor
            # For simplicity, let's pick one as major based on sign, other as minor
            affinity_major = "Fire" if x > 0 else "Water"
            affinity_minor = "Air" if y > 0 else "Earth"
            major_val, minor_val = abs(x), abs(y)

    # Calculate light or dark affinity based on zoom level
    if final_clicks > 0:  # Positive zoom level (zooming in towards light/white)
        affinity_type = "Light"
        # Scale affinity value based on clicks, 0 clicks could be base value
        affinity_value = abs(final_clicks) * 3  # Scales from 3 to 27
    elif final_clicks < 0:  # Negative zoom level (zooming out towards dark/black)
        affinity_type = "Dark"
        affinity_value = abs(final_clicks) * 3  # Scales from 3 to 27
    else:  # final_clicks == 0 (Neutral zoom)
        affinity_type = "Light" # Default to Light affinity if neutral zoom
        affinity_value = 0  # Or a small base value

    # Prepare text lines
    results_font = pygame.font.Font(None, 34)
    results_lines = []
    results_lines.append("Exploration Complete")
    results_lines.append("")
    # Adjust display based on whether a minor affinity exists
    if affinity_minor:
        results_lines.append(f"Affinities: {affinity_major} ({major_val}), {affinity_minor} ({minor_val})")
    elif affinity_major: # Display major even if no minor (e.g., at center)
         results_lines.append(f"Affinity: {affinity_major}")
    else: # Should not happen if not at center, but for completeness
         results_lines.append("No Elemental Affinity")


    # Ensure the light/dark affinity value is +3 as requested by a previous user instruction
    # Note: This overrides the calculated light/dark affinity value from zoom clicks.
    # If you want the light/dark affinity to be based on zoom, remove this line.
    light_dark_display_value = affinity_value + 3 # This line was already here, keeping it.


    results_lines.append(f"{affinity_type} Affinity: {light_dark_display_value}") # Use the potentially modified value
    results_lines.append("")
    results_lines.append("Press any key to sleep.")

    # Draw results lines centered
    line_spacing = 35  # Consistent line spacing
    total_text_height = len(results_lines) * line_spacing
    results_y_offset = (WINDOW_HEIGHT - total_text_height) // 2

    for i, line in enumerate(results_lines):
        text = results_font.render(line, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, results_y_offset + i * line_spacing))
        screen.blit(text, text_rect)

    pygame.display.flip()

    # --- Wait for Quit with Minimum Display Time ---
    display_start_time = pygame.time.get_ticks() # Record the time the results screen was displayed
    minimum_display_duration = 2000 # 2 seconds in milliseconds

    waiting_for_quit = True
    while waiting_for_quit:
        current_time_quit = pygame.time.get_ticks() # Get current time in the quit loop

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Allow quitting immediately if the window is closed
                waiting_for_quit = False
            if event.type == pygame.KEYDOWN:
                # Only allow exiting on key press AFTER the minimum display duration has passed
                if current_time_quit - display_start_time >= minimum_display_duration:
                     waiting_for_quit = False

        # If the minimum display duration has passed, and no quit event occurred,
        # the loop will continue until a valid quit event (window close or key press) occurs.
        # If the duration hasn't passed, key presses are ignored.

        clock.tick(FPS)  # Keep responsive

    pygame.quit()
    # Return relevant final values
    return final_player_pos, final_clicks, affinity_type, affinity_value


# --- Helper Function (Not used in Stage 3 directly) ---
def draw_text(screen, text, pos, font, color=(255, 220, 0)):
    """Draws text on the screen"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=pos)
    screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    # Example of how to run Stage 3 independently (for testing)
    # Pass a dummy final_color and a test score (time)
    # final_color, score
    final_data = run_stage_3((100, 150, 200), 10)  # Example: pass a shade of blue and 10 seconds
    print(f"Stage 3 ended.")
    if final_data:
        f_pos, f_cli, aff_type, aff_value = final_data
        print(f" Final Player Position (Grid): {f_pos}")
        # The final radius is calculated internally and not returned directly anymore,
        # but could be added back if needed for a subsequent stage.
        # print(f" Final Player Radius: {f_rad:.2f}")
        print(f" Final Zoom Clicks: {f_cli}")
        print(f" Final Affinity Type: {aff_type}")
        print(f" Final Affinity Value: {aff_value}")

    sys.exit()
