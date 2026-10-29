# Agent instructions — Python Games

**Lire README.md puis docs/CHATGPT_PROJECT_HISTORY.md avant chaque changement.**

Projet : Collection de 7 prototypes Python autonomes : Poste-Slime, Pixel Patchwork, Pong, Frog Crossing, Maze Roguelite, Endless Platformer et Tower Defense.

Règles : Conserver les dossiers de chaque jeu et leurs attributions ; commandes à exécuter dans chaque sous-dossier. Ne pas déclarer les jeux finalisés.

Préserver la provenance et ne jamais écraser les versions existantes. Documenter ce qui a réellement été testé. Après chaque modification, enrichir docs/CHATGPT_PROJECT_HISTORY.md si une instruction, décision ou nouveau dialogue pertinent est disponible ; séparer citations exactes des résumés et noter les dates seulement si certaines. Ne publier ni secrets ni données privées.

## Tower Defense v2 (2026-10-29)

Lire `tower-defense/README.md`. L'ancien jeu se trouve dans `tower-defense/legacy_main.py`; l'entrée active est `tower-defense/main.py`, avec moteur indépendant `tower-defense/rules.py`. Maintenir des tests purs sans interface et un benchmark de stratégie via `tools/balance_tower_defense.py`. Corriger l'équilibrage sur mesures puis test manuel, sans présumer de l'expérience du joueur. Ne pas supprimer les autres jeux.
