"""Tower Defense v2: gameplay and economy independent of pygame."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot

WIDTH, HEIGHT = 740, 640
PATH = ((0, 130), (670, 130), (670, 300), (100, 300), (100, 510), (735, 510))
TOWERS = {
    "cannon": {"cost": 70, "damage": 6, "range": 124, "cooldown": 0.65, "slow": 0},
    "sniper": {"cost": 130, "damage": 21, "range": 215, "cooldown": 2.0, "slow": 0},
    "frost": {"cost": 105, "damage": 2, "range": 135, "cooldown": 1.25, "slow": 1.6},
}
ENEMIES = {
    "grunt": {"hp": 13, "speed": 72, "reward": 10, "leak": 1},
    "runner": {"hp": 9, "speed": 120, "reward": 12, "leak": 1},
    "tank": {"hp": 38, "speed": 43, "reward": 17, "leak": 2},
    "boss": {"hp": 190, "speed": 32, "reward": 90, "leak": 5},
}


def wave_plan(wave: int) -> list[str]:
    if not 1 <= wave <= 100:
        raise ValueError("Wave out of range")
    count = min(35, 4 + wave * 2)
    plan = ["grunt"] * count
    for index in range(count):
        if wave >= 2 and index % 4 == 3:
            plan[index] = "runner"
        if wave >= 3 and index % 7 == 6:
            plan[index] = "tank"
    if wave % 5 == 0:
        plan.append("boss")
    return plan


def distance_to_segment(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((x-a[0])*dx + (y-a[1])*dy) / (dx*dx+dy*dy)))
    return hypot(x-(a[0]+t*dx), y-(a[1]+t*dy))


def can_place(x, y, existing) -> bool:
    if not (28 <= x <= WIDTH-28 and 28 <= y <= HEIGHT-28):
        return False
    if any(distance_to_segment(x, y, a, b) < 34 for a, b in zip(PATH, PATH[1:])):
        return False
    return all(hypot(x-t.x, y-t.y) >= 46 for t in existing)


def upgrade_cost(level: int) -> int:
    if not 1 <= level <= 3:
        raise ValueError("Only tower levels 1..3 can be upgraded")
    return 48 + level * 38


@dataclass
class Tower:
    x: float
    y: float
    kind: str
    level: int = 1
    recharge: float = 0.0
    flash: float = 0.0
    target: tuple[float, float] | None = None

    def range(self):
        return TOWERS[self.kind]["range"] + 15 * (self.level-1)

    def damage(self):
        return TOWERS[self.kind]["damage"] * (1 + 0.6*(self.level-1))

    def cooldown(self):
        return TOWERS[self.kind]["cooldown"] * (0.86 ** (self.level-1))


@dataclass
class Enemy:
    kind: str
    wave: int
    x: float = PATH[0][0]
    y: float = PATH[0][1]
    segment: int = 0
    slow: float = 0.0
    hp: float = field(init=False)

    def __post_init__(self):
        self.hp = ENEMIES[self.kind]["hp"] * (1 + 0.32 * (self.wave - 1))

    def travel(self, seconds):
        movement = ENEMIES[self.kind]["speed"] * min(0.1, max(0, seconds))
        movement *= 0.55 if self.slow > 0 else 1.0
        self.slow = max(0, self.slow-seconds)
        # Consume the entire step at waypoints, with no tunnelling or premature exit.
        while movement > 0 and self.segment < len(PATH)-1:
            tx, ty = PATH[self.segment+1]
            distance = hypot(tx-self.x, ty-self.y)
            if distance <= movement:
                self.x, self.y = tx, ty
                movement -= distance
                self.segment += 1
            else:
                fraction = movement / distance
                self.x += (tx-self.x) * fraction
                self.y += (ty-self.y) * fraction
                movement = 0
        return self.segment == len(PATH)-1

    def progress(self):
        return self.segment + (hypot(self.x-PATH[self.segment][0],self.y-PATH[self.segment][1]) /
                               max(1,hypot(PATH[min(self.segment+1,len(PATH)-1)][0]-PATH[self.segment][0],
                                            PATH[min(self.segment+1,len(PATH)-1)][1]-PATH[self.segment][1])))


class Game:
    def __init__(self):
        self.coins = 200
        self.lives = 20
        self.score = 0
        self.wave = 1
        self.phase = "ready"
        self.towers: list[Tower] = []
        self.enemies: list[Enemy] = []
        self.to_spawn: list[str] = []
        self.spawn_clock = 0.0
        self.kills = 0
        self.leaks = 0

    def place(self, x, y, kind):
        if self.phase == "game-over" or kind not in TOWERS or not can_place(x, y, self.towers):
            return False
        if self.coins < TOWERS[kind]["cost"]:
            return False
        self.coins -= TOWERS[kind]["cost"]
        self.towers.append(Tower(x, y, kind))
        return True

    def upgrade(self, tower):
        if tower not in self.towers or tower.level >= 4 or self.phase == "game-over":
            return False
        cost = upgrade_cost(tower.level)
        if self.coins < cost:
            return False
        self.coins -= cost
        tower.level += 1
        return True

    def start_wave(self):
        if self.phase != "ready":
            return False
        self.phase = "active"
        self.to_spawn = wave_plan(self.wave)
        self.spawn_clock = 0.0
        return True

    def step(self, dt: float):
        if self.phase != "active":
            return
        dt = max(0.0, min(0.1, dt))
        self.spawn_clock -= dt
        if self.to_spawn and self.spawn_clock <= 0:
            self.enemies.append(Enemy(self.to_spawn.pop(0), self.wave))
            self.spawn_clock = max(0.32, 0.76 - 0.055 * (self.wave - 1))
        for enemy in self.enemies[:]:
            if enemy.travel(dt):
                self.enemies.remove(enemy)
                self.lives = max(0, self.lives - ENEMIES[enemy.kind]["leak"])
                self.leaks += 1
        if self.lives <= 0:
            self.phase = "game-over"
            return
        for tower in self.towers:
            tower.recharge -= dt
            tower.flash = max(0, tower.flash-dt)
            if tower.recharge > 0:
                continue
            possible = [e for e in self.enemies if hypot(e.x-tower.x,e.y-tower.y) <= tower.range()]
            if not possible:
                continue
            enemy = max(possible, key=lambda e:e.progress())
            enemy.hp -= tower.damage()
            if TOWERS[tower.kind]["slow"]:
                enemy.slow = max(enemy.slow, TOWERS[tower.kind]["slow"])
            tower.target = (enemy.x, enemy.y)
            tower.flash = 0.12
            tower.recharge = tower.cooldown()
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.coins += ENEMIES[enemy.kind]["reward"]
                self.score += 10 if enemy.kind != "boss" else 100
                self.kills += 1
        if not self.to_spawn and not self.enemies:
            self.phase = "ready"
            self.coins += 18 + self.wave * 3
            self.wave = min(100, self.wave+1)
