import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "tower-defense"))
from rules import Game, Enemy, Tower, PATH, TOWERS, wave_plan, can_place, upgrade_cost

class TowerDefenseTests(unittest.TestCase):
    def test_no_infinite_boss_spawning(self):
        self.assertEqual(wave_plan(4).count("boss"),0)
        self.assertEqual(wave_plan(5).count("boss"),1)
        self.assertEqual(wave_plan(10).count("boss"),1)
    def test_purchase_and_no_free_towers(self):
        g=Game();self.assertFalse(g.place(100,130,"cannon"))
        self.assertTrue(g.place(200,200,"cannon"))
        self.assertEqual(g.coins,130)
        self.assertFalse(g.place(200,200,"sniper"))
    def test_path_endpoint_is_exact(self):
        e=Enemy("runner",1)
        for _ in range(2000):
            if e.travel(.1):break
        self.assertEqual((e.x,e.y),PATH[-1])
        self.assertTrue(e.travel(.1))
    def test_upgrades_cost_and_level_cap(self):
        g=Game();self.assertTrue(g.place(200,200,"cannon"))
        t=g.towers[0];before=g.coins
        self.assertTrue(g.upgrade(t));self.assertEqual(g.coins,before-upgrade_cost(1))
        g.coins=1000
        for _ in range(2):self.assertTrue(g.upgrade(t))
        self.assertEqual(t.level,4);self.assertFalse(g.upgrade(t))
    def test_one_wave_completes_and_awards_income(self):
        g=Game();self.assertTrue(g.start_wave());self.assertFalse(g.start_wave())
        for _ in range(3600):
            g.step(1/60)
            if g.phase!="active":break
        self.assertEqual(g.phase,"ready")
        self.assertEqual(g.wave,2)
        self.assertLess(g.lives,20)
        self.assertGreater(g.coins,200)
    def test_tower_combat_eliminates_enemies(self):
        g=Game()
        self.assertTrue(g.place(200,200,"cannon"));self.assertTrue(g.place(450,200,"cannon"))
        g.start_wave()
        for _ in range(3500):
            g.step(1/60)
            if g.phase=="ready":break
        self.assertGreater(g.kills,0)
        self.assertGreater(g.score,0)
    def test_game_over_prevents_purchases(self):
        g=Game();g.lives=1;g.start_wave()
        g.enemies=[Enemy("boss",1)];g.to_spawn=[]
        g.enemies[0].segment=len(PATH)-2;g.enemies[0].x,g.enemies[0].y=PATH[-1]
        g.step(.05)
        self.assertEqual(g.phase,"game-over")
        self.assertFalse(g.place(200,200,"cannon"))
    def test_tower_specs_and_no_path_placement(self):
        self.assertEqual(set(TOWERS),{"cannon","sniper","frost"})
        self.assertFalse(can_place(100,300,[]))
        self.assertFalse(can_place(-10,200,[]))
        self.assertTrue(can_place(200,200,[]))
    def test_progress_monotonic(self):
        e=Enemy("grunt",1);last=e.progress()
        for _ in range(100):
            e.travel(.07);self.assertGreaterEqual(e.progress(),last);last=e.progress()

if __name__=="__main__":unittest.main()
