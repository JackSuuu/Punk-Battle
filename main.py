import pygame
from pygame import mixer
from moviepy.editor import VideoFileClip
from fighter import Fighter

mixer.init()
pygame.init()

# Create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Punk Battle")

# Set frame rate
clock = pygame.time.Clock()
FPS = 60

# Define colors
RED = (238, 40, 65)
YELLOW = (255, 255, 0)
GREEN = (84, 237, 100)
GREY = (84, 85, 100)
WHITE = (255, 255, 255)

# Define game variable
intro_screen = True
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]  # Player Score: [p1, p2]
round_over = False
round_over_time = 0
ROUND_OVER_COOLDOWN = 2000

# Define fighter variables
GOD_SIZE = 200
GOD_SCALE = 3
GOD_OFFSET = [82, 65]
GOD_DATA = [GOD_SIZE, GOD_SCALE, GOD_OFFSET]
WARRIOR_SIZE = 162
WARRIOR_SCALE = 3.5
WARRIOR_OFFSET = [65, 53]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]

# Load music & sounds
pygame.mixer.music.load("assets/audio/627040__herb__aiva-cyberpunk-ambient.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

# Load special sound effect
victory_effect = pygame.mixer.Sound("assets/audio/Victory_game_sound.mp3")
victory_effect.set_volume(0.4)
# sword_fx = pygame.mixer.Sound("...") --> add one more parameter in Fighter class to pass the var

# Load static background-image
bg_image = pygame.image.load("assets/images/background/neon.jpg").convert_alpha()

# Load dynamic background image
clip = VideoFileClip("assets/images/background/Sakura_Gif.gif")
frames = [pygame.image.fromstring(frame.tostring(), clip.size, "RGB") for frame in clip.iter_frames()]
frames = [pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT)) for frame in frames]
frame_index = 0

# Load icon
icon_img = pygame.image.load("icon/battle_icon.png").convert_alpha()
transform_icon = pygame.transform.scale(icon_img, (60, 60))

# Load sprite sheets
martial_god_sheet = pygame.image.load("assets/images/martial_god/god.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/images/warrior/warrior.png").convert_alpha()

# Define number of steps in each animation
GOD_ANIMATION_STEPS = [6, 6, 6, 2, 8, 2, 8, 4]
WARRIOR_ANIMATION_STEPS = [7, 7, 7, 3, 10, 3, 8, 3]

# Define font
intro_font = pygame.font.Font("assets/fonts/Silver.ttf", 150)
count_font = pygame.font.Font("assets/fonts/Silver.ttf", 90)  # second parameter is size
score_font = pygame.font.Font("assets/fonts/Silver.ttf", 30)


# Function for drawing text
def draw_text(text, font, text_col, x, y, alpha=255):
    img = font.render(text, True, text_col)
    img.set_alpha(alpha)
    SCREEN.blit(img, (x, y))


# Function for drawing static background
def draw_static_background():
    global bg_image
    scale_background = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    SCREEN.blit(scale_background, (0, 0))


# Function for drawing dynamic background
def draw_dynamic_background():
    global frame_index
    SCREEN.blit(frames[frame_index], (0, 0))
    frame_index = (frame_index + 1) % len(frames)
    if frame_index == len(frames):
        frame_index = 0


# Function for drawing fighter health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(SCREEN, GREY, (x - 5, y - 5, 410, 40))  # Border
    pygame.draw.rect(SCREEN, RED, (x, y, 400, 30))
    pygame.draw.rect(SCREEN, GREEN, (x, y, 400 * ratio, 30))


# Function for drawing a button
def draw_button(x, y):
    button_width = 200
    button_height = 200
    button_rect = pygame.Rect((x, y), button_width, button_height)


# Function for test if the button is being clicked
def is_button_clicked(button_rect):
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        return pygame.mouse.get_pressed()[0]
    return False


# Create two instances of fighters
player_1 = 1
player_2 = 2
fighter__1 = Fighter(player_1, 200, 310, False, GOD_DATA, martial_god_sheet, GOD_ANIMATION_STEPS)
fighter__2 = Fighter(player_2, 700, 290, True, WARRIOR_DATA, wizard_sheet, WARRIOR_ANIMATION_STEPS)


# ============================= Game loop =============================
running = True
while running:
    clock.tick(FPS)

    # Display the intro screen when activate the game
    if intro_screen:
        draw_static_background()
        draw_text("PUNK BATTLE", intro_font, WHITE, 240, 80)
        draw_text("press space to start", score_font, WHITE, 400, 200)
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            intro_screen = False
    else:
        # Draw background
        draw_dynamic_background()

        # Show player stats
        draw_health_bar(fighter__1.health, 20, 20)
        draw_health_bar(fighter__2.health, 580, 20)
        draw_text(f"P1 SCORE:  {score[0]}", score_font, WHITE, 315, 60)
        draw_text(f"P2 SCORE:  {score[1]}", score_font, WHITE, 580, 60)

        # Update count down
        if intro_count <= 0:
            # Display icon
            SCREEN.blit(transform_icon, ((SCREEN_WIDTH / 2) - 30, SCREEN_HEIGHT - 580))
            # Move fighters
            fighter__1.movement(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN, fighter__2)
            fighter__2.movement(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN, fighter__1)
        else:
            # Display count timer
            draw_text(str(intro_count), count_font, WHITE, (SCREEN_WIDTH / 2) - 10, SCREEN_HEIGHT - 590)
            # Update count timer
            if pygame.time.get_ticks() - last_count_update >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        # Update fighters
        fighter__1.update()
        fighter__2.update()

        # Draw fighters
        fighter__1.draw(SCREEN)
        fighter__2.draw(SCREEN)

        # Check for player defeat
        if not round_over:
            if not fighter__1.alive:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif not fighter__2.alive:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else:
            # Display victory
            draw_text('VICTORY!', count_font, YELLOW, 400, 95)
            victory_effect.play()
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 3
                fighter__1 = Fighter(player_1, 200, 310, False, GOD_DATA, martial_god_sheet, GOD_ANIMATION_STEPS)
                fighter__2 = Fighter(player_2, 700, 290, True, WARRIOR_DATA, wizard_sheet, WARRIOR_ANIMATION_STEPS)

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update display
    pygame.display.update()

# Exit pygame
pygame.quit()
