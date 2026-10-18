# Pong à deux joueurs (Python + pygame)
# Contrôles:
#  - Joueur gauche : Z (haut), S (bas)
#  - Joueur droit  : Flèche Haut, Flèche Bas
# Exécution: python pong.py
#
# Aucune dépendance externe autre que pygame.
# pip install pygame

import pygame
import sys

# ---------- Config ----------
WIDTH, HEIGHT = 900, 600
FPS = 60

PADDLE_W, PADDLE_H = 14, 100
PADDLE_SPEED = 6

BALL_SIZE = 14
BALL_SPEED_X = 6
BALL_SPEED_Y = 4

WIN_SCORE = 10

BG_COLOR = (15, 18, 30)
FG_COLOR = (230, 235, 245)
ACCENT = (120, 170, 255)
NET_COLOR = (60, 70, 100)

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def draw_center_net(surface):
    seg_h = 18
    gap = 12
    x = WIDTH // 2 - 2
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, NET_COLOR, (x, y, 4, seg_h))
        y += seg_h + gap

# ---------- Entities ----------
class Paddle(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, PADDLE_W, PADDLE_H)
        self.v = 0

    def move_up(self):
        self.v = -PADDLE_SPEED

    def move_down(self):
        self.v = PADDLE_SPEED

    def stop(self):
        self.v = 0

    def update(self):
        self.y += self.v
        self.y = clamp(self.y, 0, HEIGHT - PADDLE_H)

class Ball(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, BALL_SIZE, BALL_SIZE)
        self.vx = BALL_SPEED_X
        self.vy = BALL_SPEED_Y

    def reset(self, direction=1):
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.vx = BALL_SPEED_X * direction
        self.vy = BALL_SPEED_Y * (-1 if direction < 0 else 1)

    def update(self):
        self.x += int(self.vx)
        self.y += int(self.vy)

        # Collisions mur haut/bas
        if self.top <= 0:
            self.top = 0
            self.vy = -self.vy
        elif self.bottom >= HEIGHT:
            self.bottom = HEIGHT
            self.vy = -self.vy

# ---------- Main ----------
def main():
    pygame.init()
    pygame.display.set_caption("Pong - 2 joueurs")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    small = pygame.font.SysFont(None, 24)

    left = Paddle(40, HEIGHT // 2 - PADDLE_H // 2)
    right = Paddle(WIDTH - 40 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2)
    ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2)

    score_l = 0
    score_r = 0

    # Inputs continus
    key_state = {
        "l_up": False,
        "l_down": False,
        "r_up": False,
        "r_down": False,
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Joueur gauche (AZERTY): Z/S
                if event.key == pygame.K_z:
                    key_state["l_up"] = True
                if event.key == pygame.K_s:
                    key_state["l_down"] = True
                # Joueur droit: flèches
                if event.key == pygame.K_UP:
                    key_state["r_up"] = True
                if event.key == pygame.K_DOWN:
                    key_state["r_down"] = True

                # Reset rapide
                if event.key == pygame.K_r:
                    score_l, score_r = 0, 0
                    ball.reset(direction=1)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_z:
                    key_state["l_up"] = False
                if event.key == pygame.K_s:
                    key_state["l_down"] = False
                if event.key == pygame.K_UP:
                    key_state["r_up"] = False
                if event.key == pygame.K_DOWN:
                    key_state["r_down"] = False

        # Applique vitesses paddles
        left.v = 0
        right.v = 0
        if key_state["l_up"]:
            left.move_up()
        if key_state["l_down"]:
            left.move_down()
        if key_state["r_up"]:
            right.move_up()
        if key_state["r_down"]:
            right.move_down()

        left.update()
        right.update()
        ball.update()

        # Collision avec paddles
        if ball.colliderect(left) and ball.vx < 0:
            # Calcul angle selon point d'impact
            offset = (ball.centery - left.centery) / (PADDLE_H / 2)
            ball.left = left.right
            ball.vx = -ball.vx
            ball.vy = clamp(ball.vy + offset * 4, -10, 10)

        if ball.colliderect(right) and ball.vx > 0:
            offset = (ball.centery - right.centery) / (PADDLE_H / 2)
            ball.right = right.left
            ball.vx = -ball.vx
            ball.vy = clamp(ball.vy + offset * 4, -10, 10)

        # Points
        if ball.right < 0:
            score_r += 1
            ball.reset(direction=1)
        elif ball.left > WIDTH:
            score_l += 1
            ball.reset(direction=-1)

        # Victoire
        winner = None
        if score_l >= WIN_SCORE:
            winner = "Gauche"
        elif score_r >= WIN_SCORE:
            winner = "Droite"

        # ---------- Rendu ----------
        screen.fill(BG_COLOR)
        draw_center_net(screen)

        # Paddles et balle
        pygame.draw.rect(screen, FG_COLOR, left)
        pygame.draw.rect(screen, FG_COLOR, right)
        pygame.draw.ellipse(screen, ACCENT, ball)

        # Scores
        score_text = font.render(f"{score_l}    {score_r}", True, FG_COLOR)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        # Aide
        help1 = small.render("Gauche: Z/S   Droite: ↑/↓   R: reset   Échap: quitter", True, (180,190,210))
        screen.blit(help1, (WIDTH // 2 - help1.get_width() // 2, HEIGHT - 30))

        # Écran de victoire
        if winner is not None:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            msg = font.render(f"Victoire côté {winner}!", True, (255, 255, 255))
            tip = small.render("Appuyez sur R pour relancer", True, (230, 235, 245))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 + 18))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
