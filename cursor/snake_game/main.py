import pygame
import random
import sys

# 初始化 pygame
pygame.init()

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# 游戏窗口设置
WIDTH = 800
HEIGHT = 600
SNAKE_SIZE = 20
SNAKE_SPEED = 15

# 创建游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('贪吃蛇游戏')

# 时钟控制游戏速度
clock = pygame.time.Clock()

# 字体设置
font_style = pygame.font.SysFont('bahnschrift', 25)
score_font = pygame.font.SysFont('comicsansms', 35)


def display_score(score):
    """显示得分"""
    value = score_font.render("得分: " + str(score), True, BLUE)
    screen.blit(value, [10, 10])


def draw_snake(snake_block, snake_list):
    """绘制蛇"""
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])


def message(msg, color):
    """显示消息"""
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])


def game_loop():
    """主游戏循环"""
    game_over = False
    game_close = False

    # 初始蛇的位置
    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    # 蛇的身体
    snake_list = []
    length_of_snake = 1

    # 食物位置
    foodx = round(random.randrange(0, WIDTH - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
    foody = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE

    while not game_over:

        while game_close:
            screen.fill(BLACK)
            message("游戏结束! 按 Q 退出 或 C 重新开始", RED)
            display_score(length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change != SNAKE_SIZE:
                    x1_change = -SNAKE_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change != -SNAKE_SIZE:
                    x1_change = SNAKE_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change != SNAKE_SIZE:
                    y1_change = -SNAKE_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change != -SNAKE_SIZE:
                    y1_change = SNAKE_SIZE
                    x1_change = 0

        # 检查边界碰撞
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        screen.fill(BLACK)

        # 绘制食物
        pygame.draw.rect(screen, RED, [foodx, foody, SNAKE_SIZE, SNAKE_SIZE])

        # 更新蛇的身体
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # 检查自身碰撞
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(SNAKE_SIZE, snake_list)
        display_score(length_of_snake - 1)

        pygame.display.update()

        # 吃到食物
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WIDTH - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
            foody = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
            length_of_snake += 1

        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
