
import math
import pytest

from src.robot import Robot
from src.simulation import Simulation


def creer_simulation(robots, dt=0.1):
    """
    Crée une simulation de test dans une arène
    de 2.5 m x 2.5 m.
    """
    return Simulation(
        largeur=2.5,
        hauteur=2.5,
        robots=robots,
        dt=dt
    )


def test_initialisation_simulation():
    """Vérifie l'initialisation de la simulation."""

    robot1 = Robot(1.0, 1.0, 0.0, 0.08)
    robot2 = Robot(1.5, 1.5, 0.0, 0.24)

    simulation = creer_simulation([robot1, robot2])

    assert simulation.largeur == 2.5
    assert simulation.hauteur == 2.5
    assert len(simulation.robots) == 2
    assert simulation.dt == pytest.approx(0.1)
    assert simulation.temps == pytest.approx(0.0)

    assert simulation.nb_iterations_collisions == 8
    assert simulation.tolerance_collision == pytest.approx(0.0001)


def test_avancement_temps():
    """Vérifie que le temps avance correctement."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)
    simulation = creer_simulation([robot])

    for _ in range(10):
        simulation.effectuer_pas()

    assert simulation.temps == pytest.approx(1.0)


def test_deplacement_pendant_simulation():
    """Vérifie le déplacement d'un robot pendant la simulation."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.1
    robot.vitesse_droite = 0.1

    simulation = creer_simulation([robot])

    for _ in range(5):
        simulation.effectuer_pas()

    assert robot.x == pytest.approx(1.05)
    assert robot.y == pytest.approx(1.0)
    assert simulation.temps == pytest.approx(0.5)


def test_limites_arene():
    """Vérifie qu'un robot reste dans les limites de l'arène."""

    robot = Robot(-0.3, 2.8, 0.0, 0.08)
    simulation = creer_simulation([robot])

    simulation.gerer_limites(robot)

    assert robot.x == pytest.approx(robot.rayon_physique)
    assert robot.y == pytest.approx(
        simulation.hauteur - robot.rayon_physique
    )


def test_limites_automatiques():
    """Vérifie la correction des limites pendant un déplacement."""

    robot = Robot(2.44, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.2
    robot.vitesse_droite = 0.2

    simulation = creer_simulation([robot])

    for _ in range(5):
        simulation.effectuer_pas()

    assert robot.x == pytest.approx(
        simulation.largeur - robot.rayon_physique
    )

    assert robot.y == pytest.approx(1.0)


def test_detection_collision():
    """Vérifie la détection des collisions."""

    robot1 = Robot(1.0, 1.0, 0.0, 0.08)
    robot2 = Robot(1.05, 1.0, 0.0, 0.24)

    simulation = creer_simulation([robot1, robot2])

    # Distance de 5 cm : collision
    assert simulation.detecter_collision(robot1, robot2) is True

    # Distance de 20 cm : pas de collision
    robot2.x = 1.20

    assert simulation.detecter_collision(robot1, robot2) is False


def test_resolution_collision():
    """Vérifie la correction du chevauchement de deux robots."""

    robot1 = Robot(1.0, 1.0, 0.0, 0.08)
    robot2 = Robot(1.05, 1.0, 0.0, 0.24)

    simulation = creer_simulation([robot1, robot2])

    simulation.resoudre_collision(robot1, robot2)

    distance = math.hypot(
        robot2.x - robot1.x,
        robot2.y - robot1.y
    )

    distance_min = (
        robot1.rayon_physique
        + robot2.rayon_physique
    )

    assert distance == pytest.approx(distance_min, abs=1e-9)
    assert simulation.detecter_collision(robot1, robot2) is False


def test_collision_automatique():
    """Vérifie la collision de deux robots qui se rapprochent."""

    robot1 = Robot(1.0, 1.0, 0.0, 0.08)
    robot2 = Robot(1.20, 1.0, math.pi, 0.24)

    for robot in [robot1, robot2]:
        robot.vitesse_gauche = 0.1
        robot.vitesse_droite = 0.1

    simulation = creer_simulation([robot1, robot2])

    for _ in range(10):
        simulation.effectuer_pas()

    distance = math.hypot(
        robot2.x - robot1.x,
        robot2.y - robot1.y
    )

    distance_min = (
        robot1.rayon_physique
        + robot2.rayon_physique
    )

    assert distance >= distance_min - simulation.tolerance_collision


def test_collisions_trois_robots():
    """Vérifie la correction de plusieurs collisions simultanées."""

    robots = [
        Robot(1.0, 1.0, 0.0, 0.08),
        Robot(1.06, 1.0, 0.0, 0.08),
        Robot(1.12, 1.0, 0.0, 0.08)
    ]

    simulation = creer_simulation(robots)

    simulation.effectuer_pas()

    assert (
        simulation.calculer_chevauchement_max()
        <= simulation.tolerance_collision
    )


def test_collision_deux_robots_mur():
    """Vérifie la correction d'une collision près du mur gauche."""

    robot1 = Robot(0.035, 1.0, 0.0, 0.08)
    robot2 = Robot(0.085, 1.0, 0.0, 0.24)

    simulation = creer_simulation([robot1, robot2])

    simulation.effectuer_pas()

    assert robot1.x >= robot1.rayon_physique
    assert robot2.x >= robot2.rayon_physique

    assert (
        simulation.calculer_chevauchement_max()
        <= simulation.tolerance_collision
    )


def test_collision_trois_robots_mur():
    """Vérifie la correction de trois robots près du mur gauche."""

    robots = [
        Robot(0.035, 1.0, 0.0, 0.10),
        Robot(0.095, 1.0, 0.0, 0.10),
        Robot(0.155, 1.0, 0.0, 0.10)
    ]

    simulation = creer_simulation(robots)

    # Notre expérience a montré que 20 itérations suffisent ici.
    simulation.nb_iterations_collisions = 20

    simulation.effectuer_pas()

    # Vérifier les murs
    for robot in robots:
        assert robot.x >= robot.rayon_physique
        assert robot.x <= simulation.largeur - robot.rayon_physique

    # Vérifier la tolérance
    assert (
        simulation.calculer_chevauchement_max()
        <= simulation.tolerance_collision
    )


def test_calcul_chevauchement_max():
    """Vérifie le calcul du chevauchement maximal."""

    robots = [
        Robot(1.0, 1.0, 0.0, 0.08),
        Robot(1.05, 1.0, 0.0, 0.08),
        Robot(1.20, 1.0, 0.0, 0.08)
    ]

    simulation = creer_simulation(robots)

    # Les robots 1 et 2 se chevauchent de 2 cm.
    assert simulation.calculer_chevauchement_max() == pytest.approx(
        0.02
    )


def test_chevauchement_sans_collision():
    """Vérifie que le chevauchement vaut zéro sans collision."""

    robots = [
        Robot(1.0, 1.0, 0.0, 0.08),
        Robot(1.5, 1.0, 0.0, 0.08)
    ]

    simulation = creer_simulation(robots)

    assert simulation.calculer_chevauchement_max() == 0.0


def test_simulation_20_robots():
    """Vérifie une simulation avec 20 robots immobiles."""

    robots = []

    # Groupe A
    for _ in range(10):
        robots.append(Robot(0.0, 0.0, 0.0, 0.10))

    # Groupe B
    for _ in range(10):
        robots.append(Robot(0.0, 0.0, 0.0, 0.15))

    # Placement sur une grille de 4 lignes et 5 colonnes
    for i, robot in enumerate(robots):
        colonne = i % 5
        ligne = i // 5

        robot.x = 0.35 + colonne * 0.45
        robot.y = 0.40 + ligne * 0.55

    simulation = creer_simulation(robots)
    simulation.nb_iterations_collisions = 20

    positions_initiales = [
        (robot.x, robot.y) for robot in robots
    ]

    for _ in range(10):
        simulation.effectuer_pas()

    positions_finales = [
        (robot.x, robot.y) for robot in robots
    ]

    assert len(simulation.robots) == 20
    assert simulation.temps == pytest.approx(1.0)
    assert positions_initiales == positions_finales
    assert simulation.calculer_chevauchement_max() == 0.0

    assert sum(r.rayon_virtuel == 0.10 for r in robots) == 10
    assert sum(r.rayon_virtuel == 0.15 for r in robots) == 10
