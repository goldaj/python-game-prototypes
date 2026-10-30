# Contre-audit GitHub et passation — Python Game Prototypes (30 octobre 2026)

Source : lecture effective des refs (3), PR (2) et arborescence GitHub. Aucun des jeux n'a été lancé durant la passe.

## Branches
- `main` : `c9af0583b39979a6fc2de0f47c959c7edcc03f98` (référence).
- `chatgpt/review-20261024` : behind, 0 commit(s) exclusif(s), 8 derrière. Déjà intégrée, candidate nettoyage après contrôle de dépendance.
- `feat/tower-defense-economy-waves-20261029` : behind, 0 commit(s) exclusif(s), 1 derrière. Déjà intégrée, candidate nettoyage après contrôle de dépendance.

## PR
- [#2](https://github.com/goldaj/python-game-prototypes/pull/2) : closed, fusionnée — feat: full tower defense economy, wave progression and measured balancing
- [#1](https://github.com/goldaj/python-game-prototypes/pull/1) : closed, fusionnée — [ChatGPT] Vérification hors-ligne des sept prototypes de jeux

## Fichiers racine
`.github`, `.gitignore`, `AGENTS.md`, `README.md`, `docs`, `endless-platformer`, `frog-crossing`, `maze-roguelite`, `pixel-patchwork`, `pong`, `poste-slime`, `tests`, `tools`, `tower-defense`.

## Tests/risques fonctionnels
1. Tester chacun des prototypes séparément : installation, commandes d'entrée, boucle de jeu, sauvegardes éventuelles et fermeture sans erreur.
2. Pour le tower defense, mesurer économie, coût/rendement des tours, vagues, difficulté des premiers niveaux et stratégie dominante ; ne pas prendre l'existence de tests pour un équilibrage pertinent.
3. Contrôler les imports transversaux pour empêcher un prototype de casser les autres ; tests headless et session manuelle.
4. Réduire la friction d'exécution sur poste Windows/PyCharm et noter les dépendances minimales.
5. Les deux branches secondaires sont déjà comprises dans main ; aucune fusion supplémentaire nécessaire en l'état. Vérifier les workflows avant supprimer.
