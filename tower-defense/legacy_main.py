import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Minimaliste")

WHITE = (255, 255, 255)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 100)
CYAN = (50, 255, 255)
ORANGE = (255, 150, 0)

font = pygame.font.SysFont("Arial", 20)

path = [(50, 100), (700, 100), (700, 300), (100, 300), (100, 500), (750, 500)]

class Enemy:
    def __init__(self, speed, health, color):
        self.path_index = 0
        self.x, self.y = path[0]
        self.speed = speed
        self.max_health = health
        self.health = health
        self.color = color
        self.slow_timer = 0

    def move(self):
        if self.slow_timer > 0:
            speed = self.speed * 0.5
            self.slow_timer -= 1
        else:
            speed = self.speed

        if self.path_index < len(path) - 1:
            tx, ty = path[self.path_index + 1]
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx, dy = dx / dist, dy / dist
                self.x += dx * speed
                self.y += dy * speed

            if dist < speed:
                self.path_index += 1

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), 10)
        pygame.draw.rect(win, RED, (self.x - 15, self.y - 20, 30, 5))
        pygame.draw.rect(win, GREEN, (self.x - 15, self.y - 20, 30 * self.health / self.max_health, 5))

    def is_dead(self):
        return self.health <= 0

    def reached_end(self):
        return self.path_index >= len(path) - 1

class Boss(Enemy):
    def __init__(self):
        super().__init__(speed=0.8, health=100, color=ORANGE)

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), 20)
        pygame.draw.rect(win, RED, (self.x - 30, self.y - 30, 60, 8))
        pygame.draw.rect(win, GREEN, (self.x - 30, self.y - 30, 60 * self.health / self.max_health, 8))

class Projectile:
    def __init__(self, x, y, target, damage, slow=False):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.slow = slow
        self.speed = 8

    def move(self):
        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx, dy = dx / dist, dy / dist
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, win):
        color = CYAN if self.slow else YELLOW
        pygame.draw.circle(win, color, (int(self.x), int(self.y)), 4)

    def hit(self):
        if math.hypot(self.x - self.target.x, self.y - self.target.y) < 10:
            self.target.health -= self.damage
            if self.slow:
                self.target.slow_timer = 60
            return True
        return False

class Tower:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_
        self.level = 1
        self.reload = 0
        self.range = 100 if type_ == "canon" else 180 if type_ == "sniper" else 120
        self.fire_rate = 30 if type_ == "canon" else 90 if type_ == "sniper" else 60
        self.damage = 1 if type_ == "canon" else 4 if type_ == "sniper" else 0
        self.slow = type_ == "slow"

    def upgrade_cost(self):
        return 30 + (self.level - 1) * 10

    def can_upgrade(self):
        return self.level < 4

    def upgrade(self):
        if self.can_upgrade():
            self.level += 1
            self.range += 20
            self.fire_rate = max(10, self.fire_rate - 5)
            self.damage += 1

    def draw(self, win):
        size = 20 + self.level * 3
        color = BLUE if self.type == "canon" else GREY if self.type == "sniper" else CYAN
        pygame.draw.rect(win, color, (self.x - size//2, self.y - size//2, size, size))
        pygame.draw.circle(win, WHITE, (self.x, self.y), self.range, 1)

        for i in range(self.level - 1):
            pygame.draw.rect(win, YELLOW, (self.x - 10 + i*7, self.y + size//2 + 5, 5, 8))

    def in_range(self, enemy):
        return math.hypot(self.x - enemy.x, self.y - enemy.y) <= self.range

    def update(self, enemies, projectiles):
        if self.reload > 0:
            self.reload -= 1
            return
        for enemy in enemies:
            if self.in_range(enemy):
                projectiles.append(Projectile(self.x, self.y, enemy, self.damage, slow=self.slow))
                self.reload = self.fire_rate
                break

clock = pygame.time.Clock()
enemies = []
towers = [
    Tower(200, 200, "canon"),
    Tower(400, 200, "sniper"),
    Tower(600, 200, "slow"),
]
projectiles = []
score = 0
selected_type = None
enemy_spawn_timer = 0

wave = 1
wave_active = True  # Première vague démarre DIRECTEMENT
wave_countdown = 600  # 10 secondes entre vagues suivantes (60fps * 10s)
wave_enemies_to_spawn = 0

button_rects = {
    "canon": pygame.Rect(10, 10, 60, 30),
    "sniper": pygame.Rect(80, 10, 60, 30),
    "slow": pygame.Rect(150, 10, 60, 30),
}

def spawn_wave(wave_num):
    global wave_enemies_to_spawn
    wave_enemies_to_spawn = wave_num * 5

def spawn_enemy():
    if random.random() < 0.7:
        enemies.append(Enemy(1.5, 5, RED))
    else:
        enemies.append(Enemy(1.0, 10, GREY))

spawn_wave(wave)  # Démarrage immédiat première vague

running = True
while running:
    clock.tick(60)
    WIN.fill(BLACK)
    pygame.draw.lines(WIN, WHITE, False, path, 5)

    if not wave_active:
        wave_countdown -= 1
        countdown_sec = max(0, wave_countdown // 60)
        txt = font.render(f"Prochaine vague dans : {countdown_sec}s", True, WHITE)
        WIN.blit(txt, (WIDTH//2 - txt.get_width()//2, 50))
        if wave_countdown <= 0:
            wave_active = True
            spawn_wave(wave)
    else:
        if wave_enemies_to_spawn > 0:
            if enemy_spawn_timer >= 30:
                spawn_enemy()
                wave_enemies_to_spawn -= 1
                enemy_spawn_timer = 0
        elif len(enemies) == 0:
            wave_active = False
            wave += 1
            wave_countdown = 600  # 10 secondes pour la prochaine vague

    enemy_spawn_timer += 1

    if score >= 1000 and not any(isinstance(e, Boss) for e in enemies):
        enemies.append(Boss())

    for tower in towers:
        tower.update(enemies, projectiles)

    for p in projectiles[:]:
        p.move()
        if p.hit():
            projectiles.remove(p)
        else:
            p.draw(WIN)

    for e in enemies[:]:
        e.move()
        if e.reached_end():
            enemies.remove(e)
            score -= 20
        elif e.is_dead():
            enemies.remove(e)
            score += 50
        else:
            e.draw(WIN)

    for tower in towers:
        tower.draw(WIN)

    for type_, rect in button_rects.items():
        color = GREEN if selected_type == type_ else GREY
        pygame.draw.rect(WIN, color, rect)
        txt = font.render(type_.capitalize(), True, BLACK)
        WIN.blit(txt, (rect.x + 5, rect.y + 5))

    score_txt = font.render(f"Score : {score}", True, WHITE)
    WIN.blit(score_txt, (WIDTH - 150, 10))

    # Barre de niveau à droite
    level = score // 500
    pygame.draw.rect(WIN, GREY, (WIDTH - 100, 50, 20, 200))
    if level > 0:
        pygame.draw.rect(WIN, YELLOW, (WIDTH - 100, 50 + 200 - min(level, 20)*10, 20, min(level, 20)*10))
    lvl_txt = font.render(f"Niveau : {level}", True, WHITE)
    WIN.blit(lvl_txt, (WIDTH - 105, 260))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for type_, rect in button_rects.items():
                if rect.collidepoint(mx, my):
                    selected_type = type_
                    break
            else:
                if selected_type:
                    if all(math.hypot(mx - t.x, my - t.y) > 40 for t in towers):
                        towers.append(Tower(mx, my, selected_type))
                    selected_type = None
                else:
                    for tower in towers:
                        if math.hypot(mx - tower.x, my - tower.y) < 30:
                            cost = tower.upgrade_cost()
                            if tower.can_upgrade() and score >= cost:
                                score -= cost
                                tower.upgrade()
                            break

    pygame.display.flip()

pygame.quit()
sys.exit()
