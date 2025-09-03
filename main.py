import pygame
import sys
import math
import random

W, H = 800, 400          
FPS = 60                 

BG_COLOR = (128, 0, 128)
PLAYER_COLOR = (255, 255, 0)
OBSTACLE_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

def create_obstacle(W, ground):
    """Случайное препятствие: прямоугольник высокий/низкий или «треугольник»."""
    obs_type = random.choice(['rect', 'triangle', 'rect_low'])
    if obs_type == 'rect':
        height = random.randint(40, 70)
        return {'type': 'rect', 'x': W, 'y': ground - height, 'width': 30, 'height': height}
    elif obs_type == 'triangle':
        size = random.randint(25, 40)
        return {'type': 'triangle', 'x': W, 'y': ground, 'size': size}
    else:
        return {'type': 'rect', 'x': W, 'y': ground - 20, 'width': 50, 'height': 20}

def get_obstacle_right_edge(obs):
    if obs['type'] == 'rect':
        return obs['x'] + obs['width']
    else:
        return obs['x'] + obs['size']

def main():
    # инициализация pygame
    pygame.init()

    # масштабируемое окно без fullscreen — для веба стабильнее
    screen = pygame.display.set_mode((W, H), flags=pygame.SCALED)
    pygame.display.set_caption("парка")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # мир
    ground = H
    player_height = 30
    player = pygame.Rect(100, ground - player_height, 30, player_height)
    y_vel = 0.0
    gravity = 0.6
    jump_power = -13
    is_jumping = False

    obstacles = []
    speed = 4
    score = 0
    game_over = False
    last_obstacle_time = 0

    running = True
    while running:
        # --- события ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # поддержка клавиатуры и тача/мыши (клик = пробел)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP) and not game_over and not is_jumping:
                    y_vel = jump_power
                    is_jumping = True
                if event.key == pygame.K_r and game_over:
                    # мягкий рестарт
                    obstacles.clear()
                    score = 0
                    y_vel = 0
                    is_jumping = False
                    game_over = False
                    speed = 4
                    player.y = ground - player_height

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if not game_over and not is_jumping:
                    y_vel = jump_power
                    is_jumping = True
                elif game_over:
                    # рестарт по клику
                    obstacles.clear()
                    score = 0
                    y_vel = 0
                    is_jumping = False
                    game_over = False
                    speed = 4
                    player.y = ground - player_height

        # --- логика ---
        screen.fill(BG_COLOR)
        if not game_over:
            # физика прыжка
            y_vel += gravity
            player.y += y_vel

            # приземление
            if player.y >= ground - player.height:
                player.y = ground - player.height
                y_vel = 0
                is_jumping = False

            # генерация препятствий по времени и дистанции
            now = pygame.time.get_ticks()
            if (now - last_obstacle_time > 1500 and
                (not obstacles or W - get_obstacle_right_edge(obstacles[-1]) > 300)):
                obstacles.append(create_obstacle(W, ground))
                last_obstacle_time = now

            # движение и коллизии
            for obs in obstacles[:]:
                obs['x'] -= speed

                if obs['x'] < -60:
                    obstacles.remove(obs)
                    score += 1

                hit = False
                if obs['type'] == 'rect':
                    obs_rect = pygame.Rect(obs['x'], obs['y'], obs['width'], obs['height'])
                    hit = player.colliderect(obs_rect)
                else:  # triangle — грубая AABB-проверка
                    if (player.right > obs['x'] - obs['size'] and
                        player.left < obs['x'] + obs['size'] and
                        player.bottom > obs['y'] - obs['size'] and
                        player.top < obs['y']):
                        hit = True
                if hit:
                    game_over = True

            # постепенное усложнение
            if score > 0 and score % 20 == 0:
                speed = 4 + score // 20

        # --- отрисовка ---
        pygame.draw.rect(screen, PLAYER_COLOR, player)

        for obs in obstacles:
            if obs['type'] == 'rect':
                pygame.draw.rect(screen, OBSTACLE_COLOR,
                                 (obs['x'], obs['y'], obs['width'], obs['height']))
            else:
                pygame.draw.polygon(screen, OBSTACLE_COLOR, [
                    (obs['x'], obs['y'] - obs['size']),
                    (obs['x'] - obs['size'], obs['y']),
                    (obs['x'] + obs['size'], obs['y'])
                ])

        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        if game_over:
            over_text = font.render("GAME OVER! Press R or click to restart", True, TEXT_COLOR)
            text_rect = over_text.get_rect(center=(W // 2, H // 2))
            screen.blit(over_text, text_rect)

        pygame.display.flip()

        # НИКАКОГО time.sleep — только tick (дружит с браузером)
        clock.tick(FPS)

    pygame.quit()
    # не вызываем sys.exit() в вебе — просто выходим из main()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # чтобы в браузере видеть ошибку в консоли
        print("Unhandled exception:", e, file=sys.stderr)
        raise

