"""
FROGGER - Cross the Street (tkinter only)

How to run:
- Save as frogger.py
- Run: python frogger.py

Goal:
- Guide the frog from the bottom to the grass at the top
- Avoid cars
- Reach the goal to score points
- Difficulty increases after each success

Controls:
- Up Arrow    : Move up
- Down Arrow  : Move down
- Left Arrow  : Move left
- Right Arrow : Move right
- R           : Restart after death
- Esc         : Quit
"""

import tkinter as tk
import random

# ----------------------------
# Configuration
# ----------------------------
WIDTH = 420
HEIGHT = 600
GRID = 40

FROG_SIZE = 30
CAR_WIDTH = 50
CAR_HEIGHT = 30

LANES_Y = [440, 400, 360, 320, 280]  # Road lanes
INITIAL_SPEED = 3
FRAME_DELAY = 16  # ~60 FPS

# ----------------------------
# Game Class
# ----------------------------
class FroggerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Frogger")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

        self.speed = INITIAL_SPEED
        self.score = 0
        self.game_over = False
        self.cars = []

        self.draw_world()
        self.create_frog()
        self.create_ui()
        self.bind_keys()

        self.spawn_cars()
        self.game_loop()

    # ----------------------------
    # Setup
    # ----------------------------
    def draw_world(self):
        # Grass (goal)
        self.canvas.create_rectangle(0, 0, WIDTH, GRID, fill="darkgreen")

        # Road
        self.canvas.create_rectangle(0, GRID, WIDTH, 480, fill="gray20")

        # Start area
        self.canvas.create_rectangle(0, 480, WIDTH, HEIGHT, fill="darkgreen")

        # Lane markers
        for y in LANES_Y:
            self.canvas.create_line(0, y + CAR_HEIGHT, WIDTH, y + CAR_HEIGHT,
                                    fill="white", dash=(10, 10))

    def create_frog(self):
        x = WIDTH // 2 - FROG_SIZE // 2
        y = HEIGHT - GRID + (GRID - FROG_SIZE) // 2
        self.frog = self.canvas.create_rectangle(
            x, y, x + FROG_SIZE, y + FROG_SIZE,
            fill="lime"
        )

    def create_ui(self):
        self.score_text = self.canvas.create_text(
            10, HEIGHT - 20,
            anchor="w",
            fill="white",
            font=("Arial", 12),
            text="Score: 0"
        )

        self.instructions = self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2,
            fill="gray",
            font=("Arial", 11),
            text=(
                "FROGGER\n\n"
                "Arrow keys to move\n"
                "Cross the road\n"
                "Avoid cars"
            )
        )

    def bind_keys(self):
        self.root.bind("<Up>", lambda e: self.move_frog(0, -GRID))
        self.root.bind("<Down>", lambda e: self.move_frog(0, GRID))
        self.root.bind("<Left>", lambda e: self.move_frog(-GRID, 0))
        self.root.bind("<Right>", lambda e: self.move_frog(GRID, 0))
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("r", lambda e: self.restart())

    # ----------------------------
    # Gameplay
    # ----------------------------
    def move_frog(self, dx, dy):
        if self.game_over:
            return

        self.canvas.move(self.frog, dx, dy)
        x1, y1, x2, y2 = self.canvas.coords(self.frog)

        # Keep frog inside screen
        if x1 < 0 or x2 > WIDTH or y2 > HEIGHT:
            self.canvas.move(self.frog, -dx, -dy)

        # Reached goal
        if y1 <= GRID:
            self.score += 1
            self.speed += 0.5
            self.reset_frog()

    def spawn_cars(self):
        if self.game_over:
            return

        lane_y = random.choice(LANES_Y)
        direction = random.choice([-1, 1])

        if direction == 1:
            x = -CAR_WIDTH
        else:
            x = WIDTH + CAR_WIDTH

        car = self.canvas.create_rectangle(
            x, lane_y,
            x + CAR_WIDTH, lane_y + CAR_HEIGHT,
            fill="red"
        )

        self.cars.append((car, direction))
        self.root.after(900, self.spawn_cars)

    def game_loop(self):
        if not self.game_over:
            self.update_cars()
            self.check_collisions()
            self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        self.root.after(FRAME_DELAY, self.game_loop)

    def update_cars(self):
        for car, direction in self.cars[:]:
            self.canvas.move(car, direction * self.speed, 0)
            x1, _, x2, _ = self.canvas.coords(car)
            if x2 < -100 or x1 > WIDTH + 100:
                self.canvas.delete(car)
                self.cars.remove((car, direction))

    def check_collisions(self):
        fx1, fy1, fx2, fy2 = self.canvas.coords(self.frog)
        for car, _ in self.cars:
            cx1, cy1, cx2, cy2 = self.canvas.coords(car)
            if not (cx2 < fx1 or cx1 > fx2 or cy2 < fy1 or cy1 > fy2):
                self.end_game()
                return

    # ----------------------------
    # Game Over / Restart
    # ----------------------------
    def reset_frog(self):
        self.canvas.coords(
            self.frog,
            WIDTH // 2 - FROG_SIZE // 2,
            HEIGHT - GRID + (GRID - FROG_SIZE) // 2,
            WIDTH // 2 + FROG_SIZE // 2,
            HEIGHT - GRID + (GRID + FROG_SIZE) // 2,
        )

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 120,
            fill="white",
            font=("Arial", 14, "bold"),
            text=(
                "SPLAT.\n\n"
                f"Final Score: {self.score}\n\n"
                "Press R to Restart\n"
                "Esc to Quit"
            )
        )

    def restart(self):
        if not self.game_over:
            return

        self.canvas.delete("all")
        self.cars.clear()
        self.speed = INITIAL_SPEED
        self.score = 0
        self.game_over = False

        self.draw_world()
        self.create_frog()
        self.create_ui()
        self.spawn_cars()

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    FroggerGame(root)
    root.mainloop()
