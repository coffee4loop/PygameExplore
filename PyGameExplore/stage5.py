import pygame
import sys
import math
import os

def run_stage_5(blue, red, brown, player_color, player_size, clue, affinities, created_name):
    """
    Displays initial stats/instructions on a full screen with a LARGE animated Player 2 sprite,
    requiring a key press to start the game.
    Then, it runs a dual-player movement game with animated elves. Player 1 is grid-based
    and moves automatically to a specific spot then follows Player 2, maintaining a minimum distance.
    Player 2 is controlled by WASD with continuous smooth, non-grid movement (at NORMAL size),
    but is locked until Player 1 completes its initial sequence.
    Sprite selection and animation for Player 2 is determined by the provided affinities.
    Handles cases where specific affinity sprites might not exist.
    Adds a large, centered notification with a white background and black text when Player 2 attempts to move beyond screen edges.
    """
    # Constants for the game
    tile_width = 50
    tile_height = 50
    grid_cols = 20
    grid_rows = 10
    window_width = tile_width * grid_cols
    window_height = tile_height * grid_rows

    # Initialize pygame
    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Stage 5: Dual Player Grid Movement")
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    # --- Notification Font ---
    font_notification = pygame.font.Font(None, 48) # Size kept at 48 as requested previously

    clock = pygame.time.Clock()

    # --- Load Player 2 Assets (Base Frames First) ---
    player2_frames = [] # Initialize list for original unscaled frames
    player2_sprite_name = "unknown"
    player2_animation_speed = 10

    # --- Scaling Factors ---
    INFO_SCREEN_SCALE_FACTOR = 10.0 # Large scale for info screen
    GAME_SCREEN_SCALE_FACTOR = 1.5  # Normal scale for game

    # --- Variables for Info Screen Sprite ---
    info_player2_scaled = []
    info_p2_scaled_width = 0
    info_p2_scaled_height = 0

    # --- Variables for Game Screen Sprite ---
    game_player2_scaled = []
    game_p2_scaled_width = 0
    game_p2_scaled_height = 0

    try:
        # Determine Player 2 sprite filename based on affinities
        affinity_type = "light"
        if 'light_dark' in affinities and affinities['light_dark']:
            affinity_type = affinities['light_dark']['type'].lower()
        ld = affinities.get('light_dark', {})
        ld_type = ld.get('type', '').lower()
        ld_value = ld.get('value', 0)
        if ld_type not in ('light', 'dark'):
            ld_type = 'light'; ld_value = 3
        affinities['light_dark'] = {'type': ld_type.capitalize(), 'value': ld_value}
        affinity_type = ld_type
        major_affinity = affinities['major']['type'].lower() if affinities['major']['type'] else "gold"
        if not affinities['major']['type']: major_affinity = "gold"

        intended_sprite_name = ""
        # Determine the intended sprite name based on affinities
        if affinity_type == "dark":
            if major_affinity == "air": intended_sprite_name = "darksky.png"
            elif major_affinity == "earth": intended_sprite_name = "darkgold.png"
            elif major_affinity == "water": intended_sprite_name = "darkwater.png"
            elif major_affinity == "fire": intended_sprite_name = "darkfire.png"
            elif major_affinity == "balance": intended_sprite_name = "darkgold.png"
            else: intended_sprite_name = f"{affinity_type}{major_affinity}.png" # Fallback
        else: # light
            if major_affinity == "air": intended_sprite_name = "lightsky.png"
            elif major_affinity == "earth": intended_sprite_name = "lightgold.png"
            elif major_affinity == "water": intended_sprite_name = "lightwater.png"
            elif major_affinity == "fire": intended_sprite_name = "lightfire.png"
            elif major_affinity == "gold": intended_sprite_name = "lightgold.png"
            elif major_affinity == "balance": intended_sprite_name = "lightgold.png"
            else: intended_sprite_name = f"{affinity_type}{major_affinity}.png" # Fallback

        player2_sprite_name = intended_sprite_name


        # Load the base (full) image, handling errors and defaults
        try:
            player2_full_img = pygame.image.load(player2_sprite_name).convert_alpha()
        except FileNotFoundError:
            print(f"Error loading sprite: {player2_sprite_name}. File not found. Defaulting to lightgold.")
            try:
                player2_full_img = pygame.image.load("lightgold.png").convert_alpha()
                player2_sprite_name = "lightgold.png"
            except pygame.error as e:
                print(f"Failed to load default sprite lightgold.png: {e}"); pygame.quit(); sys.exit()
        except pygame.error as e:
            print(f"Failed to load sprite {player2_sprite_name} due to pygame error: {e}")
            try:
                player2_full_img = pygame.image.load("lightgold.png").convert_alpha()
                player2_sprite_name = "lightgold.png"
            except pygame.error as e_default:
                print(f"Failed to load default sprite lightgold.png after initial error: {e_default}"); pygame.quit(); sys.exit()

        # Split into original, unscaled frames
        p2_width = player2_full_img.get_width() // 3
        p2_height = player2_full_img.get_height()
        player2_frames = [
            player2_full_img.subsurface(0, 0, p2_width, p2_height),
            player2_full_img.subsurface(p2_width, 0, p2_width, p2_height),
            player2_full_img.subsurface(p2_width * 2, 0, p2_width, p2_height)
        ]

        # --- Create Scaled Sprites for INFO Screen (Large) ---
        info_p2_scaled_width = int(tile_width * INFO_SCREEN_SCALE_FACTOR)
        info_p2_scaled_height = int(tile_height * INFO_SCREEN_SCALE_FACTOR)
        info_player2_scaled = [pygame.transform.scale(img, (info_p2_scaled_width, info_p2_scaled_height)) for img in player2_frames]

        # --- Create Scaled Sprites for GAME Screen (Normal) ---
        game_p2_scaled_width = int(tile_width * GAME_SCREEN_SCALE_FACTOR)
        game_p2_scaled_height = int(tile_height * GAME_SCREEN_SCALE_FACTOR)
        game_player2_scaled = [pygame.transform.scale(img, (game_p2_scaled_width, game_p2_scaled_height)) for img in player2_frames]


    except pygame.error as e:
        print(f"Failed during Player 2 asset preparation: {e}")
        # Allow continuing without P2 sprite if loading failed but pygame is ok
        info_player2_scaled = []
        game_player2_scaled = []


    # --- Display Initial Instructions/Stats Screen ---
    instruction_color = (255, 255, 255)
    instructions = [
        f" [press space to go to game]  [W,A,S,D to MOVE]                  [Name: {created_name}]",
        f"",
        f"Strength: {blue}",
        f"Agility: {blue}",
        f"HP: {brown}",
        f"Defense: {brown}",f"",
        f"Secret Shop Currency (Score): {clue}",
        f"Unallocated Stats: {red}",f"",f"",
        f"Major Affinity: {affinities['major']['type']} ({affinities['major']['value']})",
        f"Minor Affinity: {affinities['minor']['type']} ({affinities['minor']['value']})",
        ]

    light_dark_affinity = affinities.get('light_dark')
    if light_dark_affinity:
        instructions.append(f"Light/Dark Affinity: {light_dark_affinity['type']} ({light_dark_affinity['value']})")
        f"Instructions: Use 'W', 'A', 'S', 'D' keys to move",
    """instructions.extend([ # Add game instructions to the info screen
        f"",
        f"Player 2 Sprite: {player2_sprite_name}", "",
        "Player 1: Moves automatically, tries to stay 1 grid away from Player 2.",
        
        "Player 2 movement is locked until Player 1 is ready.",
        "Press any key to start the game."
    ])"""

    instruction_surfaces = [font_medium.render(line, True, instruction_color) for line in instructions]

    # Info screen Player 2 animation variables
    info_p2_animation_timer = 0
    info_p2_animation_frame = 0
    # Calculate position for LARGE Player 2 sprite on info screen
    info_p2_draw_x = window_width - info_p2_scaled_width - 30 # Padding from right
    info_p2_draw_y = window_height // 2 - info_p2_scaled_height // 2 # Centered vertically

    waiting_for_key = True
    while waiting_for_key:
        screen.fill((0, 0, 0))

        # Draw instruction text
        x_offset = 10
        y_offset = 10
        max_text_width = 0 # Keep track of text width to avoid overlap
        for surface in instruction_surfaces:
            rect = surface.get_rect(topleft=(x_offset, y_offset))
            screen.blit(surface, rect)
            y_offset += 30
            if rect.width > max_text_width:
                max_text_width = rect.width

        # Adjust info sprite position if text is too wide
        if info_player2_scaled: # Only adjust if sprite loaded
            if info_p2_draw_x < max_text_width + x_offset + 20: # Add some padding
                info_p2_draw_x = max(max_text_width + x_offset + 20, window_width - info_p2_scaled_width - 10) # Ensure it doesn't go off screen


        # Draw LARGE animated Player 2 sprite if successfully loaded
        if info_player2_scaled: # Check if list is not empty
            info_p2_animation_timer += 1
            if info_p2_animation_timer >= player2_animation_speed:
                info_p2_animation_timer = 0
                info_p2_animation_frame = (info_p2_animation_frame + 1) % len(info_player2_scaled)

            current_info_p2_image = info_player2_scaled[info_p2_animation_frame]
            # Ensure sprite doesn't go off right edge if text pushed it
            draw_x = min(info_p2_draw_x, window_width - info_p2_scaled_width)
            screen.blit(current_info_p2_image, (draw_x, info_p2_draw_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN: waiting_for_key = False; break
            if event.type == pygame.KEYUP: pass

        clock.tick(60)

    # --- Clear event queue before starting the main game loop ---
    pygame.event.clear()

    # --- Load Main Game Assets (Player 1) ---
    try:
        grass_img = pygame.image.load('grass.png').convert()
        sand_img = pygame.image.load('sand.png').convert()
        elf_down_img = pygame.image.load('elfdown.png').convert_alpha()
        elf_up_full = pygame.image.load('elfup.png').convert_alpha()
        elf_left_full = pygame.image.load('elfleft.png').convert_alpha()

        up_width = elf_up_full.get_width() // 2
        elf_up_frames = [ elf_up_full.subsurface(0, 0, up_width, elf_up_full.get_height()), elf_up_full.subsurface(up_width, 0, up_width, elf_up_full.get_height()) ]
        left_width = elf_left_full.get_width() // 2
        elf_left_frames = [ elf_left_full.subsurface(0, 0, left_width, elf_left_full.get_height()), elf_left_full.subsurface(left_width, 0, left_width, elf_left_full.get_height()) ]
        elf_right_frames = [pygame.transform.flip(img, True, False) for img in elf_left_frames]

        elf_down_scaled = pygame.transform.scale(elf_down_img, (tile_width, tile_height))
        elf_up_scaled = [pygame.transform.scale(img, (tile_width, tile_height)) for img in elf_up_frames]
        elf_left_scaled = [pygame.transform.scale(img, (tile_width, tile_height)) for img in elf_left_frames]
        elf_right_scaled = [pygame.transform.scale(img, (tile_width, tile_height)) for img in elf_right_frames]
        # Player 2 assets (game_player2_scaled) already prepared

    except pygame.error as e: print(f"Failed to load a required game image: {e}"); pygame.quit(); sys.exit()
    except FileNotFoundError as e: print(f"Failed to load a required game image file: {e}"); pygame.quit(); sys.exit()


    # --- Initialize Game State ---

    # Player 1 properties
    player1_grid_y = 4; player1_grid_x = 1
    player1_x = player1_grid_x * tile_width; player1_y = player1_grid_y * tile_height
    player1_moving = False; player1_move_direction = (0, 0)
    player1_animation_timer = 0; player1_animation_speed = 10
    player1_left_animation_frame = 0; player1_up_animation_frame = 0
    player1_current_image = elf_right_scaled[0] # Start facing right
    player1_target_x = 0; player1_target_y = 0
    player1_following = False; player1_follow_delay = 0
    player1_reached_destination = False

    # Player 2 properties (Using NORMAL game scale)
    player2_x = 11 * tile_width; player2_y = 4 * tile_height
    player2_vx = 0.0; player2_vy = 0.0
    player2_speed = 5.0
    player2_animation_timer = 0 # Reset timer for game loop animation
    # Use NORMAL scaled frame, handle failure case where list might be empty
    player2_current_image = game_player2_scaled[0] if game_player2_scaled else None
    player2_animation_frame = 0 # Reset frame for game loop animation
    player2_movement_unlocked = False

    # Grid pattern
    grid_pattern = [
        ['G','G','G','G','G','S','S','S','G','G','G','S','G','G','G','S','S','S','G','G'], # 20
        ['G','G','G','G','S','G','G','G','G','G','S','S','S','G','G','G','G','G','S','G'], # 20
        ['G','G','G','S','G','G','S','S','S','S','S','G','S','S','S','S','S','G','G','S'], # 20
        ['G','G','G','S','G','G','S','G','G','S','G','G','G','S','G','G','S','G','G','S'], # 20
        ['S','S','G','S','G','G','G','S','S','G','G','S','G','G','S','S','G','G','G','S'], # 20
        ['S','S','G','S','G','G','G','S','S','G','G','S','S','G','G','G','G','G','S','G'], # 20
        ['G','G','G','S','G','G','S','G','G','S','G','G','G','S','G','G','S','G','G','S'], # 20
        ['G','G','G','S','G','G','S','S','S','S','S','G','S','S','S','S','S','G','G','S'], # 20
        ['G','G','G','G','S','G','G','G','G','G','S','S','S','G','G','G','G','S','G','G'], # 20
        ['G','G','G','G','G','S','S','S','G','G','G','S','G','G','G','S','S','S','G','G']  # 20
    ]

    # Player 1 Initial Move setup
    player1_initial_target_grid_x = 8; player1_initial_target_grid_y = 4
    player1_target_grid_x = player1_initial_target_grid_x; player1_target_grid_y = player1_initial_target_grid_y
    player1_target_x = player1_target_grid_x * tile_width; player1_target_y = player1_target_grid_y * tile_height
    initial_dx = 0; initial_dy = 0
    if player1_grid_x < player1_target_grid_x: initial_dx = 1
    elif player1_grid_x > player1_target_grid_x: initial_dx = -1
    if player1_grid_y < player1_target_grid_y: initial_dy = 1
    elif player1_grid_y > player1_target_grid_y: initial_dy = -1
    player1_move_direction = (initial_dx, initial_dy)
    player1_moving = True
    player1_reached_destination = False

    # --- Notification Variables ---
    boundary_notification_text = "This content will be unlocked in a future update"
    boundary_notification_color = (0, 0, 0) # Changed to Black
    boundary_notification_bg_color = (255, 255, 255) # White background color
    boundary_notification_padding = 15 # Padding around text for background
    show_boundary_notification = False
    boundary_notification_start_time = 0
    boundary_notification_duration = 2000 # 2 seconds

    # Game loop variables
    running = True
    speech_bubble_timer = 0; show_speech_bubble = False; speech_bubble_duration = 2000
    keys_pressed = { pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False }

    # --- Main Game Loop ---
    while running:
        dt = clock.tick(60) / 1000.0 # Delta time (optional for physics)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if player2_movement_unlocked and event.key in keys_pressed: keys_pressed[event.key] = True
            if event.type == pygame.KEYUP:
                if player2_movement_unlocked and event.key in keys_pressed: keys_pressed[event.key] = False

        # --- Player 2 Update (Uses NORMAL game scale: game_p2_scaled_width/height) ---
        if player2_movement_unlocked:
            target_vx = 0.0; target_vy = 0.0
            if keys_pressed[pygame.K_a]: target_vx -= player2_speed
            if keys_pressed[pygame.K_d]: target_vx += player2_speed
            if keys_pressed[pygame.K_w]: target_vy -= player2_speed
            if keys_pressed[pygame.K_s]: target_vy += player2_speed

            # Normalize diagonal movement
            mag_sq = target_vx**2 + target_vy**2
            if mag_sq > player2_speed**2: # Avoid sqrt if possible
                mag = math.sqrt(mag_sq)
                target_vx = (target_vx / mag) * player2_speed
                target_vy = (target_vy / mag) * player2_speed

            player2_vx = target_vx; player2_vy = target_vy

            # Store position *before* clamping
            # Calculate the potential next position based on velocity
            potential_next_x = player2_x + player2_vx
            potential_next_y = player2_y + player2_vy


            # Update position (consider using dt for frame rate independence if needed)
            player2_x += player2_vx # * dt * speed_multiplier (if using dt)
            player2_y += player2_vy # * dt * speed_multiplier (if using dt)


            # Clamp Player 2 using NORMAL game dimensions
            player2_x = max(0.0, min(player2_x, window_width - game_p2_scaled_width))
            player2_y = max(0.0, min(player2_y, window_height - game_p2_scaled_height))

            # Check if clamping occurred (Player 2 tried to move past an edge)
            # Compare the clamped position to the calculated position *before* clamping
            if player2_x != potential_next_x or player2_y != potential_next_y:
                # Trigger the notification
                show_boundary_notification = True
                boundary_notification_start_time = pygame.time.get_ticks()


        else: # Player 2 movement locked
            player2_vx = 0.0; player2_vy = 0.0

        # Player 2 Animation Update (using NORMAL game scale: game_player2_scaled)
        if game_player2_scaled: # Only animate if sprite loaded
            player2_animation_timer += 1
            if player2_animation_timer >= player2_animation_speed:
                player2_animation_timer = 0
                player2_animation_frame = (player2_animation_frame + 1) % len(game_player2_scaled)
                player2_current_image = game_player2_scaled[player2_animation_frame]

        # --- Player 1 Update ---
        if player1_moving:
            move_speed = 3 # Pixels per frame
            move_dx = player1_move_direction[0]; move_dy = player1_move_direction[1]
            player1_x += move_dx * move_speed; player1_y += move_dy * move_speed

            # Player 1 Animation
            player1_animation_timer += 1
            if player1_animation_timer >= player1_animation_speed:
                player1_animation_timer = 0
                if move_dx == -1: player1_current_image = elf_left_scaled[player1_left_animation_frame % 2]; player1_left_animation_frame += 1
                elif move_dx == 1: player1_current_image = elf_right_scaled[player1_left_animation_frame % 2]; player1_left_animation_frame += 1 # Use same index logic
                elif move_dy == -1: player1_current_image = elf_up_scaled[player1_up_animation_frame % 2]; player1_up_animation_frame += 1
                elif move_dy == 1: player1_current_image = elf_down_scaled

            # Check arrival (more robust check for reaching/passing target)
            reached_x = (move_dx > 0 and player1_x >= player1_target_x) or \
                        (move_dx < 0 and player1_x <= player1_target_x) or \
                        (move_dx == 0)
            reached_y = (move_dy > 0 and player1_y >= player1_target_y) or \
                        (move_dy < 0 and player1_y <= player1_target_y) or \
                        (move_dy == 0)

            if reached_x and reached_y:
                player1_grid_x = player1_target_grid_x; player1_grid_y = player1_target_grid_y
                player1_x = player1_grid_x * tile_width; player1_y = player1_grid_y * tile_height # Snap to grid
                player1_moving = False
                player1_current_image = elf_down_scaled # Idle pose

                # Check if initial destination reached
                if not player1_reached_destination and player1_grid_x == player1_initial_target_grid_x and player1_grid_y == player1_initial_target_grid_y:
                    player1_reached_destination = True
                    show_speech_bubble = True
                    speech_bubble_timer = pygame.time.get_ticks()
                    player1_current_image = elf_down_scaled # Ensure idle pose after reaching


        # Player 1 Following Logic (Uses NORMAL game scale for P2 center: game_p2_scaled_width/height)
        # This block only calculates and initiates the *next* move if P1 is following, not moving, and off cooldown.
        if player1_following and not player1_moving and player1_follow_delay <= 0:
            # Determine Player 2's grid cell using NORMAL game dimensions
            player2_center_x = player2_x + game_p2_scaled_width / 2
            player2_center_y = player2_y + game_p2_scaled_height / 2
            player2_current_grid_x = int(player2_center_x // tile_width)
            player2_current_grid_y = int(player2_center_y // tile_height)
            player2_current_grid_x = max(0, min(player2_current_grid_x, grid_cols - 1)) # Clamp grid coords
            player2_current_grid_y = max(0, min(player2_current_grid_y, grid_rows - 1))

            dx_to_p2 = player2_current_grid_x - player1_grid_x
            dy_to_p2 = player2_current_grid_y - player1_grid_y

            move_dx = 0; move_dy = 0
            # Decide movement only if not already in the target adjacent cell
            # Check if P1 needs to move closer (Manhattan distance > 1)
            if abs(dx_to_p2) > 0 or abs(dy_to_p2) > 0: # Only move if not in the same cell
                # Prioritize axis with greater distance
                if abs(dx_to_p2) > abs(dy_to_p2):
                    move_dx = 1 if dx_to_p2 > 0 else -1
                elif abs(dy_to_p2) > abs(dx_to_p2):
                    move_dy = 1 if dy_to_p2 > 0 else -1
                else: # Equal distance, prioritize arbitrarily (e.g., horizontal)
                    if dx_to_p2 != 0:
                        move_dx = 1 if dx_to_p2 > 0 else -1
                    elif dy_to_p2 != 0: # If dx is 0, use dy
                        move_dy = 1 if dy_to_p2 > 0 else -1


            potential_target_grid_x = player1_grid_x + move_dx
            potential_target_grid_y = player1_grid_y + move_dy

            # Check if the potential move is valid (within bounds AND not Player 2's current cell)
            is_valid_move = False
            if 0 <= potential_target_grid_x < grid_cols and 0 <= potential_target_grid_y < grid_rows:
                # Ensure P1 doesn't try to move *into* P2's exact grid cell
                # Note: P1 follows at a distance, so this check might be redundant if distance logic is perfect,
                # but it's safer.
                player2_coll_rect = pygame.Rect(player2_x, player2_y, game_p2_scaled_width, game_p2_scaled_height)
                potential_p1_coll_rect = pygame.Rect(potential_target_grid_x * tile_width, potential_target_grid_y * tile_height, tile_width, tile_height)

                # Check if the potential target cell for P1 overlaps with P2's current collision rectangle
                if not potential_p1_coll_rect.colliderect(player2_coll_rect):
                     is_valid_move = True
                else:
                    # If P1's target cell *does* overlap with P2, print a debug message
                    # print(f"P1 prevented from moving to ({potential_target_grid_x}, {potential_target_grid_y}) because it overlaps with P2.")
                    pass


            if is_valid_move and (move_dx != 0 or move_dy != 0): # Only start moving if a direction was chosen
                player1_target_grid_x = potential_target_grid_x; player1_target_grid_y = potential_target_grid_y
                player1_target_x = player1_target_grid_x * tile_width; player1_target_y = player1_target_grid_y * tile_height
                player1_move_direction = (move_dx, move_dy)
                player1_moving = True
                player1_follow_delay = 5 # Add a small delay between follow moves
            else:
                # Cannot move or doesn't need to move, stay put
                player1_move_direction = (0, 0)
                player1_moving = False
                player1_current_image = elf_down_scaled # Ensure idle pose

        # Decrement follow delay
        if player1_follow_delay > 0: player1_follow_delay -= 1

        # --- Drawing ---
        # Background
        for y in range(grid_rows):
            for x in range(grid_cols):
                img_to_draw = grass_img if grid_pattern[y][x] == 'G' else sand_img
                screen.blit(img_to_draw, (x * tile_width, y * tile_height))

        # Player 1
        screen.blit(player1_current_image, (int(player1_x), int(player1_y)))

        # Player 2 (using NORMAL game scale: game_player2_scaled)
        if player2_current_image: # Check if image exists (in case of load failure)
            # player2_x, player2_y is the top-left corner
            screen.blit(player2_current_image, (int(player2_x), int(player2_y)))

        # Speech bubble
        if show_speech_bubble:
            bubble_width = 80; bubble_height = 30
            bubble_x = int(player1_x + tile_width / 2 - bubble_width / 2)
            bubble_y = int(player1_y - bubble_height - 10) # Position above P1
            # Clamp bubble position to screen
            bubble_x = max(0, min(bubble_x, window_width - bubble_width))
            bubble_y = max(0, bubble_y)

            pygame.draw.ellipse(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height))
            # Draw text inside bubble
            text_surface = font_small.render("...", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(bubble_x + bubble_width / 2, bubble_y + bubble_height / 2))
            screen.blit(text_surface, text_rect)

            # Hide bubble after duration and TRIGGER FOLLOW/UNLOCK
            current_time = pygame.time.get_ticks()
            if current_time - speech_bubble_timer > speech_bubble_duration:
                show_speech_bubble = False
                # --- Trigger Follow and Unlock Player 2 HERE ---
                if not player1_following: # Ensure this block only runs once
                    player1_following = True
                    player1_follow_delay = 0 # Allow the follow logic to run immediately next frame if needed
                    player2_movement_unlocked = True # Unlock Player 2
                    # print("--- SPEECH BUBBLE ENDED: UNLOCKING PLAYER 2 AND STARTING FOLLOW ---") # Optional debug print


        # --- Draw Boundary Notification ---
        if show_boundary_notification:
            # Render the text surface (now black)
            notification_surface = font_notification.render(boundary_notification_text, True, boundary_notification_color)
            # Get the rectangle for the text, centered on screen
            text_rect = notification_surface.get_rect(center=(window_width // 2, window_height // 2))

            # Create the background rectangle with padding
            background_rect = pygame.Rect(0, 0, text_rect.width + 2 * boundary_notification_padding, text_rect.height + 2 * boundary_notification_padding)
            # Center the background rectangle at the same point as the text
            background_rect.center = text_rect.center

            # Draw the white background rectangle
            pygame.draw.rect(screen, boundary_notification_bg_color, background_rect)

            # Draw the black text surface on top of the rectangle
            screen.blit(notification_surface, text_rect)


            # Check if notification duration has passed
            current_time = pygame.time.get_ticks()
            if current_time - boundary_notification_start_time > boundary_notification_duration:
                show_boundary_notification = False

        # Update the display
        pygame.display.flip()

    # Quit Pygame when the main loop ends
    pygame.quit()

# Example usage when running this script directly
if __name__ == "__main__":
    # Ensure required image files exist
    required_files = [
        'grass.png', 'sand.png', 'elfdown.png', 'elfup.png', 'elfleft.png',
        'lightgold.png', # Default fallback P2 sprite
        # Add other potential affinity sprites if testing them:
        'lightsky.png', 'lightwater.png', 'lightfire.png',
        'darkgold.png', 'darksky.png', 'darkwater.png', 'darkfire.png'
    ]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("Error: Missing required image file(s):")
        for f in missing_files: print(f"- {f}")
        print("Please ensure these files are in the same directory as the script.")
        sys.exit()

    # --- Example Game Data ---
    blue = 15; red = 8; brown = 3
    player_color = (0, 128, 255); player_size = 60.75; clue = 42
    # --- Test Different Affinities ---
    affinities = {
        "major": {"type": "Air", "value": 5},
        "minor": {"type": "Fire", "value": 2},
        "light_dark": {"type": "Dark", "value": 4} # Example: Dark Air -> darksky.png
    }
    # affinities = { "major": {"type": "Balance", "value": 0}, "minor": {"type": "None", "value": 7}, "light_dark": {"type": "Light", "value": 3} } # Example: Light Balance -> lightgold.png
    # affinities = { "major": {"type": "Earth", "value": 6}, "minor": {"type": "Water", "value": 1}, "light_dark": None } # Example: None -> Light Earth -> lightgold.png

    created_name = "NoName"

    # Run the game stage function
    run_stage_5(blue, red, brown, player_color, player_size, clue, affinities, created_name)

    # Exit the script cleanly after the game function returns
    sys.exit()