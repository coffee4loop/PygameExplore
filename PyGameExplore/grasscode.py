import pygame
import sys
import math

# Constants
tile_width = 50
tile_height = 50
grid_cols = 20
grid_rows = 10

# Window size
window_width = tile_width * grid_cols
window_height = tile_height * grid_rows

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Single-Step Grid Movement with Animated Elf")

# Load the images
try:
    grass_img = pygame.image.load('grass.png').convert()
    sand_img = pygame.image.load('sand.png').convert()
    elf_down_img = pygame.image.load('elfdown.png').convert_alpha()
    elf_up_full = pygame.image.load('elfup.png').convert_alpha()
    elf_left_full = pygame.image.load('elfleft.png').convert_alpha()

    # Split elf_up
    up_width = elf_up_full.get_width() // 2
    elf_up_frames = [
        elf_up_full.subsurface(0, 0, up_width, elf_up_full.get_height()),
        elf_up_full.subsurface(up_width, 0, up_width, elf_up_full.get_height())
    ]

    # Split elf_left
    left_width = elf_left_full.get_width() // 2
    elf_left_frames = [
        elf_left_full.subsurface(0, 0, left_width, elf_left_full.get_height()),
        elf_left_full.subsurface(left_width, 0, left_width, elf_left_full.get_height())
    ]

    elf_right_frames = [pygame.transform.flip(img, True, False) for img in elf_left_frames]

    elf_down_scaled = pygame.transform.scale(elf_down_img, (tile_width, tile_height))
    elf_up_scaled = [pygame.transform.scale(img, (tile_width, tile_height)) for img in elf_up_frames]
    elf_left_scaled = [pygame.transform.scale(img, (tile_width, tile_height)) for img in elf_left_frames]
    elf_right_scaled = [pygame.transform.scale(img, (tile_width, tile_height)) for img in elf_right_frames]

except pygame.error as e:
    print(f"Failed to load image: {e}")
    pygame.quit()
    sys.exit()

# Player properties
start_row = 4  # Row 5
start_col = 1  # Column 2
player_grid_y = start_row
player_grid_x = start_col
player_x = player_grid_x * tile_width
player_y = player_grid_y * tile_height
is_moving = False
move_direction = None
animation_timer = 0
animation_speed = 10  # Adjust for animation speed
left_animation_frame = 0
up_animation_frame = 0
current_player_image = elf_right_scaled[0]  # Start facing right

# Define the grid pattern for the background
grid_pattern = [
    ['G', 'G', 'G', 'G', 'G', 'S', 'S', 'S', 'G', 'G', 'G', 'S', 'G', 'G', 'G', 'S', 'S', 'S', 'G', 'G'],
    ['G', 'G', 'G', 'G', 'S', 'G', 'G', 'G', 'G', 'G', 'S', 'S', 'S', 'G', 'G', 'G', 'G', 'G', 'S', 'G'],
    ['G', 'G', 'G', 'S', 'G', 'G', 'S', 'S', 'S', 'S', 'S', 'G', 'S', 'S', 'S', 'S', 'S', 'G', 'G', 'S'],
    ['G', 'G', 'G', 'S', 'G', 'G', 'S', 'G', 'G', 'S', 'G', 'G', 'G', 'S', 'G', 'G', 'S', 'G', 'G', 'S'],
    ['S', 'S', 'G', 'S', 'G', 'G', 'G', 'S', 'S', 'G', 'G', 'S', 'G', 'G', 'S', 'S', 'G', 'G', 'G', 'S'],
    ['S', 'S', 'G', 'S', 'G', 'G', 'G', 'S', 'S', 'G', 'G', 'S', 'G', 'G', 'S', 'S', 'G', 'G', 'G', 'S'],
    ['G', 'G', 'G', 'S', 'G', 'G', 'S', 'G', 'G', 'S', 'G', 'G', 'G', 'S', 'G', 'G', 'S', 'G', 'G', 'S'],
    ['G', 'G', 'G', 'S', 'G', 'G', 'S', 'S', 'S', 'S', 'S', 'G', 'S', 'S', 'S', 'S', 'S', 'G', 'G', 'S'],
    ['G', 'G', 'G', 'G', 'S', 'G', 'G', 'G', 'G', 'G', 'S', 'S', 'S', 'G', 'G', 'G', 'G', 'G', 'S', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'S', 'S', 'S', 'G', 'G', 'G', 'S', 'G', 'G', 'G', 'S', 'S', 'S', 'G', 'G']
]

# Adjust grid dimensions based on the pattern
grid_rows = len(grid_pattern)
grid_cols = len(grid_pattern[0])
window_width = tile_width * grid_cols
window_height = tile_height * grid_rows
screen = pygame.display.set_mode((window_width, window_height))

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not is_moving:
            target_grid_x = player_grid_x
            target_grid_y = player_grid_y

            if event.key == pygame.K_a:
                target_grid_x -= 1
                move_direction = (-1, 0)
            elif event.key == pygame.K_d:
                target_grid_x += 1
                move_direction = (1, 0)
            elif event.key == pygame.K_w:
                target_grid_y -= 1
                move_direction = (0, -1)
            elif event.key == pygame.K_s:
                target_grid_y += 1
                move_direction = (0, 1)

            # Check if the next position is within the grid
            if 0 <= target_grid_x < grid_cols and 0 <= target_grid_y < grid_rows:
                is_moving = True
                target_x = target_grid_x * tile_width
                target_y = target_grid_y * tile_height

    if is_moving:
        player_x += move_direction[0] * 5
        player_y += move_direction[1] * 5

        animation_timer += 1
        if animation_timer >= animation_speed:
            animation_timer = 0
            if move_direction == (-1, 0):
                current_player_image = elf_left_scaled[left_animation_frame % 2]
                left_animation_frame += 1
            elif move_direction == (1, 0):
                current_player_image = elf_right_scaled[left_animation_frame % 2]
                left_animation_frame += 1
            elif move_direction == (0, -1):
                current_player_image = elf_up_scaled[up_animation_frame % 2]
                up_animation_frame += 1
            elif move_direction == (0, 1):
                current_player_image = elf_down_scaled

        distance = math.sqrt((player_x - target_x)**2 + (player_y - target_y)**2)
        if distance < 5:
            player_grid_x += move_direction[0]
            player_grid_y += move_direction[1]
            player_x = player_grid_x * tile_width
            player_y = player_grid_y * tile_height
            is_moving = False
            move_direction = None

    # Draw the background with the sand pattern
    for y in range(grid_rows):
        for x in range(grid_cols):
            tile_type = grid_pattern[y][x]
            if tile_type == 'S':
                screen.blit(sand_img, (x * tile_width, y * tile_height))
            elif tile_type == 'G':
                screen.blit(grass_img, (x * tile_width, y * tile_height))

    # Draw the player
    screen.blit(current_player_image, (int(player_x), int(player_y)))

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()