# Step 1: Initialize the game
import pygame
import sys
import numpy as np


pygame.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 900
GRID_SIZE = 4
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("2048")

score = 0
file = open("high_score.txt", "r")
init_high = int(file.readline())
file.close()
high_score = init_high


grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)


def compress(grid):
    new_grid = np.zeros((4, 4), dtype=int)
    for i in range(4):
        pos = 0
        for j in range(4):
            if grid[i][j] != 0:
                new_grid[i][pos] = grid[i][j]
                pos += 1
    return new_grid


def merge(grid):
    global score
    for i in range(4):
        for j in range(3):
            if grid[i][j] == grid[i][j + 1] and grid[i][j] != 0:
                merged_value = grid[i][j] * 2
                grid[i][j] = merged_value
                grid[i][j + 1] = 0
                score += merged_value
    return grid


def draw_score():
    font = pygame.font.SysFont("arial", 40, bold=True)
    score_text = font.render("Score: " + str(score), True, (0, 0, 0))
    screen.blit(score_text, (20, 20))


def transpose(grid):
    return np.transpose(grid)


def move_up(grid):
    grid = transpose(grid)
    grid = move_left(grid)
    grid = transpose(grid)
    return grid


def move_down(grid):
    grid = transpose(grid)
    grid = reverse(grid)
    grid = move_left(grid)
    grid = reverse(grid)
    grid = transpose(grid)
    return grid


def move_left(grid):

    grid = compress(grid)

    grid = merge(grid)

    grid = compress(grid)
    return grid


def move_right(grid):
    grid = reverse(grid)
    grid = move_left(grid)
    grid = reverse(grid)
    return grid


def reverse(grid):
    return np.array([row[::-1] for row in grid])


def update_game(direction):
    global grid
    global score
    old_grid = grid.copy()

    if direction == "UP":
        grid = move_up(grid)
    elif direction == "DOWN":
        grid = move_down(grid)
    elif direction == "LEFT":
        grid = move_left(grid)
    elif direction == "RIGHT":
        grid = move_right(grid)

    if not np.array_equal(old_grid, grid):
        add_new_tile(grid)
        if check_game_over(grid):
            show_game_over()
            return True
    else:
        print("No tiles moved. Try a different direction!")
    return False


def check_game_over(grid):
    global score

    if 0 in grid:
        return False

    for i in range(4):
        for j in range(4):

            if j < 3 and grid[i][j] == grid[i][j + 1]:
                return False

            if i < 3 and grid[i][j] == grid[i + 1][j]:
                return False
    update_high_score(score)
    return True


def add_new_tile(grid):

    empty_positions = [(i, j) for i in range(4) for j in range(4) if grid[i][j] == 0]

    if not empty_positions:
        return grid

    r, c = empty_positions[np.random.randint(0, len(empty_positions))]

    grid[r][c] = np.random.choice([2, 4], p=[0.9, 0.1])
    return grid


def draw_grid(grid_start_x, grid_start_y):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            pygame.draw.rect(
                screen,
                get_tile_color("bg"),
                pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            )

            if grid[y][x] != 0:
                draw_tile_at(grid[y][x], x, y, grid_start_x, grid_start_y)


def update_high_score(new_score):
    global high_score
    if new_score > high_score:
        high_score = new_score
        with open("high_score.txt", "w") as file:
            file.write(str(high_score))


def draw_high_score():
    font = pygame.font.SysFont("arial", 40, bold=True)
    score_text = font.render("High Score: " + str(high_score), True, (0, 0, 0))
    screen.blit(score_text, (20, 60))


def show_game_over():
    screen.fill(get_tile_color("dark text"))

    font = pygame.font.SysFont("arial", 50, bold=True)

    text_game_over = font.render("Game Over!", True, (255, 0, 0))
    text_restart = font.render("Press R to Restart", True, (0, 0, 0))

    text_game_over_rect = text_game_over.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
    )
    text_restart_rect = text_restart.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
    )

    screen.blit(text_game_over, text_game_over_rect)
    screen.blit(text_restart, text_restart_rect)

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    waiting_for_input = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def get_tile_color(value):
    switcher = {
        0: (204, 192, 179),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
        "light text": (249, 246, 242),
        "dark text": (119, 110, 101),
        "other": (0, 0, 0),
        "bg": (187, 173, 160),
    }
    return switcher.get(value)


TILE_GAP = 10  # Gap between tiles


def draw_tile_at(tile_value, current_x, current_y, start_x, start_y):
    pixel_x = start_x + current_x * (TILE_SIZE + TILE_GAP) + TILE_GAP
    pixel_y = start_y + current_y * (TILE_SIZE + TILE_GAP) + TILE_GAP
    size = TILE_SIZE - TILE_GAP

    tile_color = get_tile_color(tile_value)

    pygame.draw.rect(
        screen,
        tile_color,
        pygame.Rect(pixel_x, pixel_y, size, size),
    )

    # Choose text color based on tile value
    if tile_value in [2, 4]:
        text_color = get_tile_color("dark text")
    else:
        text_color = get_tile_color("light text")

    font = pygame.font.SysFont("arial", 40, bold=True)
    text = font.render(str(tile_value), True, text_color)
    text_rect = text.get_rect(
        center=(
            pixel_x + size // 2,
            pixel_y + size // 2,
        )
    )
    screen.blit(text, text_rect)


def draw_bottom_container():
    pygame.draw.rect(screen, "pink", (0, 800, SCREEN_WIDTH, 100))
    draw_score(820)


def draw_score(y_position):
    font = pygame.font.SysFont("arial", 20, bold=False)

    score_text = font.render(f"Score: {score}", False, "black")
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, y_position))
    screen.blit(score_text, score_rect)

    high_score_text = font.render(f"High Score: {high_score}", True, "black")
    high_score_rect = high_score_text.get_rect(
        center=(SCREEN_WIDTH // 2, y_position + 50)
    )
    screen.blit(high_score_text, high_score_rect)


def main():

    global screen, grid, score
    score = 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    screen.fill(get_tile_color("bg"))

    grid_start_x = (
        SCREEN_WIDTH - (GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * TILE_GAP)
    ) / 2 + TILE_GAP
    grid_start_y = (
        800 - (GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * TILE_GAP)
    ) / 2 + TILE_GAP

    add_new_tile(grid)
    add_new_tile(grid)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    update_game("UP")
                elif event.key == pygame.K_DOWN:
                    update_game("DOWN")
                elif event.key == pygame.K_LEFT:
                    update_game("LEFT")
                elif event.key == pygame.K_RIGHT:
                    update_game("RIGHT")

        if check_game_over(grid):
            show_game_over()
            running = False

        draw_grid(grid_start_x, grid_start_y)
        draw_bottom_container()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
