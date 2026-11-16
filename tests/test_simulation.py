
import math
import pytest

from src.robot import Robot
from src.simulation import Simulation
from src.controller import Controleur


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

def test_direction_lumiere():
    """ 
    Vérifie la direction de la lumière centrale depuis 4 positions différentes.
    """
    robot = Robot(0.25, 1.25, 0.0, 0.10)
    simulation = creer_simulation([robot])
    
    # Lumière à droite.
    assert simulation.calculer_direction_lumiere(robot) == pytest.approx(0.0)
    
    # Lumière à gauche.
    robot.x = 2.25
    robot.y = 1.25
    
    assert simulation.calculer_direction_lumiere(robot) == pytest.approx(math.pi)
    
    # Lumière en haut.
    robot.x = 1.25
    robot.y = 0.25
    
    assert simulation.calculer_direction_lumiere(robot) == pytest.approx(math.pi / 2)
    
    # Lumière en bas.
    robot.x = 1.25
    robot.y = 2.25
    
    assert simulation.calculer_direction_lumiere(robot) == pytest.approx(-math.pi / 2)
    

def test_ecart_lumiere():
    """ 
    Vérifie le calcul de l'écart angulaire entre l'orientation du robot et la lumière.
    """
    robot = Robot(1.25, 0.25, 0.0, 0.10)
    simulation = creer_simulation([robot])
    
    # Cas 1 : lumière à gauche (+90°).
    assert simulation.calculer_ecart_lumiere(robot) == pytest.approx(math.pi / 2)
    
    # Cas 2 : lumière à droite (-90°).
    robot.x = 0.25
    robot.y = 1.25
    robot.theta = math.pi / 2
    
    assert simulation.calculer_ecart_lumiere(robot) == pytest.approx(-math.pi / 2)
    
    # Cas 3 : robot déjà orienté vers la lumière.
    robot.theta = 0.0
    assert simulation.calculer_ecart_lumiere(robot) == pytest.approx(0.0)
    
    # Cas 4 : Normalisation de l'angle. Lumière à +170°, robot orienté à -170°.
    angle_lumiere = math.radians(170)
    robot.x = simulation.lumiere_x - math.cos(angle_lumiere)
    robot.y = simulation.lumiere_y - math.sin(angle_lumiere)
    robot.theta = math.radians(-170)
    
    assert simulation.calculer_ecart_lumiere(robot) == pytest.approx(math.radians(-20))
    

def test_distance_lumiere():
    """ 
    Vérifie le calcul de la distance entre un robot et la lumière centrale.
    """
    robot = Robot(0.25, 1.25, 0.0, 0.10)
    simulation = creer_simulation([robot])
    
    # Cas 1 : robot à 1m de la lumière.
    assert simulation.calculer_distance_lumiere(robot) == pytest.approx(1.0)
    
    # Cas 2 : robot exactement au centre.
    robot.x = 1.25
    robot.y = 1.25
    
    assert simulation.calculer_distance_lumiere(robot) == pytest.approx(0.0)
    
    # Cas 3 : robot en diagonale.
    robot.x = 0.25
    robot.y = 0.25
    assert simulation.calculer_distance_lumiere(robot) == pytest.approx(math.sqrt(2))
    

def test_distance_robots():
    """ 
    Vérifie le calcul de la distance entre 2 robots
    """
    robot1 = Robot(0.5, 1.0, 0.0, 0.10)
    robot2 = Robot(0.8, 1.4, 0.0, 0.15)
    simulation = creer_simulation([robot1, robot2])
    
    # Cas 1 : distance en diagonale.
    assert simulation.calculer_distance_robots(robot1, robot2) == pytest.approx(0.5)
    
    # Cas 2 : robots au même endroit.
    robot2.x = 0.5
    robot2.y = 1.0
    
    assert simulation.calculer_distance_robots(robot1, robot2) == pytest.approx(0.0)
    
    # Cas 3 : distance horizontale.
    robot2.x = 1.5
    robot2.y = 1.0
    
    assert simulation.calculer_distance_robots(robot1, robot2) == pytest.approx(1.0)


def test_detecter_voisins():
    """ 
    Vérifie que seuls les robots situés dans la zone de détection sont retournés.
    """
    robot_a = Robot(0.5, 0.5, 0.0, 0.10)
    robot_b = Robot(0.7, 0.5, 0.0, 0.10)
    robot_c = Robot(0.5, 0.9, 0.0, 0.15)
    robot_d = Robot(1.3, 0.5, 0.0, 0.15)
    simulation = creer_simulation([robot_a, robot_b, robot_c, robot_d])
    
    voisins = simulation.detecter_voisins(robot_a, 0.5)
    
    # Les deux robots proches sont détectés.
    assert robot_b in voisins
    assert robot_c in voisins
    
    # Le robot éloigné n'est pas détecté.
    assert robot_d not in voisins
    
    # Un robot ne se détecte pas lui-même.
    assert robot_a not in voisins
    
    # Exactement 2 voisins.
    assert len(voisins) == 2

def test_chevauchement_virtuel():
    """ 
    Vérifie que le chevauchement virtuel dépend du rayon du robot qui effectue l'observation.
    """
    
    robot_a = Robot(0.5, 0.5, 0.0, 0.10)
    robot_b = Robot(0.68, 0.5, 0.0, 0.15)

    simulation = creer_simulation([robot_a, robot_b])
    
    # Cas 1 : du point de vue du robot A.
    chevauchement_a = simulation.calculer_chevauchement_virtuel(robot_a, robot_b)
    
    assert chevauchement_a == pytest.approx(0.02)
    
    # Cas 2 : du point de vue du robot B.
    chevauchement_b = simulation.calculer_chevauchement_virtuel(robot_b, robot_a)
    
    assert chevauchement_b == pytest.approx(0.12)
    
    # Cas 3 : aucun chevauchement virtuel
    robot_b.x = 1.0
    
    assert simulation.calculer_chevauchement_virtuel(robot_a, robot_b) == pytest.approx(0.0)
    
def test_direction_repulsion():
    """ 
    Vérifie que le vecteur de répulsion pointe dans la direction opposée du voisin
    """
    robot_a = Robot(0.5, 0.5, 0.0, 0.10)
    robot_b = Robot(0.8, 0.5, 0.0, 0.15)

    simulation = creer_simulation([robot_a, robot_b])
    
    # Cas 1 : voisin à droite -> répulsion à gauche.
    ux, uy = simulation.calculer_direction_repulsion(robot_a, robot_b)
    
    assert ux == pytest.approx(-1.0)
    assert uy == pytest.approx(0.0)
    
    # Cas 2 : voisin à gauche -> répulsion à droite.
    robot_b.x = 0.2
    ux, uy = simulation.calculer_direction_repulsion(robot_a, robot_b)
    
    assert ux == pytest.approx(1.0)
    assert uy == pytest.approx(0.0)
    
    # Cas 3 : voisin au-dessus -> répulsion vers le bas.
    robot_b.x = 0.5
    robot_b.y = 0.8
    ux, uy = simulation.calculer_direction_repulsion(robot_a, robot_b)
    
    assert ux == pytest.approx(0.0)
    assert uy == pytest.approx(-1.0)
    
    # Cas 4 : robot exactement au même endroit.
    robot_b.x = 0.5
    robot_b.y = 0.5
    ux, uy = simulation.calculer_direction_repulsion(robot_a, robot_b)
    
    assert ux == pytest.approx(0.0)
    assert uy == pytest.approx(0.0)

def test_repulsion_totale():
    """ 
    Vérifie que les contributions de répulsion de plusieurs voisins s'additionnent.
    """
    robot_a = Robot(1.0, 1.0, 0.0, 0.10)
    robot_b = Robot(1.15, 1.0, 0.0, 0.15)
    robot_c = Robot(1.0, 1.15, 0.0, 0.15)

    simulation = creer_simulation([robot_a, robot_b, robot_c])
    
    # Cas 1 : deux voisins exercent une répulsion.
    rx, ry = simulation.calculer_repulsion_totale(robot_a)
    
    assert rx == pytest.approx(-0.05)
    assert ry == pytest.approx(-0.05)
    
    # Cas 2 : les voisins sont trop éloignés.
    robot_b.x = 2.0
    robot_c.y = 2.0
    rx, ry = simulation.calculer_repulsion_totale(robot_a)
    
    assert rx == pytest.approx(0.0)
    assert ry == pytest.approx(0.0)
    

def test_effectuer_pas_avec_controleur(monkeypatch):
    """ 
    Vérifie que la simulation utilise le contrôleur pour mettre à jour les vitesses et déplacer un robot.
    """
    # Créer un robot initialement immobile.
    robot = Robot(1.0, 1.0, 0.0, 0.10)

    # Créer la simulation et le contrôleur.
    simulation = Simulation(2.5, 2.5, [robot], 0.1)
    controleur = Controleur(simulation)

    # Associer le contrôleur à la simulation.
    simulation.controleur = controleur

    # Imposer des vitesses identiques aux deux roues.
    monkeypatch.setattr(controleur, "calculer_vitesses_roues", lambda robot: (0.05, 0.05))
    
    # Effectuer un pas de simulation.
    simulation.effectuer_pas()
    
    assert robot.vitesse_gauche == pytest.approx(0.05)
    assert robot.vitesse_droite == pytest.approx(0.05)
    
    assert robot.x == pytest.approx(1.005)
    assert robot.y == pytest.approx(1.0)
    
    assert robot.theta == pytest.approx(0.0)
    
    assert simulation.temps == pytest.approx(0.1)

def test_calculer_distance_centre():
    """ 
    Vérifie que la distance entre un robot et le centre de l'arène est correctement calculée.
    """
    
    # Créer un robot situé à 0.5 m du centre.
    robot = Robot(1.55, 1.65, 0.0, 0.10)
    
    # Créer une simulation de 2.5m sur 2.5m.
    simulation = Simulation(2.5, 2.5, [robot], 0.1)
    
    # Calculer la distance du robot au centre.
    distance = simulation.calculer_distance_centre(robot)
    
    # Vérifier que la distance obtenue est de 0.5m.
    assert distance == pytest.approx(0.5)


def test_calculer_distance_moyenne_population(): 
    """
    Vérifie que la distance moyenne au centre est correctement calculée pour chaque population.
    """
     # Créer deux robots de la population A.
    robot1 = Robot(1.25, 1.25, 0.0, 0.10)
    robot2 = Robot(1.55, 1.65, 0.0, 0.10)

    # Créer un robot de la population B.
    robot3 = Robot(1.25, 1.65, 0.0, 0.15)
    
    # Créer la simulation.
    simulation = Simulation(2.5,2.5,[robot1, robot2, robot3], 0.1) 
    
    # Calculer les distances moyennes des populations.
    distance_A = simulation.calculer_distance_moyenne_population(0.10)
    distance_B = simulation.calculer_distance_moyenne_population(0.15)
    
    assert distance_A == pytest.approx(0.25)
    assert distance_B == pytest.approx(0.40)
    
    # Vérifier le cas d'une population inexistante.
    distance_absente = simulation.calculer_distance_moyenne_population(0.20)
    
    assert distance_absente == pytest.approx(0.0)