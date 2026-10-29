"""Reproducible simplified economy/gameplay simulations; no pygame required."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tower-defense"))
from rules import Game, TOWERS

def simulate(strategy, max_wave=8):
    game=Game()
    while game.phase!="game-over" and game.wave<=max_wave:
        if strategy=="basic":
            spots=[(200,200,"cannon"),(450,200,"cannon"),(620,400,"sniper"),(200,400,"frost")]
            for x,y,t in spots:
                if not any(abs(x-a.x)<1 and abs(y-a.y)<1 for a in game.towers):
                    game.place(x,y,t)
        game.start_wave()
        for _ in range(5000):
            game.step(1/60)
            if game.phase!="active":break
        else:raise RuntimeError("Wave did not terminate")
    return {"strategy":strategy,"wave":game.wave,"lives":game.lives,"kills":game.kills,"leaks":game.leaks,"coins":game.coins,"score":game.score}

if __name__=="__main__":
    for strategy in ("no-towers","basic"):
        print(simulate(strategy))
