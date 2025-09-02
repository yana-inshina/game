import pygame, random, math

pygame.init()

W, H = 800, 400
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Geometry dash")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

BG_COLOR = (128, 0, 128)
PLAYER_COLOR = (255, 255, 0)
OBSTACLE_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

ground = H
player_height = 30
player = pygame.Rect(100, ground - player_height, 30, player_height)
y_vel = 0
gravity = 0.6
jump_power = -13
is_jumping = False

obstacles = []
speed = 4
score = 0
game_over = False
last_obstacle_time = 0

def create_obstacle():
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

running = True
while running:
    current_time = pygame.time.get_ticks()
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not is_jumping:
                y_vel = jump_power
                is_jumping = True
            if event.key == pygame.K_r and game_over:
                player.y = ground - player_height
                obstacles = []
                score = 0
                y_vel = 0
                is_jumping = False
                game_over = False
                speed = 4

    if not game_over:
        y_vel += gravity
        player.y += y_vel

        if player.y >= ground - player.height:
            player.y = ground - player.height
            y_vel = 0
            is_jumping = False

        if (current_time - last_obstacle_time > 1500 and
            (not obstacles or W - get_obstacle_right_edge(obstacles[-1]) > 300)):
            obstacles.append(create_obstacle())
            last_obstacle_time = current_time

        for obs in obstacles[:]:
            obs['x'] -= speed

            if obs['x'] < -50:
                obstacles.remove(obs)
                score += 1

            if obs['type'] == 'rect':
                obs_rect = pygame.Rect(obs['x'], obs['y'], obs['width'], obs['height'])
                if player.colliderect(obs_rect):
                    game_over = True
            else:
                if (player.right > obs['x'] - obs['size'] and
                    player.left < obs['x'] + obs['size'] and
                    player.bottom > obs['y'] - obs['size'] and
                    player.top < obs['y']):
                    game_over = True

        if score % 20 == 0 and score > 0:
            speed = 4 + score // 20

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
        over_text = font.render("GAME OVER! Press R to restart", True, TEXT_COLOR)
        text_rect = over_text.get_rect(center=(W // 2, H // 2))
        screen.blit(over_text, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

exit()
