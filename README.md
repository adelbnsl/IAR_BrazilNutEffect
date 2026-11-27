
# IAR — Brazil Nut Effect

## Présentation

Projet réalisé dans le cadre de l'UE IAR (Intelligence Artificielle et Robotique) du Master AI2D à Sorbonne Université.

L'objectif est de reproduire en simulation le phénomène de ségrégation collective décrit dans l'article :

**Segregation in Swarms of e-puck Robots Based on the Brazil Nut Effect**

J. Chen, M. Gauci, M. J. Price et R. Groß — AAMAS 2012.

Article : http://www.ifaamas.org/Proceedings/aamas2012/papers/4A_4.pdf

## Objectif

Simuler un essaim de robots mobiles qui s'organisent collectivement selon leur rayon virtuel.

Les robots utilisent des interactions locales, sans contrôle centralisé, afin de faire émerger une séparation spatiale entre deux groupes :

- Petits rayons virtuels : davantage vers le centre.
- Grands rayons virtuels : davantage vers la périphérie.

## Organisation du projet

- `src/` : code des robots, du contrôleur et de la simulation.
- `experiments/` : scripts des expériences.
- `results/` : données et graphiques obtenus.
- `tests/` : tests du simulateur.
- `main.py` : point d'entrée du programme.

## Installation

### 1. Créer un environnement virtuel

```powershell
python -m venv .venv
```

### 2. Activer l'environnement (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
python -m pip install -r requirements.txt
```

## Exécution

Une fois la simulation implémentée :

```powershell
python main.py
```

## État du projet

En cours de développement.

## Référence scientifique

Chen, J., Gauci, M., Price, M. J., & Groß, R. (2012).
*Segregation in Swarms of e-puck Robots Based on the Brazil Nut Effect.*
Proceedings of AAMAS 2012.

## Configuration

Tous les paramètres de l'expérience sont regroupés dans `src/config.py` (valeurs par défaut, avec unité et description) et dans `config.json` à la racine, chargé automatiquement. Ce fichier peut être partiel : les paramètres absents gardent leur valeur par défaut. Les clés qui commencent par `_` sont ignorées (pour ajouter des commentaires).

| Section | Contenu |
|---|---|
| `arene` | côté de l'arène |
| `robot` | rayon physique, entraxe des roues |
| `controleur` | poids attraction / répulsion / bruit, gain et vitesses |
| `simulation` | pas de temps `dt`, itérations et tolérance de collision |
| `groupes` | nombre de robots, rayon de base, effectifs (null : équation 4 de l'article) |
| `placement` | grille de départ |
| `experience` | valeurs de b, nombre d'essais, durée, graine |
| `visualisation` | b, vitesse de l'animation pour `main.py` |

```bash
python main.py --afficher-config                          # tous les paramètres, valeurs, unités, descriptions
python main.py --config configs/ancien_main.json          # autre fichier de configuration
python main.py --set controleur.poids_aleatoire=0.6 --set visualisation.b=2
python experiments/run_experiments.py --b 2 3 --essais 5 --duree 300
python experiments/run_experiments.py --set groupes.effectifs=[10,10] --sortie results/essai_10_10
```

Priorité : valeurs par défaut < `config.json` (ou `--config`) < options `--b/--essais/--duree/--graine` < `--set`.
Les fautes de frappe et les valeurs incohérentes sont refusées avec un message explicite. Chaque exécution de `run_experiments.py` copie les paramètres utilisés dans `results/parametres.json`.

Configurations d'exemple dans `configs/` : `ancien_main.json` (10 + 10 robots, rayons 0,10 m et 0,15 m) et `bruit_fort.json`.

## Contrôleur fidèle à l'article

Deux contrôleurs sont disponibles, au choix avec `controleur.mode` :

- `"simple"` (défaut) : le contrôleur du projet, continu, avec les paramètres de la section `[controleur]`.
- `"article"` : `ControleurArticle` (`src/controller.py`), qui suit la section 2.2 de l'article, avec les paramètres de la section `[article]`.

Le contrôleur `"article"` répète un cycle de 5 s, synchrone pour tous les robots : scan de 2,4 s (le robot est immobile), rotation de 1,3 s vers la direction choisie, puis avance de 1,3 s. La direction est choisie une fois par cycle : attraction (unitaire) + bruit pondéré par 0,6 (conservé tout le cycle) + répulsion `k (2r - d)` avec k = 0,2, plafonnée à 6,4. La vitesse est proportionnelle à la norme du vecteur (12,8 cm/s au maximum).

```bash
python main.py --config configs/article.json                       # animation
python experiments/run_experiments.py --set controleur.mode=article  # protocole de l'article
```

Hypothèse à vérifier : l'article ne donne pas l'unité de `2r - d` ; le code suppose des centimètres.
Différence restante : la perception est exacte (pas de robots fusionnés ni masqués par la caméra).
