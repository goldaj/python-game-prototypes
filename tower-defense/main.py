"""Play the new deterministic-economy Tower Defense with pygame."""
import sys
import pygame
from rules import Game, PATH, WIDTH, HEIGHT, TOWERS, upgrade_cost

PANEL = 230
WHITE = (235, 237, 248)
pygame.init()
screen = pygame.display.set_mode((WIDTH+PANEL, HEIGHT))
pygame.display.set_caption("Tower Defense : stratégie et économie")
clock=pygame.time.Clock()
font=pygame.font.SysFont("arial",19)
small=pygame.font.SysFont("arial",15)
large=pygame.font.SysFont("arial",28,bold=True)
colors={"cannon":(75,135,255),"sniper":(242,192,79),"frost":(103,224,237)}
enemycolors={"grunt":(221,85,79),"runner":(241,140,78),"tank":(147,111,185),"boss":(246,84,183)}
buttons={name:pygame.Rect(WIDTH+15,150+i*60,PANEL-30,49) for i,name in enumerate(TOWERS)}
game=Game()
selected="cannon"
paused=False
message="Choisis tes tours puis Espace pour lancer la vague."

def line(text,x,y,color=WHITE,small_text=False):
    f=small if small_text else font
    screen.blit(f.render(text,True,color),(x,y))

def draw():
    screen.fill((22,26,40))
    pygame.draw.lines(screen,(103,110,137),False,PATH,65)
    pygame.draw.lines(screen,(173,174,185),False,PATH,3)
    for tower in game.towers:
        if tower.flash>0 and tower.target:
            pygame.draw.line(screen,(251,229,156),(tower.x,tower.y),tower.target,3)
        pygame.draw.circle(screen,colors[tower.kind],(int(tower.x),int(tower.y)),14+tower.level*2)
        pygame.draw.circle(screen,(210,210,240),(int(tower.x),int(tower.y)),tower.range(),1)
        line(str(tower.level),tower.x-5,tower.y-11,(15,20,36),True)
    for enemy in game.enemies:
        x,y=int(enemy.x),int(enemy.y)
        size=20 if enemy.kind=="boss" else 13 if enemy.kind=="tank" else 10
        pygame.draw.circle(screen,enemycolors[enemy.kind],(x,y),size)
        if enemy.slow>0:pygame.draw.circle(screen,(85,235,244),(x,y),size+4,2)
        maximum=__import__("rules").ENEMIES[enemy.kind]["hp"]*(1+.14*(enemy.wave-1))
        pygame.draw.rect(screen,(75,35,38),(x-size,y-size-11,size*2,4))
        pygame.draw.rect(screen,(95,223,133),(x-size,y-size-11,int(size*2*max(0,enemy.hp)/maximum),4))
    pygame.draw.rect(screen,(30,34,55),(WIDTH,0,PANEL,HEIGHT))
    line("TOUR DE DÉFENSE",WIDTH+15,18)
    line(f"Vague {game.wave} | {game.phase}",WIDTH+15,53)
    line(f"Pièces : {game.coins}",WIDTH+15,81,(235,209,112))
    line(f"Vies : {game.lives}  Score : {game.score}",WIDTH+15,108)
    for name,rect in buttons.items():
        pygame.draw.rect(screen,colors[name] if selected==name else (75,79,108),rect,border_radius=9)
        pygame.draw.rect(screen,(180,180,209),rect,2,border_radius=9)
        label=f"{name.title()}  {TOWERS[name]['cost']} pièces"
        line(label,rect.x+11,rect.y+11,(16,20,37) if selected==name else WHITE)
    line("Clic terrain : placer",WIDTH+15,353,small_text=True)
    line("Clic sur tour : améliorer",WIDTH+15,378,small_text=True)
    line("1/2/3 : type | Espace : vague",WIDTH+15,413,small_text=True)
    line("P : pause | R : recommencer",WIDTH+15,439,small_text=True)
    line("Aucun placement sur le chemin",WIDTH+15,464,small_text=True)
    line(f"Ennemis restants : {len(game.to_spawn)+len(game.enemies)}",WIDTH+15,510,small_text=True)
    line(f"Éliminés : {game.kills}   Fuites : {game.leaks}",WIDTH+15,535,small_text=True)
    status=message[:36]
    line(status,WIDTH+15,595,(204,216,249),True)
    if game.phase=="game-over" or paused:
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA);overlay.fill((0,0,0,155));screen.blit(overlay,(0,0))
        label="DÉFAITE • R pour recommencer" if game.phase=="game-over" else "PAUSE • P pour reprendre"
        screen.blit(large.render(label,True,WHITE),(WIDTH//2-220,HEIGHT//2-25))

def click(pos):
    global selected,message
    x,y=pos
    if x>=WIDTH:
        for name,rect in buttons.items():
            if rect.collidepoint(x,y):selected=name;message=f"Tour sélectionnée : {name}";return
        return
    for tower in game.towers:
        if (tower.x-x)**2+(tower.y-y)**2 < 25**2:
            cost=upgrade_cost(tower.level) if tower.level<4 else None
            if game.upgrade(tower):message=f"Tour niveau {tower.level} achetée."
            else:message="Niveau max ou pièces insuffisantes." if cost else "Niveau max."
            return
    if game.place(x,y,selected):message=f"{selected} placée."
    else:message="Terrain interdit ou pièces insuffisantes."

running=True
while running:
    dt=clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type==pygame.QUIT:running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:running=False
            elif event.key==pygame.K_r:game=Game();paused=False;message="Nouvelle partie."
            elif event.key==pygame.K_p:paused=not paused
            elif event.key==pygame.K_SPACE:
                if game.start_wave():message="Vague lancée."
            elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                selected=list(TOWERS)[event.key-pygame.K_1]
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and not paused and game.phase!="game-over":
            click(event.pos)
    if not paused:game.step(dt)
    draw()
    pygame.display.flip()
pygame.quit()
sys.exit()
