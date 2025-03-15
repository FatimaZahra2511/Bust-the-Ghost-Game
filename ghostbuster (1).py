import pygame
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and grid
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
GRID_WIDTH, GRID_HEIGHT = 12, 9
CELL_SIZE = SCREEN_HEIGHT // GRID_HEIGHT
INFO_WIDTH = 200

# Colors
BACKGROUND_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
GRID_COLOR = (128, 128, 128)
BUTTON_COLOR = (200, 200, 200)
TEXT_COLOR = (0, 0, 0)
SENSOR_COLORS = {'RED': (255, 0, 0), 'ORANGE': (255, 165, 0), 'YELLOW': (255, 255, 0), 'GREEN': (0, 255, 0)}
BLACK = (0, 0, 0)

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH + INFO_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bust the Ghost')

# Fonts
font = pygame.font.SysFont(None, 36)

# Game variables
game_running = True
game_over = False
game_over_message = ""
clock = pygame.time.Clock()
bust_attempts = 2
score = 35  
peep_enabled = False
ghost_found = False
sensor_readings = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
is_bust_mode = False


# Button definitions
bust_button_rect = pygame.Rect(SCREEN_WIDTH + 30, 10, 140, 40)
peep_button_rect = pygame.Rect(SCREEN_WIDTH + 30, 60, 140, 40)

def PlaceGhost():
    return np.random.randint(0, GRID_WIDTH), np.random.randint(0, GRID_HEIGHT)

ghost_x, ghost_y = PlaceGhost()
probabilities = np.full((GRID_HEIGHT, GRID_WIDTH), 1 / (GRID_WIDTH * GRID_HEIGHT))

def draw_grid():
    screen.fill(BACKGROUND_COLOR, (SCREEN_WIDTH, 0, INFO_WIDTH, SCREEN_HEIGHT))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Draw the sensor color if there is a sensor reading for this cell
            if sensor_readings[y][x]:
                pygame.draw.rect(screen, sensor_readings[y][x], rect)
            else:
                pygame.draw.rect(screen, GRID_COLOR, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_buttons():
    pygame.draw.rect(screen, BUTTON_COLOR, bust_button_rect)
    pygame.draw.rect(screen, BUTTON_COLOR, peep_button_rect)
    bust_text = font.render('Bust', True, TEXT_COLOR)
    peep_text = font.render('Peep', True, TEXT_COLOR)
    screen.blit(bust_text, bust_button_rect.topleft + (10, 10))
    screen.blit(peep_text, peep_button_rect.topleft + (10, 10))

def draw_score_and_attempts():
    attempts_text = font.render(f'Attempts: {bust_attempts}', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(attempts_text, (SCREEN_WIDTH + 10, 110))
    screen.blit(score_text, (SCREEN_WIDTH + 10, 150))

def show_message(message, color, y_offset):
    message_text = font.render(message, True, color)
    message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(message_text, message_rect)

def calculate_distance(x1, y1, x2, y2):
    return max(abs(x1 - x2), abs(y1 - y2))

def get_sensor_reading_color(distance):
    if distance == 0: return 'RED'
    elif distance in [1, 2]: return 'ORANGE'
    elif distance in [3, 4]: return 'YELLOW'
    else: return 'GREEN'

def DistanceSense(x_click, y_click):
    distance = calculate_distance(x_click, y_click, ghost_x, ghost_y)
    return get_sensor_reading_color(distance)

def get_likelihood(distance, sensor_color):
    # Conditional probability values based on sensor accuracy
    probabilities = {
        'RED': {0: 0.9, 1: 0.1},
        'ORANGE': {0: 0.1, 1: 0.8, 2: 0.1},
        'YELLOW': {1: 0.1, 2: 0.7, 3: 0.1, 4: 0.1},
        'GREEN': {2: 0.1, 3: 0.1, 4: 0.8, '>=5': 1.0},
    }
    
    # Check for '>=5' key for distances of 5 or more
    if distance >= 5:
        return probabilities[sensor_color].get('>=5', 0)
    else:
        # Return the corresponding probability if it exists
        return probabilities[sensor_color].get(distance, 0)

def update_probabilities(x, y, sensor_color):
    global probabilities
    likelihood = np.zeros((GRID_HEIGHT, GRID_WIDTH))
    marginal_prob = 0

    # Calculate likelihood and marginal probability
    for j in range(GRID_HEIGHT):
        for i in range(GRID_WIDTH):
            distance = calculate_distance(i, j, x, y)
            likelihood[j, i] = get_likelihood(distance, sensor_color)
            marginal_prob += likelihood[j, i] * probabilities[j, i]

    # Update posterior probabilities
    if marginal_prob > 0:
        probabilities *= likelihood  # element-wise multiplication for the update step
        probabilities /= marginal_prob  # normalization step
    else:
        # Handle the unlikely case where the marginal_prob is 0
        probabilities = np.full((GRID_HEIGHT, GRID_WIDTH), 1 / (GRID_WIDTH * GRID_HEIGHT))

    # Normalization check
    total_prob = np.sum(probabilities)
    if not np.isclose(total_prob, 1.0):
        raise ValueError(f"Normalization error: Probabilities sum to {total_prob}, not 1.")


def handle_click(x, y):
    global game_running, bust_attempts, score, peep_enabled, probabilities, game_over, game_over_message, sensor_readings, is_bust_mode, ghost_x, ghost_y

    grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE

    # Check if the game is in bust mode and handle bust logic
    if is_bust_mode:
        is_bust_mode = False  # Reset the bust mode regardless of outcome
        if (grid_x, grid_y) == (ghost_x, ghost_y):
            game_over = True
            game_over_message = "Ghost busted! You win!"
        else:
            bust_attempts -= 1  # Deduct an attempt only if the bust was not successful
            if bust_attempts == 0:
                game_over = True
                game_over_message = "Game over: No more attempts"
    else:
        # Handle sensor reading and score deduction logic
        if not game_over and 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            score -= 1
            sensor_color = DistanceSense(grid_x, grid_y)
            sensor_readings[grid_y][grid_x] = SENSOR_COLORS[sensor_color]
            update_probabilities(grid_x, grid_y, sensor_color)
            if score <= 0 and not game_over:
                game_over = True
                game_over_message = "Game over: Out of score"

def draw_probabilities():
    if peep_enabled:
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                prob_text = font.render(f'{probabilities[y, x]:.2f}', True, WHITE)
                text_rect = prob_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(prob_text, text_rect)

# Main game loop
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX, mouseY = pygame.mouse.get_pos()
            if bust_button_rect.collidepoint(mouseX, mouseY):
                if not is_bust_mode and bust_attempts > 0:  # Check bust mode and attempts
                    is_bust_mode = True  # Enter bust mode
            elif peep_button_rect.collidepoint(mouseX, mouseY):
                peep_enabled = not peep_enabled  # Toggle peep mode
            elif 0 <= mouseX < SCREEN_WIDTH and 0 <= mouseY < SCREEN_HEIGHT:
                handle_click(mouseX, mouseY)

    screen.fill(BACKGROUND_COLOR)
    draw_grid()
    draw_buttons()
    draw_score_and_attempts()
    
    if game_over:
        show_message(game_over_message, BLACK, -50)
        show_message("Press any key to exit.", BLACK, 50)
    else:
        if peep_enabled:
            draw_probabilities()

    pygame.display.flip()

    if game_over:
        # When the game is over, wait for any key press to exit
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                game_running = False

    clock.tick(60)

pygame.quit()
sys.exit()