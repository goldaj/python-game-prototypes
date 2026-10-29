"""Frogger player movement checks without opening a Tkinter window."""
import importlib.util
import types
import unittest
from pathlib import Path

FROG_PATH = Path(__file__).resolve().parents[1] / "frog-crossing" / "main.py"
spec = importlib.util.spec_from_file_location("frog_crossing", FROG_PATH)
game_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_module)


class CanvasStub:
    def __init__(self, rects):
        self.rects = {key: list(value) for key, value in rects.items()}
    def move(self, key, dx, dy):
        self.rects[key] = [x + (dx if i % 2 == 0 else dy)
                           for i, x in enumerate(self.rects[key])]
    def coords(self, key, *value):
        if value:
            self.rects[key] = list(value)
        return self.rects[key][:]
    def create_text(self, *args, **kwargs):
        return 55
    def delete(self, *args, **kwargs):
        return None


def game(rects):
    instance = game_module.FroggerGame.__new__(game_module.FroggerGame)
    instance.canvas = CanvasStub(rects)
    instance.frog = 1
    instance.cars = []
    instance.speed = game_module.INITIAL_SPEED
    instance.score = 0
    instance.game_over = False
    instance.spawn_after_id = "pending-car"
    instance.cancelled = []
    instance.root = types.SimpleNamespace(
        after_cancel=lambda timer: instance.cancelled.append(timer),
    )
    return instance


class FroggerMovementTests(unittest.TestCase):
    def test_invalid_top_and_left_moves_do_not_score_or_escape(self):
        g = game({1: (5, 45, 35, 75)})
        original = g.canvas.coords(1)
        g.move_frog(-40, 0)
        self.assertEqual(g.canvas.coords(1), original)
        g.move_frog(0, -80)
        self.assertEqual(g.canvas.coords(1), original)
        self.assertEqual(g.score, 0)

    def test_reaching_goal_scores_and_returns_to_start(self):
        g = game({1: (200, 45, 230, 75)})
        g.move_frog(0, -40)
        self.assertEqual(g.score, 1)
        self.assertEqual(g.speed, game_module.INITIAL_SPEED + 0.5)
        self.assertEqual(g.canvas.coords(1)[1], 565)

    def test_stepping_into_a_car_causes_immediate_game_over(self):
        g = game({1: (100, 320, 130, 350), 2: (140, 320, 190, 350)})
        g.cars = [(2, 1)]
        g.move_frog(40, 0)
        self.assertTrue(g.game_over)
        self.assertEqual(g.cancelled, ["pending-car"])
        self.assertIsNone(g.spawn_after_id)


if __name__ == "__main__":
    unittest.main()
