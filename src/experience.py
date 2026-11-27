"""
Construction d'une simulation à partir des paramètres (utilisée par main.py et par les expériences).
"""

import math
import random

from src.config import Parametres
from src.controller import Controleur, ControleurArticle
from src.robot import Robot
from src.simulation import Simulation


def calculer_effectifs(n, rayons):
    """
    Répartit n robots entre les groupes selon l'équation 4 de l'article :
    n_k proportionnel à (2k - 1) / r_k^2.

    Paramètres :
    n : nombre total de robots.
    rayons : liste des rayons virtuels, du groupe 1 au groupe m.

    Retourne :
    Liste d'effectifs entiers dont la somme vaut n.
    """
    poids = [(2 * (k + 1) - 1) / (r ** 2) for k, r in enumerate(rayons)]
    total = sum(poids)
    effectifs = [round(n * p / total) for p in poids]

    # Corriger l'arrondi sur le groupe le plus nombreux pour que la somme vaille n.
    ecart = n - sum(effectifs)
    effectifs[effectifs.index(max(effectifs))] += ecart
    return effectifs


def tirer_positions_initiales(n, rng, cote_arene=2.5, pas_grille=0.20, taille_grille=6):
    """
    Tire n positions initiales distinctes sur une grille carrée centrée sur la lumière
    (6 x 6 points espacés de 20 cm dans l'article), avec une orientation parmi N, S, E, O.

    Retourne :
    Liste de n tuples (x, y, theta).
    """
    centre = cote_arene / 2
    decalage = (taille_grille - 1) / 2
    points = [
        (centre + (colonne - decalage) * pas_grille, centre + (ligne - decalage) * pas_grille)
        for colonne in range(taille_grille)
        for ligne in range(taille_grille)
    ]
    choisis = rng.sample(points, n)
    orientations = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]
    return [(x, y, rng.choice(orientations)) for (x, y) in choisis]


def creer_simulation(b, graine, parametres=None):
    """
    Crée une simulation prête à être lancée pour un facteur de rayon b.

    Groupe 1 : rayon a. Groupe 2 : rayon a*b (équation 3 de l'article).
    Les effectifs suivent groupes.effectifs s'il est fourni, sinon l'équation 4.

    Paramètres :
    b : facteur de rayon.
    graine : graine du générateur aléatoire (placement initial et bruit du contrôleur).
    parametres : objet Parametres (valeurs par défaut si None).
    """
    p = parametres if parametres is not None else Parametres()

    # Le module random sert au contrôleur, rng au tirage initial : les deux partent de la même graine.
    random.seed(graine)
    rng = random.Random(graine)

    rayons = [p.groupes.rayon_base, p.groupes.rayon_base * b]
    effectifs = p.groupes.effectifs or calculer_effectifs(p.groupes.n_robots, rayons)

    positions = tirer_positions_initiales(
        p.groupes.n_robots, rng, p.arene.cote, p.placement.pas_grille, p.placement.taille_grille
    )

    robots = []
    index = 0
    for numero_groupe, (rayon, effectif) in enumerate(zip(rayons, effectifs), start=1):
        for _ in range(effectif):
            x, y, theta = positions[index]
            robot = Robot(x, y, theta, rayon, groupe=numero_groupe)
            robot.rayon_physique = p.robot.rayon_physique
            robot.distance_roues = p.robot.distance_roues
            robots.append(robot)
            index += 1

    simulation = Simulation(p.arene.cote, p.arene.cote, robots, p.simulation.dt)
    simulation.nb_iterations_collisions = p.simulation.nb_iterations_collisions
    simulation.tolerance_collision = p.simulation.tolerance_collision
    if p.controleur.mode == "article":
        simulation.controleur = ControleurArticle(simulation, p.article)
    else:
        simulation.controleur = Controleur(simulation, p.controleur)
    return simulation
