# Tower Defense v2 : économie et vagues

Version jouable remplaçant l'ancien prototype gratuit. Ancien code conservé tel quel sous `tower-defense/legacy_main.py`, entrée courante `tower-defense/main.py`.

## Installer et jouer
```bash
python -m pip install pygame
cd tower-defense
python main.py
```

- **1 / 2 / 3** : choisir canon, sniper ou tour de gel ; clic sur la carte pour acheter et placer.
- **Clic sur une tour** : payer une amélioration jusqu'au niveau 4.
- **Espace** : lancer la vague suivante quand le terrain est prêt.
- **P** : pause/reprise, **R** : recommencer, **Échap** : sortir.
- Tours interdites sur le chemin et trop près d'une autre tour.
- Pièces au départ : 200 ; les ennemis tués et les vagues terminées rapportent des pièces, les fuites coûtent des vies. Défaite à zéro vie.
- Trois espèces d'ennemis courants et boss toutes les cinq vagues. Boss généré **une seule fois par vague**. Leurs points de vie progressent avec la difficulté. Les tours ciblent l'ennemi le plus avancé.
- La tour de gel ralentit, le sniper frappe fort et lentement, le canon est polyvalent.

## Architecture
`tower-defense/rules.py` contient le moteur sans dépendance graphique : cheminements exacts, placement, économie, niveaux, vagues, ciblage, dégâts, ralentissement. `main.py` n'est plus qu'un écran Pygame et le pilotage. Le moteur permet des essais de balance reproductibles.

## Équilibrage
`python tools/balance_tower_defense.py` exécute trois stratégies déterministes (sans tours, quatre positions fixes et quatre positions avec améliorations) et affiche vagues survécues, fuites, victimes, score et pièces (sans lancer Pygame). Une stratégie basique **n'est pas une stratégie optimale** : utiliser ces mesures comme indicateur et faire tester plusieurs styles, puis ajuster les coûts, la puissance et les phases. L'amélioration doit être calibrée par des parties manuelles et des scénarios de référence.

## Tests et reprise Codex
`python -m unittest discover -s tests -p "test_tower_defense.py" -v`. La CI inclut aussi la compilation de `tower-defense/main.py` et du moteur sans ouvrir de fenêtre. Tester ensuite une vraie session Pygame localement. Non testé graphiquement lors de la création.

Prochaines fonctionnalités de valeur : prévisualisation fantôme de placement, niveau de difficulté adaptatif plafonné, styles de tourelles, sélections d'ennemis, cartes de chemins alternatives, journal détaillé de balance et sauvegarde méta si consentie. Ne pas supprimer `legacy_main.py` sans directive de l'utilisateur ; ne pas prétendre que les métriques déterministes garantissent un jeu équilibré.

### Résultats mesurés sur les 8 premières vagues (CI, 2026-10-29)

| Stratégie | Vague atteinte | Vies restantes | Ennemis tués | Fuites | Pièces |
| --- | ---: | ---: | ---: | ---: | ---: |
| Aucune tour | 3 | 0 | 0 | 20 | 245 |
| 4 positions, sans amélioration | 8 | 0 | 90 | 13 | 1016 |
| 4 positions, améliorations progressives | 9 | 15 | 104 | 1 | 393 |

**Lecture** : sans tours, défaite rapide ; avec tours basiques, difficulté croissante ; avec améliorations, meilleur résultat mais coût réel sur la trésorerie. Stratégies fixes, pas d'optimisation, métriques déterministes issues de `tools/balance_tower_defense.py` et de la [CI](https://github.com/goldaj/python-game-prototypes/actions/runs/40851171246). Cela ne prouve pas un équilibrage final ; test joueur et stratégies diverses requis.
