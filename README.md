
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
