# Prototypes de jeux Python

Une collection d’explorations de gameplay et d’interfaces : ce sont des prototypes, avec des fonctionnalités et une qualité variables. Plusieurs versions ont été développées avec l’aide d’une IA ; les attributions présentes dans les sources sont conservées.

| Prototype | Piste explorée | Exécution |
| --- | --- | --- |
| `poste-slime/` | Livraison, exploration et objets définis en JSON — version v3d | `python main.py` |
| `pixel-patchwork/` | Placement, rotation et combinaison de pièces — version v2d | `python main.py` |
| `pong/` | Pong et collisions entre balle et raquettes | `python pong.py` |
| `frog-crossing/` | Jeu de traversée avec interface Tkinter | `python main.py` |
| `maze-roguelite/` | Labyrinthe procédural, ennemis et objets | `python main.py` |
| `endless-platformer/` | Plateformes générées par segments et déplacement avec inertie | `python main.py` |
| `tower-defense/` | Vagues d’ennemis, tours et projectiles | `python main.py` |

Les commandes se lancent depuis le dossier du prototype. Installer Python 3 et, pour les jeux Pygame, `python -m pip install pygame` ou les dépendances du `requirements.txt` correspondant. Tkinter dépend de l’installation Python.

Les ressources nécessaires aux variantes Poste-Slime et Pixel Patchwork accompagnent leurs sources. Les autres explorations dessinent leurs éléments dans le code. Les sauvegardes personnelles et environnements de développement restent locaux.

État de validation : analyse syntaxique des fichiers Python lors de l’import ; les sessions de jeu complètes, l’équilibrage, les performances et la compatibilité sur différentes machines restent à vérifier. Ces prototypes ne constituent pas des jeux finalisés.

Les deux copies locales de Poste-Slime v3d étaient identiques pour le code et les contenus JSON ; elles sont représentées par un seul dossier ici. Les autres projets existants sur GitHub ont été comparés avant l’import pour éviter de créer des copies de dépôts.
