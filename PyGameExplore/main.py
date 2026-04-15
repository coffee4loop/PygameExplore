import pygame
import sys
import os  # Import the os module

# Import game stages
from catch_balls import run_game
from next_stage import run_next_stage
from stage3 import run_stage_3, GRID_SIZE
from stage4 import name_creation_game
from stage5 import run_stage_5

# Import the loading screen functions
import loadingscreen  # Import the loadingscreen.py file


pygame.init()

# --- Game Constants ---
TABLET_WIDTH = 500
TABLET_HEIGHT = 500
os.environ['SDL_VIDEO_CENTERED'] = '1' #add this
screen = pygame.display.set_mode((TABLET_WIDTH, TABLET_HEIGHT))  # use same screen.
pygame.display.set_caption("Main Game")  # set different caption

if __name__ == "__main__":

    loadingscreen.play_loading_screen()  # Run the loading screen

    # --- Stage 1: Catch the Falling Balls ---
    print("Starting Stage 1: Catch the Falling Balls...")
    final_color, final_radius, blue, red, brown = run_game()
    print("Stage 1 completed.")
    print(f"Stage 1 results stored: Color={final_color}, Radius={final_radius}, Blue={blue}, Red={red}, Brown={brown}")

    # --- Stage 2: Player Evolution ---
    print("Starting Stage 2: Player Evolution...")
    final_score = run_next_stage(red=red)
    print("Stage 2 completed.")
    print(f"Stage 2 result: Final Score={final_score}")

    try:
        final_score = int(final_score)
        if final_score <= 0:
            print(f"Warning: final_score ({final_score}) is not positive. Setting score to 1.")
            final_score = 1
    except (TypeError, ValueError):
        print(
            "Error: final_score from run_next_stage is not a valid integer (received:"
            f" {final_score}). Setting score to 1."
        )
        final_score = 1

    # --- Stage 3: Exploration & Affinity Discovery ---
    print("Starting Stage 3: Exploration...")
    final_player_pos, final_clicks, affinity_type, affinity_value = run_stage_3(
        final_color,
        final_score
    )
    print("Stage 3 completed.")
    print(
        f"Stage 3 results: Player Pos={final_player_pos}, Clicks={final_clicks}, Affinity Type={affinity_type}, Affinity Value={affinity_value}")

    # --- Calculate Affinities based on Stage 3 results ---
    light_dark_affinity = {"type": affinity_type, "value": affinity_value}

    center = GRID_SIZE // 2
    x = final_player_pos[1] - center
    y = -(final_player_pos[0] - center)

    if abs(x) > abs(y):
        affinity_major = "Fire" if x > 0 else "Water"
        affinity_minor = "Air" if y > 0 else "Earth"
        major_val, minor_val = abs(x), abs(y)
    elif abs(y) > abs(x):
        affinity_major = "Air" if y > 0 else "Earth"
        affinity_minor = "Fire" if x > 0 else "Water"
        major_val, minor_val = abs(y), abs(x)
    else:
        if x == 0:
            affinity_major = ""
            affinity_minor = ""
            major_val, minor_val = 0, 0
        else:
            affinity_major = "Fire" if x > 0 else "Water"
            affinity_minor = "Air" if y > 0 else "Earth"
            major_val, minor_val = abs(x), abs(y)

    affinities = {
        "major": {"type": affinity_major, "value": major_val},
        "minor": {"type": affinity_minor, "value": minor_val},
        "light_dark": light_dark_affinity,
    }
    print(f"Calculated Affinities before modification: {affinities}")

    affinities["light_dark"]["value"] += 3
    print(f"Calculated Affinities after modification for Stage 5: {affinities}")

    # --- Stage 4: Name Creation Game ---
    print("Starting Stage 4: Name Creation Game...")
    created_name = name_creation_game()
    print(f"Stage 4 (Name Game) completed. Created Name: {created_name}")

    # --- Stage 5: Final Stage ---
    print("Starting Stage 5...")
    run_stage_5(
        blue=blue,
        red=red,
        brown=brown,
        player_color=final_color,
        player_size=final_radius,
        clue=final_score,
        affinities=affinities,
        created_name=created_name
    )
    print("Stage 5 completed.")
    print("All stages finished.")

    pygame.quit()
    sys.exit()
