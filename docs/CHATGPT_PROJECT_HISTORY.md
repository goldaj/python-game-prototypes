# Historique de projet ChatGPT — Python Games

Archive de transmission à Codex créée le 2026-10-24, **non exhaustive**. Aucun export intégral des anciens échanges n'est disponible dans cette session.

## Périmètre vérifié dans README.md
Collection de 7 prototypes Python autonomes : Poste-Slime, Pixel Patchwork, Pong, Frog Crossing, Maze Roguelite, Endless Platformer et Tower Defense.

## Règles de reprise
Conserver les dossiers de chaque jeu et leurs attributions ; commandes à exécuter dans chaque sous-dossier. Ne pas déclarer les jeux finalisés.

## Échanges attestés
- **2026-10-18** — Assistant (résumé reconstruit, non verbatim) : regroupement d'archives d'apprentissage/prototypes dans des dépôts distincts, conservation de la provenance et documentation honnête du niveau de validation.
- **2026-10-18 13:24:13 UTC** — Utilisateur (extrait verbatim) : « N'écrase aucun repo existant. »
- **2026-10-24** — Utilisateur (résumé reconstruit, non verbatim) : demande un AGENTS.md propre au dépôt, un historique lisible par Codex avec messages utilisateur/assistant et horodatages disponibles, ainsi qu'une mise à jour récurrente de la documentation.

## Limites et maintenance
Les transcriptions exactes des échanges précédents et leurs horaires ne sont pas disponibles ici ; aucune réponse de l'assistant n'a été inventée. Lorsque le propriétaire fournit des exports authentiques, conserver la distinction rôle/date/texte et vérifier les informations sensibles avant commit. Ajouter les nouveaux échanges sourcés en fin de document, sans réécrire le passé.

## 2026-10-29 : évolution Tower Defense

Utilisateur (verbatim, heure précise indisponible) : « Je ne te demande pas de créer une tâche planifiée qui continue chaque jour. Je te demande de continuer maintenant en boucle et de ne pas t'arrêter sur juste 3 améliorations alors qu'il y a plus de 40 repo et plusieurs améliorations possibles par repo ».

Assistant (résumé non verbatim) : sélection du prototype Tower Defense après examen des jeux. Nouvelle économie, trois tours, vagues, boss non infini, cheminement déterministe, ciblage, état de défaite ; conservation de l'ancien code dans `tower-defense/legacy_main.py`. Tests purs et outil d'équilibrage ajoutés ; validation graphique Pygame encore nécessaire. Lire `tower-defense/README.md`.
