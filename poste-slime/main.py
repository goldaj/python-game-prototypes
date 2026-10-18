
import os, sys, math, random, json, time
import pygame

W, H = 1280, 720
FPS = 60
PAL = {"encre_sombre": (46,42,39), "encre_brune": (111,90,82), "or_postal": (230,195,106), "menthe": (168,196,174), "corail": (242,169,160)}

def clamp(x,a,b): return a if x<a else b if x>b else x
def norm(v): x,y=v; l=(x*x+y*y)**0.5; return (0,0) if l==0 else (x/l,y/l)
def dist(a,b): return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5

pygame.mixer.pre_init(44100, -16, 1, 256)
pygame.init()
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Poste-Slime — POC (Pygame v3d)")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def img(n):
    p = os.path.join(BASE_DIR, "assets","img",n)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Asset manquant: {p}")
    return pygame.image.load(p).convert_alpha()

SLIME_FR = [img("slime_0.png"), img("slime_1.png"), img("slime_2.png")]
ENEMY = [img("enemy_owl.png"), img("enemy_crab.png"), img("enemy_mole.png"), img("enemy_runner.png")]
HOUSES = [img(fn) for fn in sorted(os.listdir(os.path.join(BASE_DIR,"assets","img")) ) if fn.startswith("house_")]
TILE = img("tile_paper.png"); TILE_ROAD=img("tile_road.png"); TILE_SIDE=img("tile_sidewalk.png")
DOOR=img("door.png"); MAIL=img("mailbox.png"); ARROW=img("arrow.png"); CARD=img("card.png")
CHECK=img("check.png"); CROSS=img("cross.png")

def snd(name):
    try:
        return pygame.mixer.Sound(os.path.join(BASE_DIR,"assets","sfx",name+".wav"))
    except Exception:
        class N: 
            def play(self,*a,**k): pass
        return N()
boing=snd("boing"); schplaf=snd("schplaf"); stamp=snd("stamp")

FONT = pygame.font.SysFont("Segoe UI,Arial", 20); FONT_S = pygame.font.SysFont("Segoe UI,Arial", 16); FONT_L=pygame.font.SysFont("Segoe UI,Arial", 28, bold=True)

class Slime:
    def __init__(self,x,y,m): self.x=x; self.y=y; self.m=m; self.r=8+m**0.5*0.4; self.t=0
class EnemyObj:
    def __init__(self,x,y,tex): self.x=x; self.y=y; self.tex=tex; self.hp=80; self.t=random.random()*6.28
class HouseObj:
    def __init__(self,x,y,tex):
        self.tex=tex; self.rect=tex.get_rect(topleft=(x,y)); self.door=(x+tex.get_width()//2, y+tex.get_height()-18)
        self.visited=False; self.needs=False; self.done=False

class Game:
    def __init__(self):
        self.bg=pygame.Surface((W,H))
        # tile
        for y in range(0,H,256):
            for x in range(0,W,256): self.bg.blit(TILE,(x,y))
        rr=[pygame.Rect(0,H//2-60,W,120), pygame.Rect(W//2-60,0,120,H)]
        for r in rr:
            for y in range(r.top,r.bottom,256):
                for x in range(r.left,r.right,256): self.bg.blit(TILE_ROAD,(x,y))
        for r in [pygame.Rect(0,H//2-80,W,20), pygame.Rect(0,H//2+60,W,20), pygame.Rect(W//2-80,0,20,H), pygame.Rect(W//2+60,0,20,H)]:
            for y in range(r.top,r.bottom,128):
                for x in range(r.left,r.right,128): self.bg.blit(TILE_SIDE,(x,y))

        self.sl=[Slime(W*0.15,H*0.5,100)]
        self.en=[EnemyObj(random.uniform(60,W-60), random.uniform(60,H-60), random.choice(ENEMY)) for _ in range(6)]
        self.houses=[]
        places=[(140,120),(420,100),(720,110),(980,130),(140,460),(420,480),(720,470),(980,490)]
        for p in places: self.houses.append(HouseObj(p[0],p[1], random.choice(HOUSES)))
        need=random.sample(self.houses, 4)
        for h in need: h.needs=True
        self.bag=len(need); self.done=0; self.target=len(need)
        self.speed=180.0; self.wave=1.0
        self.mode="play"; self.msg=""; self.msg_t=0; self.cards=[]; self.reroll=False

        # load timbres
        self.db={}
        base=os.path.join(BASE_DIR,"content","items","timbres")
        if os.path.isdir(base):
            for fn in os.listdir(base):
                if fn.endswith(".json"):
                    with open(os.path.join(base,fn),"r",encoding="utf-8") as f: self.db[fn]=json.load(f)

    def lead(self): return self.sl[0]
    def toast(self, txt, dur=2): self.msg=txt; self.msg_t=dur
    def split(self):
        if len(self.sl)>=6: return
        m=sum(s.m for s in self.sl); 
        if m<=12: return
        a=max(6,int(m*0.5)); b=m-a; x,y=self.lead().x,self.lead().y
        self.sl=[Slime(x,y,a), Slime(x+12,y,b)]; schplaf.play()
    def fuse(self):
        if len(self.sl)<2: return
        m=sum(s.m for s in self.sl); x,y=self.lead().x,self.lead().y
        r=16+m**0.5*4; dmg=(4+m*0.3)*self.wave
        kept=[]
        for e in self.en:
            if (e.x-x)**2+(e.y-y)**2<=r*r: e.hp-=dmg
            if e.hp>0: kept.append(e)
        self.en=kept; self.sl=[Slime(x,y,m)]; stamp.play()
    def interact(self):
        near=min(self.houses, key=lambda h: dist((self.lead().x,self.lead().y), h.door)) if self.houses else None
        if near and dist((self.lead().x,self.lead().y), near.door)<40:
            near.visited=True
            if near.needs and not near.done:
                if self.bag>0: near.done=True; self.bag-=1; self.done+=1; stamp.play(); self.open_cards()
                else: self.toast("Sac vide !")
            else: self.toast("Aucune livraison ici.")
        else: self.toast("Personne ne répond.")
    def open_cards(self):
        self.mode="upgrade"; pool=list(self.db.values()); random.shuffle(pool); self.cards=pool[:3]; self.reroll=False
    def apply(self, card):
        for eff in card.get("effects", []):
            if eff["stat"]=="speed_mult": self.speed *= float(eff["value"])
            if eff["stat"]=="hp_mult":
                for s in self.sl: s.m=int(s.m*float(eff["value"])); s.r=8+s.m**0.5*0.4
            if eff["stat"]=="wave_mult": self.wave *= float(eff["value"])
        self.mode="play"
        if self.done>=self.target: self.mode="win"; self.toast("Tournée terminée !")
    def update(self, dt, keys, mouse, keydown, wheel):
        if self.mode!="play": return
        l=self.lead(); dx=(keys[pygame.K_d]-keys[pygame.K_a] or keys[pygame.K_RIGHT]-keys[pygame.K_LEFT]); dy=(keys[pygame.K_s]-keys[pygame.K_w] or keys[pygame.K_DOWN]-keys[pygame.K_UP])
        vx,vy=norm((dx,dy)); l.x=clamp(l.x+vx*180*dt,0,W); l.y=clamp(l.y+vy*180*dt,0,H)
        for s in self.sl: s.t=(s.t+dt*4)%3
        for h in self.houses:
            if h.rect.collidepoint(l.x,l.y):
                left=l.x-h.rect.left; right=h.rect.right-l.x; top=l.y-h.rect.top; bottom=h.rect.bottom-l.y
                m=min(left,right,top,bottom)
                if m==left: l.x=h.rect.left-1
                elif m==right: l.x=h.rect.right+1
                elif m==top: l.y=h.rect.top-1
                else: l.y=h.rect.bottom+1
        for e in self.en:
            e.t+=dt; ax,ay=math.cos(e.t*1.1), math.sin(e.t*1.3); l2=(ax*ax+ay*ay)**0.5 or 1; e.x=clamp(e.x+ax/l2*60*dt,60,W-60); e.y=clamp(e.y+ay/l2*60*dt,60,H-60)
        if mouse[0] or keys[pygame.K_e]: self.split()
        if mouse[2] or keys[pygame.K_r]: self.fuse()
        if keydown==pygame.K_f: self.interact()
        if self.msg_t>0: self.msg_t-=dt
    def draw(self):
        screen.blit(self.bg,(0,0))
        for h in self.houses:
            screen.blit(h.tex, (h.rect.x, h.rect.y))
            screen.blit(DOOR, DOOR.get_rect(center=(h.door[0], h.door[1]-24)))
            if h.visited:
                badge = CHECK if h.done else (MAIL if h.needs else CROSS)
                screen.blit(badge, badge.get_rect(center=(h.door[0], h.door[1]-56)))
        for e in self.en: screen.blit(e.tex, e.tex.get_rect(center=(e.x,e.y)))
        for s in self.sl:
            idx=int(s.t)%3; screen.blit(SLIME_FR[idx], SLIME_FR[idx].get_rect(center=(s.x,s.y)))
        hud = FONT.render(f"Livraisons: {self.done}/{self.target}  •  Sac: {self.bag}", True, PAL["encre_sombre"]); screen.blit(hud, (16,12))
        help1 = FONT_S.render("ZQSD/WASD bouger • F = Sonner • E : split • R : fusion", True, PAL["encre_sombre"]); screen.blit(help1,(16,H-26))
        if self.mode=="win":
            overlay=pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((0,0,0,160)); screen.blit(overlay,(0,0))
            done=FONT_L.render("Tournée terminée — Bravo facteur !", True, (244,237,227)); screen.blit(done,(W/2-done.get_width()/2,H/2-done.get_height()/2))

def wrap_text(text, font, max_width): pass

def main():
    g=Game(); running=True; wheel=0; keydown=None
    while running:
        dt = clock.tick(FPS)/1000.0; wheel=0; keydown=None
        keys=pygame.key.get_pressed()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.KEYDOWN: keydown=ev.key
        mouse=pygame.mouse.get_pressed(3)
        g.update(dt, keys, mouse, keydown, wheel); g.draw(); pygame.display.flip()
    pygame.quit()

if __name__=="__main__": main()
