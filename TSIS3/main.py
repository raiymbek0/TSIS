import pygame, sys, time, random
from racer import Player, Enemy, Coin, PowerUp, Hazard
from ui import Button, draw_text
from persistence import load_data, save_data, update_leaderboard

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load Settings
settings = load_data('settings.json', {"sound": True, "car_color": "red", "difficulty": 1})
bg = pygame.transform.scale(pygame.image.load("road.jpg"), (WIDTH, HEIGHT))


def game_loop():
    speed = 5 + settings['difficulty']
    score, coins_count = 0, 0
    N = 5
    active_buff = None
    buff_timer = 0
    shielded = False

    player = Player(settings['car_color'])
    enemies = pygame.sprite.Group(Enemy(speed))
    coins = pygame.sprite.Group(Coin())
    powerups = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    bg_y = 0
    running = True
    while running:
        # Dynamic Speed Logic
        current_speed = speed * 1.5 if active_buff == 'nitro' else speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

        # Update Background
        screen.blit(bg, (0, bg_y))
        screen.blit(bg, (0, bg_y - HEIGHT))
        bg_y = (bg_y + current_speed) % HEIGHT

        # Movement
        player.move()
        enemies.update(current_speed)
        coins.update(current_speed)
        powerups.update(current_speed)
        hazards.update(current_speed)

        # Spawning Hazards/Powerups
        if random.random() < 0.01: hazards.add(Hazard())
        if random.random() < 0.005: powerups.add(PowerUp(random.choice(['nitro', 'shield', 'repair'])))

        # Collision: Coins
        coin_hit = pygame.sprite.spritecollideany(player, coins)
        if coin_hit:
            coins_count += coin_hit.weight
            if coins_count // N > (coins_count - coin_hit.weight) // N:
                speed += 0.5
            coin_hit.spawn()

        # Collision: Powerups
        p_hit = pygame.sprite.spritecollideany(player, powerups)
        if p_hit:
            if p_hit.type == 'nitro':
                active_buff = 'nitro'
                buff_timer = time.time() + 4
            elif p_hit.type == 'shield':
                shielded = True
            p_hit.kill()

        # Buff Timers
        if active_buff == 'nitro' and time.time() > buff_timer:
            active_buff = None

        # Collision: Enemies/Hazards
        if pygame.sprite.spritecollideany(player, enemies) or pygame.sprite.spritecollideany(player, hazards):
            if shielded:
                shielded = False
                # Clear hazards/enemies hit
                for h in pygame.sprite.spritecollide(player, hazards, True): pass
                for e in pygame.sprite.spritecollide(player, enemies, False): e.rect.top = -100
            else:
                update_leaderboard("Player", coins_count)
                return "GAME_OVER", coins_count

        # Drawing
        enemies.draw(screen)
        coins.draw(screen)
        powerups.draw(screen)
        hazards.draw(screen)
        screen.blit(player.image, player.rect)

        draw_text(screen, f"Coins: {coins_count}", 20, 10, 10, (0, 0, 0))
        if shielded: draw_text(screen, "SHIELD ON", 15, 10, 40, (0, 255, 255))

        pygame.display.update()
        clock.tick(60)


def main_menu():
    btn_play = Button(100, 200, 200, 50, "PLAY")
    btn_lb = Button(100, 270, 200, 50, "LEADERBOARD")
    while True:
        screen.fill((255, 255, 255))
        draw_text(screen, "RACER ARCADE", 40, WIDTH // 2, 100, center=True)
        btn_play.draw(screen)
        btn_lb.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_play.is_clicked(event): game_loop()
            if btn_lb.is_clicked(event): leaderboard_screen()
        pygame.display.update()


def leaderboard_screen():
    while True:
        screen.fill((240, 240, 240))
        draw_text(screen, "TOP 10", 30, WIDTH // 2, 50, center=True)
        lb = load_data('leaderboard.json', [])
        for i, entry in enumerate(lb[:10]):
            draw_text(screen, f"{i + 1}. {entry['name']} - {entry['score']}", 18, 100, 120 + i * 30)

        btn_back = Button(100, 500, 200, 50, "BACK")
        btn_back.draw(screen)
        for event in pygame.event.get():
            if btn_back.is_clicked(event): return
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()


if __name__ == "__main__":
    main_menu()