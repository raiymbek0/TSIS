import pygame
import sys
import json
from db import Database
from game import Snake, Food
from config import DB_CONFIG, SCREEN_WIDTH, SCREEN_HEIGHT

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake TSIS4 - PostgreSQL Edition')
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("Verdana", 20)

# Подключение к БД
db = Database(DB_CONFIG)


def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except:
        return {"snake_color": [0, 255, 0], "grid": True, "sound": True}


def main():
    # 1. Ввод имени в консоли (как на твоем скрине)
    username = input("Enter Username: ")

    settings = load_settings()
    snake = Snake(settings['snake_color'])

    # Инициализация еды и препятствий (Task 3.2, 3.4)
    # Передаем пустой список препятствий для начала
    food = Food((0, 255, 0), 1)
    food.spawn([], snake.body)

    score = 0
    level = 1
    running = True

    # 2. ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
    while running:
        screen.fill((0, 0, 0))  # Очистка экрана

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Управление змейкой
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 20):
                    snake.direction = (0, -20)
                if event.key == pygame.K_DOWN and snake.direction != (0, -20):
                    snake.direction = (0, 20)
                if event.key == pygame.K_LEFT and snake.direction != (20, 0):
                    snake.direction = (-20, 0)
                if event.key == pygame.K_RIGHT and snake.direction != (-20, 0):
                    snake.direction = (20, 0)

        # Движение змейки
        head = snake.move()

        # Проверка столкновения со стенами
        if (head[0] < 0 or head[0] >= SCREEN_WIDTH or
                head[1] < 0 or head[1] >= SCREEN_HEIGHT or
                head in snake.body[1:]):
            print(f"Game Over! Score: {score}")
            db.save_result(username, score, level)  # Сохранение в БД (Task 3.1)
            running = False

        # Проверка поедания еды
        if head == food.pos:
            score += food.weight
            food.spawn([], snake.body)
            # Увеличение уровня каждые 3 еды
            if score % 3 == 0:
                level += 1
        else:
            snake.body.pop()  # Удаляем хвост, если ничего не съели

        # ОТРИСОВКА
        # Рисуем змейку
        for block in snake.body:
            pygame.draw.rect(screen, snake.color, (block[0], block[1], 18, 18))

        # Рисуем еду
        pygame.draw.rect(screen, food.color, (food.pos[0], food.pos[1], 20, 20))

        # Текст (Score, Level, User)
        info_txt = font_small.render(f"User: {username} | Score: {score} | Level: {level}", True, (255, 255, 255))
        screen.blit(info_txt, (10, 10))

        pygame.display.flip()
        clock.tick(10 + level)  # Скорость растет с уровнем

    pygame.quit()


if __name__ == "__main__":
    main()