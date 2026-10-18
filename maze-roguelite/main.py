import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
TILESIZE = 40
MAP_W, MAP_H = WIDTH // TILESIZE, HEIGHT // TILESIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

def draw_text(surface, text, pos, color=(255,255,255)):
    surface.blit(font.render(text, True, color), pos)

def is_wall(x, y, walls):
    tx, ty = int(x // TILESIZE), int(y // TILESIZE)
    return (tx, ty) in walls

def generate_maze(w, h):
    visited = set()
    walls = set((x, y) for x in range(w) for y in range(h))
    def dfs(cx, cy):
        visited.add((cx, cy))
        walls.discard((cx, cy))
        dirs = [(0,-1), (1,0), (0,1), (-1,0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx+dx, cy+dy
            if 1 <= nx < w-1 and 1 <= ny < h-1 and (nx, ny) not in visited:
                walls.discard((cx + dx//2, cy + dy//2))
                dfs(nx, ny)
    dfs(1,1)
    return walls

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.speed = 4
        self.coins = 0
        self.kamehameha_cooldown = 0
        self.kamehameha_active = False
        self.kamehameha_timer = 0

    def move(self, dx, dy, walls):
        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed
        if not is_wall(nx, self.y, walls):
            self.x = nx
        if not is_wall(self.x, ny, walls):
            self.y = ny

    def draw(self):
        pygame.draw.rect(screen, (0,200,0), (self.x, self.y, TILESIZE, TILESIZE))

    def rect(self):
        return pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)

    def fire_kamehameha(self):
        now = pygame.time.get_ticks()
        if now > self.kamehameha_cooldown:
            self.kamehameha_active = True
            self.kamehameha_timer = now + 500  # visible pendant 0.5s
            self.kamehameha_cooldown = now + 2000  # 2s de cooldown

    def draw_kamehameha(self):
        if self.kamehameha_active:
            pygame.draw.rect(screen, (100, 200, 255), (self.x + TILESIZE, self.y + TILESIZE//4, WIDTH, TILESIZE//2))

    def kamehameha_rect(self):
        return pygame.Rect(self.x + TILESIZE, self.y + TILESIZE//4, WIDTH, TILESIZE//2)

class Enemy:
    def __init__(self, x, y, scale=1.0):
        self.x, self.y = x, y
        self.hp = int(30 * scale)
        self.damage = int(5 * scale)
        self.speed = 2 * scale

    def move_toward(self, target, walls):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = max(1, (dx**2 + dy**2)**0.5)
        dx, dy = dx / dist, dy / dist
        if not is_wall(self.x + dx * self.speed, self.y, walls):
            self.x += dx * self.speed
        if not is_wall(self.x, self.y + dy * self.speed, walls):
            self.y += dy * self.speed

    def draw(self):
        pygame.draw.rect(screen, (200,50,50), (self.x, self.y, TILESIZE, TILESIZE))

    def rect(self):
        return pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)

class Item:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind = kind

    def draw(self):
        color = (0,255,255) if self.kind == "heal" else (255,215,0)
        pygame.draw.rect(screen, color, (self.x, self.y, TILESIZE//2, TILESIZE//2))

    def rect(self):
        return pygame.Rect(self.x, self.y, TILESIZE//2, TILESIZE//2)

def main():
    walls = generate_maze(MAP_W, MAP_H)
    player = Player(100, 100)
    enemies = []
    items = []
    wave = 1
    spawn_timer = 0
    shop_open = False

    while True:
        dt = clock.tick(60)
        screen.fill((20,20,20))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.fire_kamehameha()
                if event.key == pygame.K_e and shop_open:
                    player.max_hp += 10
                    player.damage += 2
                    player.hp = player.max_hp
                    shop_open = False

        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        player.move(dx, dy, walls)

        now = pygame.time.get_ticks()
        if player.kamehameha_active and now > player.kamehameha_timer:
            player.kamehameha_active = False

        spawn_timer += dt
        if spawn_timer > 5000 and not shop_open:
            for _ in range(wave):
                while True:
                    x, y = random.randint(1, MAP_W-2), random.randint(1, MAP_H-2)
                    if (x,y) not in walls:
                        break
                enemies.append(Enemy(x*TILESIZE, y*TILESIZE, 1 + wave*0.1))
            wave += 1
            spawn_timer = 0

        for e in enemies[:]:
            e.move_toward(player, walls)
            if player.kamehameha_active and e.rect().colliderect(player.kamehameha_rect()):
                e.hp -= player.damage * 3
            if e.rect().colliderect(player.rect()):
                player.hp -= e.damage
                enemies.remove(e)
                if random.random() < 0.3:
                    items.append(Item(e.x, e.y, "heal" if random.random() < 0.5 else "coin"))
            if e.hp <= 0:
                enemies.remove(e)

        for item in items[:]:
            if item.rect().colliderect(player.rect()):
                if item.kind == "heal":
                    player.hp = min(player.max_hp, player.hp + 20)
                elif item.kind == "coin":
                    player.coins += 1
                items.remove(item)

        if player.hp <= 0:
            draw_text(screen, "GAME OVER", (WIDTH//2 - 60, HEIGHT//2), (255,0,0))
            pygame.display.flip()
            pygame.time.wait(3000)
            return

        if not enemies and spawn_timer == 0:
            shop_open = True

        for (x,y) in walls:
            pygame.draw.rect(screen, (60,60,60), (x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE))

        player.draw()
        player.draw_kamehameha()
        for e in enemies: e.draw()
        for i in items: i.draw()

        draw_text(screen, f"HP: {player.hp}/{player.max_hp} | DMG: {player.damage} | Coins: {player.coins} | Wave: {wave}", (10,10))
        if shop_open:
            draw_text(screen, "SHOP: Press [E] to upgrade HP and DMG", (WIDTH//2 - 150, HEIGHT//2), (255,255,0))

        pygame.display.flip()

if __name__ == "__main__":
    main()
