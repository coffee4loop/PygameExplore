import pygame
import sys
import random
# No longer need import time for the overlay approach

def name_creation_game():
    """
    Stage 4: A mini-game where the player catches letters to form a name.
    Features a zoomed-in view (viewport) with larger blocks.
    Includes an introductory overlay before the game starts,
    with each word on a new line and specific words being larger.
    The game can be exited early by pressing Enter.
    Instructions are displayed on screen during the game.
    This function returns the created name string for use in Stage 5.
    """
    pygame.init()

    # --- Grid and Viewport Settings ---
    grid_cols = 50  # Total logical grid columns (UNCHANGED)
    grid_rows = 15  # Total logical grid rows (UNCHANGED)

    # --- INCREASED BLOCK SIZE ---
    block_size = 32 # Pixel size of each grid block (Increased from 20)

    view_cols = 12  # Number of columns to DISPLAY in the window
    view_rows = 15  # Number of rows to DISPLAY in the window (same as grid_rows)

    # --- Window Settings (Derived from Viewport and NEW block_size) ---
    ui_height = 100 # Space at the bottom for UI elements (Can adjust if needed)
    window_width = view_cols * block_size  # Window width based on viewport & block_size
    game_area_height = view_rows * block_size # Height of the game area in the window
    window_height = game_area_height + ui_height # Total window height
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Name Creation Game (Large Blocks)")
    clock = pygame.time.Clock()

    # --- ADJUSTED FONT SIZES ---
    # Font for letters in blocks (Increased from 24)
    font = pygame.font.Font(None, 48)
    # Font for UI text (Increased from 18)
    small_font = pygame.font.Font(None, 36)

    # --- Intro Text Fonts ---
    intro_large_font = pygame.font.Font(None, 56) # Larger font size 56
    intro_small_font = pygame.font.Font(None, 36) # Smaller font size 36
    text_color = (255, 255, 255) # White

    # --- Game Mechanics Settings ---
    block_speed = 1 # Grid units per update interval
    update_interval = 250  # Update moving row every 250 milliseconds (Can adjust if movement feels too fast/slow)
    initial_falling_speed = 400 # Initial speed pixels/sec for falling blocks
    falling_speed_increase_rate = 25 # Increase in fall speed pixels/sec
    falling_speed_interval = 0.1 * 1000 # Interval to increase fall speed (ms)
    next_row_delay = 750 # Delay before spawning next row (ms)

    # --- Capture Zone (Updates based on block_size) ---
    zone_width = block_size # Capture zone is one block wide
    zone_grid_x = grid_cols // 2 # LOGICAL position of the zone (center of the GRID)
    # VISUAL position of the zone (center of the WINDOW)
    zone_x = (window_width // 2) - (zone_width // 2)
    zone_y = 0 # Zone starts at the top of the game area

    # --- Viewport Offset (Updates based on block_size and window_width) ---
    grid_center_pixel_x = zone_grid_x * block_size + block_size / 2
    x_offset = grid_center_pixel_x - (window_width / 2)
    x_offset = max(0, min(x_offset, (grid_cols * block_size) - window_width))

    # --- Game State Variables ---
    name = ""
    space_pressed = False
    current_row_index = 0
    spawn_direction = 1 # 1 for left-to-right, -1 for right-to-left
    row_finished = False
    game_over = False # Flag to indicate when the game is ready to end (e.g., Enter pressed)
    next_row_spawn_time = 0
    captured_letter_this_frame = None # Temp store for captured letter feedback
    last_update_time = pygame.time.get_ticks()
    rows_stopped = [False] * grid_rows # Track if a row's horizontal movement stopped
    last_frame_time = pygame.time.get_ticks()
    letter_rows = []      # Holds the blocks for each row
    captured_letters = [] # Holds the successfully captured letter blocks

    # --- Intro Panel State ---
    game_state = 'intro' # Start in the intro state
    intro_duration = 3000 # 3 seconds in milliseconds
    intro_start_ticks = pygame.time.get_ticks() # Time when intro started

    # --- Intro Text Words and Fonts ---
    # List of (word, font) tuples for each line (each word is a new line)
    intro_text_words = [
        ("You", intro_large_font),
        ("are", intro_small_font),
        ("being", intro_small_font),
        ("summoned.", intro_large_font),
        ("", intro_large_font), # Empty string for a blank line
        ("", intro_large_font), # Empty string for a blank line
        ("Tell", intro_large_font),
        ("the", intro_small_font),
        ("summoner", intro_small_font),
        ("your", intro_large_font),
        ("Name.", intro_large_font)
    ]

    # --- Pre-render Intro Text Words ---
    # Store rendered surfaces and their dimensions for drawing
    rendered_intro_words = [] # List of (surface, height) tuples
    total_intro_block_height = 0
    line_spacing = 10 # Vertical space between lines (words)

    for word, font_obj in intro_text_words:
        surface = font_obj.render(word, True, text_color)
        rendered_intro_words.append((surface, surface.get_height()))
        total_intro_block_height += surface.get_height()

    # Add spacing between lines (words)
    if len(rendered_intro_words) > 1:
        total_intro_block_height += line_spacing * (len(rendered_intro_words) - 1)

    # Calculate starting Y position to center the block of text
    start_y = (window_height - total_intro_block_height) // 2


    def create_letter_blocks(row_index, direction):
        """Creates a row of randomly arranged letter blocks across the FULL grid."""
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        random.shuffle(letters)
        print(f"Row {row_index + 1} Letters (first {grid_cols}): {letters[:grid_cols]}") # DEBUG PRINT

        blocks = []
        start_x_grid = 0 if direction == 1 else (grid_cols - 1)
        start_x_pixel = start_x_grid * block_size # Uses new block_size

        for i, letter in enumerate(letters[:grid_cols]):
            x = start_x_pixel + i * block_size * direction # Uses new block_size
            y = row_index * block_size # Uses new block_size
            grid_x = start_x_grid + i * direction

            blocks.append({
                "letter": letter, "x": x, "y": y, "direction": direction,
                "captured": False, "fall_speed": 0, "in_zone": False,
                "original_x": x, "grid_x": grid_x,
                "last_fall_speed_update": pygame.time.get_ticks(),
                "off_screen": False
            })
        return blocks

    # Calculate the left and right edges of the *entire grid* in pixels
    grid_left_edge_pixel = 0
    grid_right_edge_pixel = grid_cols * block_size # Uses new block_size

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_frame_time) / 1000.0
        last_frame_time = current_time

        captured_letter_this_frame = None

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # If in intro state and window closed, just exit
                if game_state == 'intro':
                    return "" # Return empty name
            if event.type == pygame.KEYDOWN:
                # Allow exiting with Enter at any time
                if event.key == pygame.K_RETURN:
                    game_over = True # Set game_over flag
                    running = False # Exit the main game loop
                elif event.key == pygame.K_SPACE and game_state == 'game': # Only process space in game state
                    # Only allow capturing if the current row is not stopped yet
                    if not space_pressed and current_row_index < len(letter_rows) and not rows_stopped[current_row_index]:
                        space_pressed = True
                        captured_block = None
                        min_distance_to_zone = float('inf')
                        closest_block_in_row = None

                        current_row = letter_rows[current_row_index]
                        if current_row:
                            for block in current_row:
                                distance = abs(block["grid_x"] - zone_grid_x)
                                if distance < min_distance_to_zone:
                                    min_distance_to_zone = distance
                                    closest_block_in_row = block

                            if closest_block_in_row:
                                block_screen_x = closest_block_in_row["x"] - x_offset
                                # Check if the block is within the capture zone on screen
                                if zone_x <= block_screen_x < zone_x + zone_width:
                                    captured_block = closest_block_in_row
                                    captured_block["captured"] = True
                                    captured_block["in_zone"] = True
                                    # Lock position to the center of the capture zone grid-wise
                                    captured_block["x"] = zone_grid_x * block_size
                                    captured_block["y"] = current_row_index * block_size

                                    captured_letters.append(captured_block)
                                    name += captured_block["letter"]
                                    captured_letter_this_frame = captured_block

                                    # Stop the horizontal movement of the current row
                                    rows_stopped[current_row_index] = True
                                    row_finished = True # Mark the row as finished processing
                                    next_row_spawn_time = current_time + next_row_delay # Set delay for next row

                                    # Make all other blocks in the row fall
                                    for other_block in current_row:
                                        if not other_block["captured"]:
                                            other_block["fall_speed"] = initial_falling_speed
                                            other_block["last_fall_speed_update"] = current_time
                                # else: # Optional: Handle miss when space is pressed
                                #     print("Miss!")


            if event.type == pygame.KEYUP and game_state == 'game': # Only process keyup in game state
                if event.key == pygame.K_SPACE:
                    space_pressed = False

        # --- Game State Logic and Drawing ---

        screen.fill((0, 0, 0)) # Fill background with black regardless of state

        if game_state == 'intro':
            # Check if intro duration is over
            if current_time - intro_start_ticks >= intro_duration:
                game_state = 'game'
                # Initialize the first row NOW that the intro is over
                if current_row_index < grid_rows:
                    letter_rows.append(create_letter_blocks(current_row_index, spawn_direction))
            else:
                # Draw the multi-line intro text overlay, centered
                current_y = start_y # Start drawing from the calculated top position

                # Draw each word as a separate line
                for surface, height in rendered_intro_words:
                    # Calculate horizontal position to center the word
                    current_x = (window_width - surface.get_width()) // 2
                    screen.blit(surface, (current_x, current_y))
                    current_y += height + line_spacing # Move down for the next word


        elif game_state == 'game':
            # --- Game Logic Update ---

            # 1. Move Current Row Horizontally
            # Only move the current row if it hasn't been stopped by capturing a letter
            if current_row_index < len(letter_rows) and not rows_stopped[current_row_index]:
                if current_time - last_update_time >= update_interval:
                    last_update_time = current_time
                    current_row = letter_rows[current_row_index]
                    if current_row:
                        needs_direction_change = False
                        for block in current_row:
                            # Move the block horizontally
                            block["x"] += block_speed * spawn_direction * block_size
                            block["grid_x"] += block_speed * spawn_direction

                        # Check if any block in the row has reached the grid edge
                        min_x_in_row = min(b["x"] for b in current_row)
                        max_x_in_row = max(b["x"] for b in current_row)

                        # Check against the pixel edges of the entire logical grid
                        if spawn_direction == 1 and max_x_in_row >= grid_right_edge_pixel - block_size:
                                needs_direction_change = True
                        elif spawn_direction == -1 and min_x_in_row <= grid_left_edge_pixel:
                                needs_direction_change = True

                        # Reverse direction if edge is hit
                        if needs_direction_change:
                                spawn_direction *= -1

            # 2. Update Falling Blocks
            # Iterate through all rows to update falling blocks (those not captured)
            for r_idx, row in enumerate(letter_rows):
                if rows_stopped[r_idx]: # Only process falling blocks in rows that have stopped
                    for block in row:
                        if not block["captured"] and not block["off_screen"]:
                            # Increase fall speed over time
                            if current_time - block["last_fall_speed_update"] >= falling_speed_interval:
                                block["fall_speed"] += falling_speed_increase_rate
                                block["last_fall_speed_update"] = current_time
                            # Update vertical position based on fall speed and time delta
                            block["y"] += block["fall_speed"] * dt
                            # Mark block as off screen if it falls below the game area
                            if block["y"] >= game_area_height:
                                block["off_screen"] = True


            # 3. Spawn Next Row
            # If the current row is finished and the delay has passed, spawn the next row
            if row_finished and current_time >= next_row_spawn_time:
                if current_row_index < grid_rows - 1:
                    current_row_index += 1
                    spawn_direction *= -1 # Reverse spawn direction for the next row
                    letter_rows.append(create_letter_blocks(current_row_index, spawn_direction))
                    row_finished = False # Reset row finished flag
                    rows_stopped[current_row_index] = False # Allow the new row to move horizontally
                else:
                    row_finished = False
                    # If the last row is completed, the game is effectively over,
                    # waiting for the user to press Enter to confirm and exit.
                    # This message is now less critical as Enter exits anytime.
                    # print("All rows completed! Press Enter to finish.")

            # --- Drawing (Game Elements) ---

            # 1. Draw the Capture Zone
            light_purple = (200, 150, 255)
            # Draw the rectangle for the capture zone
            pygame.draw.rect(screen, light_purple,
                             (zone_x, zone_y, zone_width, game_area_height), 3) # 3 is the line thickness

            # 2. Draw Letter Blocks
            # Draw all blocks that haven't been captured and are not off-screen
            for row_idx, row in enumerate(letter_rows):
                for block in row:
                    if not block["captured"] and not block["off_screen"]:
                        # Calculate screen position based on block's grid position and viewport offset
                        draw_x = block["x"] - x_offset
                        draw_y = int(block["y"]) # Vertical position is pixel-based for falling

                        # Only draw blocks that are visible within the window width
                        if draw_x + block_size > 0 and draw_x < window_width:
                            # Create a surface for the block
                            block_surface = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                            # Draw the block background (white)
                            pygame.draw.rect(block_surface, (255, 255, 255), (0, 0, block_size, block_size))
                            # Draw the block border (black)
                            pygame.draw.rect(block_surface, (0, 0, 0), (0, 0, block_size, block_size), 1)

                            # Render the letter on the block
                            letter_surface = font.render(block["letter"], True, (0, 0, 0))
                            # Center the letter on the block surface
                            letter_rect = letter_surface.get_rect(center=(block_size // 2, block_size // 2))
                            block_surface.blit(letter_surface, letter_rect)

                            # Draw the block surface onto the main screen
                            screen.blit(block_surface, (draw_x, draw_y))

            # 3. Draw Captured Letters
            # Draw the blocks that have been successfully captured
            for captured_block in captured_letters:
                # Calculate screen position (these are fixed grid positions)
                draw_x = captured_block["x"] - x_offset
                draw_y = int(captured_block["y"])

                if draw_x + block_size > 0 and draw_x < window_width:
                    # Create a surface for the captured block
                    block_surface = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                    # Draw the captured block background (light purple)
                    pygame.draw.rect(block_surface, light_purple, (0, 0, block_size, block_size))
                    # Draw the block border (black)
                    pygame.draw.rect(block_surface, (0, 0, 0), (0, 0, block_size, block_size), 1)

                    # Render the letter on the captured block
                    letter_surface = font.render(captured_block["letter"], True, (0, 0, 0))
                    # Center the letter on the block surface
                    letter_rect = letter_surface.get_rect(center=(block_size // 2, block_size // 2))
                    block_surface.blit(letter_surface, letter_rect)

                    # Draw the captured block surface onto the main screen
                    screen.blit(block_surface, (draw_x, draw_y))


            # 4. Draw UI Elements
            # Define the starting Y position for the UI area
            ui_y_start = game_area_height + 10
            # Draw the background rectangle for the UI area
            pygame.draw.rect(screen, (30, 30, 30), (0, game_area_height, window_width, ui_height))

            # Render and draw the current name
            name_surface = small_font.render(f"Name: {name}", True, (177, 156, 217))
            screen.blit(name_surface, (10, ui_y_start + 0))

            # Display prompt text - now always shows "Press ENTER to finish" or "SPACE to catch"
            prompt_text_catch = "press Space to CATCH LETTERS"
            prompt_text_submit = "press ENTER to SUBMIT NAME"

            # Render the prompt texts
            catch_surface = small_font.render(prompt_text_catch, True, (255, 255, 255))
            submit_surface = small_font.render(prompt_text_submit, True, (255, 255, 255))

            # Draw the prompt texts in the UI area
            screen.blit(catch_surface, (10, ui_y_start + 40)) # Position for "SPACE to catch"
            screen.blit(submit_surface, (10, ui_y_start + 70)) # Position for "ENTER to finish early"


        # --- Display Update ---
        pygame.display.flip() # Update the full screen Surface to the screen
        clock.tick(60) # Limit the frame rate to 60 FPS

    # --- Cleanup ---
    pygame.quit() # Uninitialize all pygame modules
    return name # Return the created name


# --- Main execution block for Stage 4 ---
if __name__ == "__main__":
    # --- Stage 4: Run the name creation game ---
    print("--- Starting Stage 4: Name Creation Game ---")
    created_name = name_creation_game()
    print(f"Stage 4 finished. The created name is: {created_name}")
    # The created_name variable now holds the name to be passed to Stage 5.
    # Stage 5 logic would follow here, using the created_name variable.
    print("--- Stage 4 execution complete. The name is ready for Stage 5. ---")
