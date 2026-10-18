
import os, sys, json, math, random
import pygame

W, H = 1280, 800
FPS = 60
GRID = 16
CELL = 28
GRID_W = GRID*CELL
GRID_H = GRID*CELL
MARGIN_LEFT = 40
MARGIN_TOP = 120
SIDEBAR_X = MARGIN_LEFT + GRID_W + 24
SIDEBAR_W = 360

PAL = {
    "bg": (234,216,200),
    "paper": (244,237,227),
    "mint": (168,196,174),
    "coral": (242,169,160),
    "lav": (200,184,232),
    "gold": (230,195,106),
    "ink": (46,42,39),
    "ink2": (111,90,82),
    "grid": (210,192,176),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
META_PATH = os.path.join(BASE_DIR, "meta.json")

pygame.mixer.pre_init(44100,-16,1,256)
pygame.init()
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Pixel Patchwork — PRO v2c")
clock = pygame.time.Clock()

def img(n): return pygame.image.load(os.path.join(BASE_DIR,"assets","img",n)).convert_alpha()
TILE = img("tile_paper.png"); PANEL_HEADER = img("panel_header.png"); PANEL_SIDEBAR = img("panel_sidebar.png"); PANEL_CENTER = img("panel_center.png")
CARD = img("card.png")
BTN_PRIMARY = img("btn_primary.png"); BTN_LARGE = img("btn_large.png")
ICO_PLACE = img("ico_place.png"); ICO_REROLL = img("ico_reroll.png"); ICO_RESTART = img("ico_restart.png"); ICO_BACK = img("ico_back.png")
CHIP = {c: img(f"chip_{c}.png") for c in ("mint","coral","lav","gold")}

def snd(name):
    try:
        s=pygame.mixer.Sound(os.path.join(BASE_DIR,"assets","sfx",name+".wav")); s.set_volume(0.7); return s
    except Exception:
        class N: 
            def play(self,*a,**k): pass
        return N()
S_PLACE=snd("place"); S_INV=snd("invalid"); S_SCORE=snd("score"); S_CARD=snd("card")

FONT = pygame.font.SysFont("Segoe UI, Arial, Roboto", 20)
FONT_L = pygame.font.SysFont("Segoe UI, Arial, Roboto", 26, bold=True)
FONT_XL = pygame.font.SysFont("Segoe UI, Arial, Roboto", 36, bold=True)

def load_meta():
    try:
        with open(META_PATH,"r",encoding="utf-8") as f: return json.load(f)
    except: return {"stability":0, "pinned_shapes":[], "pinned_colors":[], "unlocks":{}}
def save_meta(m):
    try:
        with open(META_PATH,"w",encoding="utf-8") as f: json.dump(m,f,ensure_ascii=False,indent=2)
    except: pass

# Base shapes (without I5)
SHAPES_BASE = {
    "I3": [(0,0),(1,0),(2,0)],
    "I4": [(0,0),(1,0),(2,0),(3,0)],
    "L3": [(0,0),(0,1),(1,1)],
    "L4": [(0,0),(0,1),(0,2),(1,2)],
    "T": [(0,0),(1,0),(2,0),(1,1)],
    "S": [(1,0),(2,0),(0,1),(1,1)],
    "Z": [(0,0),(1,0),(1,1),(2,1)],
    "O": [(0,0),(1,0),(0,1),(1,1)],
    "P": [(0,0),(1,0),(0,1),(0,2)],
    "Dot2": [(0,0),(1,0)],
}

COLORS=["mint","coral","lav","gold"]

def rotate(points):
    pts=[(y,-x) for (x,y) in points]
    minx=min(p[0] for p in pts); miny=min(p[1] for p in pts)
    return [(x-minx, y-miny) for (x,y) in pts]

def flip(points):
    pts=[(-x,y) for (x,y) in points]
    minx=min(p[0] for p in pts); miny=min(p[1] for p in pts)
    return [(x-minx, y-miny) for (x,y) in pts]

class Piece:
    def __init__(self, shape, color, points):
        self.shape=shape; self.points=points[:]  # points provided by Game (fixes KeyError)
        self.color=color; self.rot=0
    def rotated(self):
        pts=self.points[:]
        for _ in range(self.rot%4): pts=rotate(pts)
        return pts
    def draw_preview(self, surf, gx, gy, valid):
        for (x,y) in self.rotated():
            ix = int(MARGIN_LEFT + (gx+x)*CELL); iy=int(MARGIN_TOP+(gy+y)*CELL)
            r=pygame.Rect(ix+2,iy+2,CELL-4,CELL-4)
            a=200 if valid else 90
            s=pygame.Surface((r.w,r.h), pygame.SRCALPHA); s.fill((*PAL[self.color],a))
            pygame.draw.rect(s, PAL["ink2"], pygame.Rect(0,0,r.w,r.h), width=2, border_radius=6)
            surf.blit(s,(r.x,r.y))

class Grid:
    def __init__(self, meta):
        self.cells=[[None for _ in range(GRID)] for _ in range(GRID)]
        self.score=0
        self.line_bonus=1.0; self.square_bonus=1.0
        self.meta = meta
        self.journal=[]; self.mono_lines_this_run=0; self.squares2x2_this_run=0
        self.mono_bonus_unlocked = meta.get("unlocks",{}).get("mono_plus", False)
    def can_place(self,piece,gx,gy):
        for (x,y) in piece.rotated():
            ix=gx+x; iy=gy+y
            if ix<0 or iy<0 or ix>=GRID or iy>=GRID: return False
            if self.cells[iy][ix] is not None: return False
        return True
    def place(self,piece,gx,gy):
        for (x,y) in piece.rotated():
            ix=gx+x; iy=gy+y; self.cells[iy][ix]=piece.color
        S_PLACE.play(); self.compute_scoring()
    def compute_scoring(self):
        gained=0
        # rows
        for y in range(GRID):
            if all(self.cells[y][x] for x in range(GRID)):
                arr=[self.cells[y][x] for x in range(GRID)]
                mono=all(c==arr[0] for c in arr)
                add=int(100*self.line_bonus)+(50 if mono else 0)
                if mono and self.mono_bonus_unlocked: add += 50
                gained+=add; self.journal.append(f"Ligne {'mono ' if mono else ''}+{add}")
                if mono: self.mono_lines_this_run += 1
        # cols
        for x in range(GRID):
            if all(self.cells[y][x] for y in range(GRID)):
                arr=[self.cells[y][x] for y in range(GRID)]
                mono=all(c==arr[0] for c in arr)
                add=int(100*self.line_bonus)+(50 if mono else 0)
                if mono and self.mono_bonus_unlocked: add += 50
                gained+=add; self.journal.append(f"Col {'mono ' if mono else ''}+{add}")
                if mono: self.mono_lines_this_run += 1
        # 2x2
        squares=0
        for y in range(GRID-1):
            for x in range(GRID-1):
                c=self.cells[y][x]
                if c and self.cells[y][x+1]==c and self.cells[y+1][x]==c and self.cells[y+1][x+1]==c:
                    add=int(30*self.square_bonus); gained+=add; squares+=1
        if squares>0: self.journal.append(f"{squares} carré(s) +{squares*int(30*self.square_bonus)}")
        self.squares2x2_this_run += squares
        if gained>0: S_SCORE.play()
        self.score+=gained
        self.journal=self.journal[-7:]

class Offer:
    def __init__(self,pieces):
        self.pieces=pieces; self.sel=0; self.reroll_used=False

UPCARDS=[
    {"id":"line_bonus","name":"Fil droit","+":"+25% Lignes","apply": lambda g: setattr(g.grid,"line_bonus", g.grid.line_bonus*1.25)},
    {"id":"square_bonus","name":"Patch serré","+":"+25% Carrés","apply": lambda g: setattr(g.grid,"square_bonus", g.grid.square_bonus*1.25)},
    {"id":"pin_shape","name":"Épingler forme","+":"Ajoute la forme choisie à la méta","apply":"pin_shape"},
    {"id":"pin_color","name":"Palette sûre","+":"Ajoute la couleur choisie à la méta","apply":"pin_color"},
    {"id":"extra_reroll","name":"Coup de fer","+":"1 reroll d'offres suppl.","apply": lambda g: setattr(g.offer, "reroll_used", False)},
]

class UIButton:
    def __init__(self, rect, label, icon=None, action=None):
        self.rect=pygame.Rect(rect); self.label=label; self.icon=icon; self.action=action
    def draw(self, surf):
        surf.blit(BTN_PRIMARY if self.rect.h<=46 else BTN_LARGE, self.rect)
        if self.icon: surf.blit(self.icon, (self.rect.x+10, self.rect.y+5))
        txt = FONT_L.render(self.label, True, PAL["ink"])
        if self.icon:
            surf.blit(txt, (self.rect.x+48, self.rect.y+10))
        else:
            surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y+10))
        # single outline only here
        pygame.draw.rect(surf, PAL["ink2"], self.rect, width=2, border_radius=12)

class Game:
    def __init__(self):
        self.mode="menu"  # menu, unlocked, play, cards, summary
        self.meta=load_meta()
        self.init_run()
        # Buttons
        self.btn_play = UIButton((W//2-230, 360, 200, 56), "Jouer", None, self.start_run)
        self.btn_unlocked = UIButton((W//2+30, 360, 200, 56), "Débloqués", None, self.goto_unlocked)
        self.btn_quit = UIButton((W//2-100, 430, 200, 56), "Quitter", None, self.quit)
        self.btn_restart = UIButton((W-180, 24, 160, 56), "Relancer", ICO_RESTART, self.start_run)
        self.btn_back = UIButton((W//2-100, 560, 200, 56), "Retour", ICO_BACK, self.goto_menu)

    def goto_menu(self): self.mode="menu"
    def goto_unlocked(self): self.mode="unlocked"

    def init_run(self):
        # Build shape dict including unlocks
        self.shapes = dict(SHAPES_BASE)
        if self.meta.get("unlocks",{}).get("shape_I5"):
            self.shapes["I5"] = [(0,0),(1,0),(2,0),(3,0),(4,0)]
        self.grid = Grid(self.meta)
        self.turn=1; self.turns_max=12
        self.seed=random.randint(0,999999); random.seed(self.seed)
        self.offer=self.new_offer(biased=True)
        self.cards=[]; self.card_rects=[]; self.selected_for_pin=None

    def start_run(self):
        self.init_run(); self.mode="play"

    def quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def shape_pool(self): return list(self.shapes.keys())

    def new_offer(self, biased=False):
        offer_size = 4 if self.meta.get("unlocks",{}).get("offer_plus") else 3
        shapes=self.shape_pool(); pieces=[]
        bias_p = min(0.8, 0.3 + 0.1*self.meta.get("stability",0))
        pinned_s=self.meta.get("pinned_shapes",[]); pinned_c=self.meta.get("pinned_colors",[])
        added=False
        for i in range(offer_size):
            s=random.choice(shapes); c=random.choice(COLORS)
            if biased and not added and (pinned_s or pinned_c) and random.random()<bias_p:
                if pinned_s and random.random()<0.6: s=random.choice(pinned_s)
                if pinned_c and random.random()<0.6: c=random.choice(pinned_c)
                added=True
            pieces.append(Piece(s,c,self.shapes[s]))  # pass points explicitly
        return Offer(pieces)

    def select_idx(self,i): 
        if 0<=i<len(self.offer.pieces): self.offer.sel=i

    def rotate_sel(self, steps=1):
        p=self.offer.pieces[self.offer.sel]
        p.rot=(p.rot+steps)%4

    def grid_xy(self, mx,my): return ((mx - MARGIN_LEFT)//CELL, (my - MARGIN_TOP)//CELL)

    def draw(self):
        # BG + header
        for y in range(0,H,256):
            for x in range(0,W,256): screen.blit(TILE,(x,y))
        screen.blit(PANEL_HEADER, (20, 16))
        title=FONT_XL.render("PIXEL PATCHWORK", True, PAL["ink"]); screen.blit(title,(36, 32))

        if self.mode=="menu":
            screen.blit(PANEL_CENTER, (W//2-450, 160))
            lines=[
                "Puzzle chill au tour par tour — Grille 16×16",
                "Choisissez une pièce (1/2/3/4), tournez-la avec la molette, puis placez-la (clic/Poser).",
                "Scores : lignes/colonnes complètes (bonus monochrome), carrés 2×2 monochromes.",
                "Méta : stabilité, épingles et déblocages (Monochrome+, Offre+, forme I5)."
            ]
            y=190
            for s in lines:
                screen.blit(FONT.render("• "+s, True, PAL["ink"]), (W//2-420, y)); y+=32
            self.btn_play.draw(screen); self.btn_unlocked.draw(screen); self.btn_quit.draw(screen)
            return

        if self.mode=="unlocked":
            screen.blit(PANEL_CENTER, (W//2-450, 160))
            t=FONT_XL.render("Améliorations débloquées", True, PAL["ink"]); screen.blit(t,(W//2-t.get_width()//2, 176))
            m=self.meta; u=m.get("unlocks",{})
            entries=[
                ("Monochrome+", "Bonus +50 sup. sur lignes/colonnes monochromes", u.get("mono_plus",False)),
                ("Offre+", "+1 pièce proposée par tour", u.get("offer_plus",False)),
                ("Forme I5", "Nouvelle forme I5 (ligne de 5)", u.get("shape_I5",False)),
            ]
            y=230
            for name,desc,ok in entries:
                col = PAL["ink"] if ok else PAL["ink2"]
                screen.blit(FONT_L.render(("✓ " if ok else "✗ ") + name, True, col),(W//2-400, y)); y+=30
                screen.blit(FONT.render(desc, True, col),(W//2-370, y)); y+=28
            self.btn_back.draw(screen)
            return

        # play/cards/summary layout
        # grid panel
        pygame.draw.rect(screen, PAL["paper"], pygame.Rect(MARGIN_LEFT-12, MARGIN_TOP-12, GRID_W+24, GRID_H+24), border_radius=18)
        pygame.draw.rect(screen, PAL["ink2"], pygame.Rect(MARGIN_LEFT-12, MARGIN_TOP-12, GRID_W+24, GRID_H+24), width=3, border_radius=18)
        # grid
        for y in range(GRID):
            for x in range(GRID):
                px=MARGIN_LEFT+x*CELL; py=MARGIN_TOP+y*CELL
                pygame.draw.rect(screen, PAL["grid"], pygame.Rect(px,py,CELL,CELL), width=1)
        # cells
        self.draw_cells()

        # Sidebar
        screen.blit(PANEL_SIDEBAR, (SIDEBAR_X, MARGIN_TOP))
        self.draw_sidebar()

        # Header infos + restart button
        info=FONT_L.render(f"Tour {self.turn}/{self.turns_max}   Score {self.grid.score}", True, PAL["ink"])
        screen.blit(info,(W//2 - info.get_width()//2, 36))
        self.btn_restart.draw(screen)

        # Placement preview
        if self.mode in ("play","cards"):
            mx,my=pygame.mouse.get_pos(); gx,gy=self.grid_xy(mx,my)
            if 0<=gx<GRID and 0<=gy<GRID:
                p=self.offer.pieces[self.offer.sel]
                p.draw_preview(screen, int(gx), int(gy), self.grid.can_place(p, int(gx), int(gy)))

        if self.mode=="cards": self.draw_cards_overlay()
        if self.mode=="summary": self.draw_summary()

    def draw_cells(self):
        for y in range(GRID):
            for x in range(GRID):
                col=self.grid.cells[y][x]
                if col:
                    px=MARGIN_LEFT+x*CELL; py=MARGIN_TOP+y*CELL
                    r2=pygame.Rect(px+3,py+3,CELL-6,CELL-6)
                    s=pygame.Surface((r2.w,r2.h), pygame.SRCALPHA); s.fill((*PAL[col],255))
                    pygame.draw.rect(s, PAL["ink2"], pygame.Rect(0,0,r2.w,r2.h), width=2, border_radius=6)
                    screen.blit(s,(r2.x,r2.y))

    def draw_sidebar(self):
        bx=SIDEBAR_X; by=MARGIN_TOP
        screen.blit(FONT_L.render("Pièces", True, PAL["ink"]),(bx+16, by+14))
        for i,p in enumerate(self.offer.pieces):
            r=pygame.Rect(bx+16, by+50+i*110, SIDEBAR_W-32, 92)
            pygame.draw.rect(screen, PAL["paper"], r, border_radius=12)
            pygame.draw.rect(screen, PAL["ink2"], r, width=2, border_radius=12)
            if i==self.offer.sel: pygame.draw.rect(screen, PAL["gold"], r, width=4, border_radius=12)
            # mini preview
            sz=16; pts=p.rotated(); w=max(x for x,y in pts)+1; h=max(y for x,y in pts)+1
            offx=(120 - w*sz)//2; offy=(70 - h*sz)//2; gx=r.x+10; gy=r.y+10
            for (x,y) in pts:
                rx=gx+offx+x*sz; ry=gy+offy+y*sz
                pygame.draw.rect(screen, PAL[p.color], pygame.Rect(rx,ry,sz-2,sz-2), border_radius=6)
                pygame.draw.rect(screen, PAL["ink2"], pygame.Rect(rx,ry,sz-2,sz-2), width=1, border_radius=6)
            screen.blit(FONT.render(f"{i+1}. {p.shape}", True, PAL["ink"]),(r.x+140, r.y+12))
            screen.blit(FONT.render("Couleur :", True, PAL["ink"]),(r.x+140, r.y+36))
            screen.blit(CHIP[p.color], (r.x+220, r.y+30))
        # Hint
        hint = FONT.render("Rotation : molette — 4 angles", True, PAL["ink"])
        screen.blit(hint,(bx+16, by+50+len(self.offer.pieces)*110+6))
        # Buttons
        self.btn_place = UIButton((bx+16, by+80+len(self.offer.pieces)*110, 160, 46), "Poser", ICO_PLACE, self.click_place)
        rr_label = "Reroll" + ("" if not self.offer.reroll_used else " (0)")
        self.btn_reroll = UIButton((bx+184, by+80+len(self.offer.pieces)*110, 160, 46), rr_label, ICO_REROLL, self.click_reroll)
        self.btn_place.draw(screen); self.btn_reroll.draw(screen)
        # Journal
        jy = by + 130 + len(self.offer.pieces)*110
        screen.blit(FONT_L.render("Journal de score", True, PAL["ink"]),(bx+16, jy))
        jpanel = pygame.Rect(bx+16, jy+30, SIDEBAR_W-32, 120)
        pygame.draw.rect(screen, PAL["paper"], jpanel, border_radius=10)
        pygame.draw.rect(screen, PAL["ink2"], jpanel, width=2, border_radius=10)
        y=jpanel.y+10
        for line in self.grid.journal[-5:]:
            screen.blit(FONT.render("• "+line, True, PAL["ink"]),(jpanel.x+10, y)); y+=22

    def draw_cards_overlay(self):
        overlay=pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((0,0,0,160)); screen.blit(overlay,(0,0))
        t=FONT_XL.render("Cartes d'amélioration", True, (255,255,255)); screen.blit(t,(W//2-t.get_width()//2, 120))
        if not self.cards:
            pool=UPCARDS[:]; random.shuffle(pool); self.cards=pool[:3]; S_CARD.play()
        cw,ch,gap=300,200,40; x0=W//2-(cw*len(self.cards)+gap*(len(self.cards)-1))//2; y0=240
        self.card_rects=[]
        for i,c in enumerate(self.cards):
            r=pygame.Rect(x0+i*(cw+gap), y0, cw, ch); self.card_rects.append(r)
            screen.blit(CARD, r); pygame.draw.rect(screen, PAL["ink2"], r, width=3, border_radius=18)
            screen.blit(FONT_L.render(c["name"], True, PAL["ink"]),(r.x+20, r.y+20))
            screen.blit(FONT.render(c["+"], True, PAL["ink"]),(r.x+20, r.y+76))
            if c["id"].startswith("pin_") and self.offer.pieces:
                sel = self.offer.pieces[self.offer.sel]
                txt = f"Épingle: {sel.shape if c['id']=='pin_shape' else sel.color}"
                screen.blit(FONT.render(txt, True, PAL["ink"]),(r.x+20, r.y+120))

    def draw_summary(self):
        overlay=pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((0,0,0,170)); screen.blit(overlay,(0,0))
        t=FONT_XL.render("Fin de run", True, (255,255,255)); screen.blit(t,(W//2-t.get_width()//2, 140))
        s=FONT_L.render(f"Score: {self.grid.score}", True, (255,255,255)); screen.blit(s,(W//2-s.get_width()//2, 200))
        # Restart button
        btn = UIButton((W//2-100, 260, 200, 56), "Relancer", ICO_RESTART, self.start_run)
        btn.draw(screen)
        # meta info
        m=load_meta()
        info=FONT.render(f"Stabilité: {m.get('stability',0)}   Épingles formes: {', '.join(m.get('pinned_shapes',[]) or ['—'])}   couleurs: {', '.join(m.get('pinned_colors',[]) or ['—'])}", True, (255,255,255))
        screen.blit(info,(W//2-info.get_width()//2, 320))

    # --- Actions ---
    def click_place(self):
        mx,my=pygame.mouse.get_pos(); gx,gy=self.grid_xy(mx,my)
        if 0<=gx<GRID and 0<=gy<GRID: self.place(int(gx),int(gy))
        else: S_INV.play()
    def click_reroll(self):
        if not self.offer.reroll_used:
            self.offer=self.new_offer(biased=True); self.offer.reroll_used=True; S_CARD.play()

    def apply_card(self, idx):
        c=self.cards[idx]
        if c["id"]=="pin_shape":
            sel=self.offer.pieces[self.offer.sel].shape; m=load_meta(); ps=m.get("pinned_shapes",[])
            if sel not in ps: ps.append(sel); m["pinned_shapes"]=ps[-6:]; save_meta(m)
        elif c["id"]=="pin_color":
            sel=self.offer.pieces[self.offer.sel].color; m=load_meta(); pc=m.get("pinned_colors",[])
            if sel not in pc: pc.append(sel); m["pinned_colors"]=pc[-6:]; save_meta(m)
        elif callable(c["apply"]): c["apply"](self)
        self.mode="play"; self.offer=self.new_offer(biased=True)

    def place(self, gx, gy):
        p=self.offer.pieces[self.offer.sel]
        if not self.grid.can_place(p, gx, gy): S_INV.play(); return
        self.grid.place(p, gx, gy)
        self.turn+=1
        if self.turn in (5,9):
            self.mode="cards"; self.cards=[]
        elif self.turn>self.turns_max:
            self.end_run()
        else:
            self.offer=self.new_offer(biased=True)

    def end_run(self):
        m=load_meta(); u=m.get("unlocks",{})
        if self.grid.mono_lines_this_run >= 2: u["mono_plus"]=True
        if self.grid.squares2x2_this_run >= 3: u["offer_plus"]=True
        if self.grid.score >= 800: u["shape_I5"]=True
        m["unlocks"]=u; m["stability"]=m.get("stability",0)+1; save_meta(m)
        self.meta=m; self.mode="summary"

    def on_click(self, pos):
        if self.mode=="menu":
            for b in (self.btn_play, self.btn_unlocked, self.btn_quit):
                if b.rect.collidepoint(pos): b.action(); return
        if self.mode=="unlocked":
            if self.btn_back.rect.collidepoint(pos): self.btn_back.action(); return
            return
        if self.mode in ("play","cards","summary"):
            if self.btn_restart.rect.collidepoint(pos): self.btn_restart.action(); return
        if self.mode=="cards":
            for i,r in enumerate(self.card_rects):
                if r.collidepoint(pos): self.apply_card(i); return
        if self.mode!="play": return
        # select piece by clicking its card
        bx=SIDEBAR_X; by=MARGIN_TOP
        for i,p in enumerate(self.offer.pieces):
            r=pygame.Rect(bx+16, by+50+i*110, SIDEBAR_W-32, 92)
            if r.collidepoint(pos): self.select_idx(i); return
        # buttons
        for b in (self.btn_place, self.btn_reroll):
            if b.rect.collidepoint(pos): b.action(); return
        # click on grid to place
        mx,my=pos; gx,gy=self.grid_xy(mx,my)
        if 0<=gx<GRID and 0<=gy<GRID: self.place(int(gx),int(gy))

def main():
    g=Game()
    running=True
    while running:
        dt=clock.tick(FPS)/1000.0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE:
                    # navigation only (no app quit)
                    if g.mode=="play": g.mode="menu"
                    elif g.mode=="menu": pass
                    elif g.mode=="unlocked": g.mode="menu"
                    elif g.mode=="cards": g.mode="play"
                    elif g.mode=="summary": g.mode="menu"
                if g.mode=="play":
                    if ev.key in (pygame.K_1, pygame.K_KP1): g.select_idx(0)
                    if ev.key in (pygame.K_2, pygame.K_KP2): g.select_idx(1)
                    if ev.key in (pygame.K_3, pygame.K_KP3): g.select_idx(2)
                    if ev.key in (pygame.K_4, pygame.K_KP4): g.select_idx(3)
                    elif ev.type==pygame.MOUSEWHEEL:
                        if g.mode=="play":
                            # rotate by wheel direction
                            steps = ev.y  # positive up
                            if steps!=0: g.rotate_sel(steps)
            elif ev.type==pygame.MOUSEBUTTONDOWN:
                # Support old-style wheel events 4/5 just in case
                if ev.button in (4,5) and g.mode=="play":
                    g.rotate_sel(1 if ev.button==4 else -1)
                else:
                    g.on_click(ev.pos)
        g.draw()
        pygame.display.flip()
    pygame.quit()

if __name__=="__main__":
    main()
