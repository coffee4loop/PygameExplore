import pygame
import sys
from PIL import Image

pygame.init()

# --- Loadingscreen Constants ---
TABLET_WIDTH = 500
TABLET_HEIGHT = 500
screen = pygame.display.set_mode((TABLET_WIDTH, TABLET_HEIGHT))
pygame.display.set_caption("GIF Player")

# List of GIF file paths for the loading screen
gif_files = [
    "1stgif.gif", "3rdgif.gif", "4thgif.gif", "5thgif.gif", "filler.gif",
    "zom3.gif", "filler2.gif", "zome2.gif", "zom1.gif",
    "filler3.gif", "filler4.gif", "zoomout.gif",
    "b2final.gif", "b3final.gif", "b4final.gif", "b5final.gif"
]

current_gif_index = 0
frames = []
frame_delays = []
current_frame = 0
last_update = 0
playing = False
reverse_playing = False
waiting_for_start = True
font = pygame.font.SysFont(None, 48)


# --- Loadingscreen Functions ---
def draw_start_button(hovered=False):
    """Draws the 'Remember.' button with rounded edges and pop effect."""
    screen.fill((0, 0, 0))
    button_text = font.render("Remember.", True, (0, 0, 0))
    text_rect = button_text.get_rect(center=(TABLET_WIDTH // 2, TABLET_HEIGHT // 2))

    button_rect = text_rect.inflate(100, 40)

    if hovered:
        button_rect = button_rect.inflate(10, 5)

    pygame.draw.rect(screen, (180, 180, 180), button_rect, border_radius=30)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, width=4, border_radius=30)

    screen.blit(button_text, button_text.get_rect(center=button_rect.center))
    pygame.display.flip()


def load_gif(gif_file):
    """Loads an animated GIF properly using PIL and converts frames to pygame surfaces."""
    global frames, frame_delays, current_frame, last_update, playing, reverse_playing

    try:
        pil_image = Image.open(gif_file)
    except Exception as e:
        print(f"Error loading GIF: {e}")
        return False

    frames = []
    frame_delays = []

    try:
        while True:
            frame = pil_image.convert('RGBA')
            pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA')
            frames.append(pygame_image)

            duration = pil_image.info.get('duration', 100)
            frame_delays.append(duration)

            pil_image.seek(pil_image.tell() + 1)
    except EOFError:
        pass

    if frames:
        current_frame = 0
        last_update = pygame.time.get_ticks()
        reverse_playing = False
        playing = True
        return True
    else:
        print(f"No frames found or error processing GIF: {gif_file}")
        return False



def draw_current_frame():
    """Draws the current frame to the screen, centered."""
    global screen
    if frames:
        frame_to_draw = frames[current_frame]
        screen.fill((0, 0, 0))
        screen.blit(
            frame_to_draw,
            (
                (TABLET_WIDTH - frame_to_draw.get_width()) // 2,
                (TABLET_HEIGHT - frame_to_draw.get_height()) // 2,
            ),
        )



def load_next_gif():
    """Advance to the next gif."""
    global current_gif_index, playing, frames, frame_delays, current_frame, last_update, waiting_for_start
    if current_gif_index >= len(gif_files):
        print("All GIFs played. Exiting.")
        playing = False
        frames = []
        frame_delays = []
        current_gif_index = 0
        waiting_for_start = True
    else:
        current_gif_file = gif_files[current_gif_index]
        print(f"Loading: {current_gif_file}")
        if load_gif(current_gif_file):
            current_gif_index += 1
        else:
            current_gif_index += 1
            load_next_gif()

def play_loading_screen():
    """Function to run the loading screen.  This is what the main program calls."""
    global waiting_for_start, playing, current_gif_index, frames, frame_delays, current_frame, last_update, reverse_playing

    # Reset these.  The main program might call this function multiple times.
    waiting_for_start = True
    playing = False
    current_gif_index = 0
    frames = []
    frame_delays = []
    current_frame = 0
    last_update = 0
    reverse_playing = False
    load_next_gif()

    while True:
        mouse_hovering = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if waiting_for_start:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    button_text = font.render("Remember.", True, (0, 0, 0))
                    text_rect = button_text.get_rect(center=(TABLET_WIDTH // 2, TABLET_HEIGHT // 2))
                    button_rect = text_rect.inflate(100, 40)

                    if button_rect.collidepoint(mouse_pos):
                        waiting_for_start = False
                        playing = True
                        # Don't return here.  Let the GIF play.

        if waiting_for_start:
            mouse_pos = pygame.mouse.get_pos()
            button_text = font.render("Remember.", True, (0, 0, 0))
            text_rect = button_text.get_rect(center=(TABLET_WIDTH // 2, TABLET_HEIGHT // 2))
            button_rect = text_rect.inflate(100, 40)

            if button_rect.collidepoint(mouse_pos):
                mouse_hovering = True
            else:
                mouse_hovering = False

            draw_start_button(hovered=mouse_hovering)
            pygame.time.Clock().tick(60)
            continue

        if playing and frames:
            current_time = pygame.time.get_ticks()
            if current_time - last_update > frame_delays[current_frame]:
                last_update = current_time

                if not reverse_playing:
                    current_frame += 1
                    if current_frame >= len(frames):
                        if current_gif_index == len(gif_files):
                            reverse_playing = True
                            current_frame = len(frames) - 2
                        else:
                            load_next_gif()
                            continue
                else:
                    current_frame -= 1
                    if current_frame < 0:
                        reverse_playing = False
                        playing = False
                        #  sequence:
                        screen.fill((255, 255, 255))  # Flash white
                        pygame.display.flip()
                        pygame.time.delay(300)

                        screen.fill((0, 0, 0))  # Black screen
                        pygame.display.flip()
                        pygame.time.delay(3000)
                        return  # Exit
        if playing and frames:
            draw_current_frame()
            pygame.display.flip()

        pygame.time.Clock().tick(60)
