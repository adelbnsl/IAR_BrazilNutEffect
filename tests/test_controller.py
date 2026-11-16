import pytest 
from src.robot import Robot
from src.simulation import Simulation
from src.controller import Controleur
import math

def test_calculer_attraction():
    """ 
    Vérifie que le vecteur d'attraction pointe correctement vers la lumière centrale. 
    """
    
    # Créer un robot à gauche de la lumière.
    robot = Robot(0.25, 1.25, 0.0, 0.10)
    
    # Créer la simulation et le contrôleur.
    simulation = Simulation(2.5, 2.5, [robot], 0.1)
    controleur = Controleur(simulation)
    
    # Cas 1 : lumière à droite.
    ax, ay = controleur.calculer_attraction(robot)
    
    assert ax == pytest.approx(1.0)
    assert ay == pytest.approx(0.0)
    
    # Cas 2 : lumière à gauche.
    robot.x = 2.25
    robot.y = 1.25
    
    ax, ay = controleur.calculer_attraction(robot)
    
    assert ax == pytest.approx(-1.0)
    assert ay == pytest.approx(0.0)
    
    # Cas 3 : lumière en haut.
    robot.x = 1.25
    robot.y = 0.25
    
    ax, ay = controleur.calculer_attraction(robot)
    
    assert ax == pytest.approx(0.0)
    assert ay == pytest.approx(1.0)
    
    # Cas 4 : lumière en bas.
    robot.x = 1.25
    robot.y = 2.25
    
    ax, ay = controleur.calculer_attraction(robot)
    
    assert ax == pytest.approx(0.0)
    assert ay == pytest.approx(-1.0)

def test_calculer_repulsion():
    """ 
    Vérifie que le contrôleur récupère correctement la répulsion totale calculé par la simulation.
    """
    # Créer trois robots.
    robot_a = Robot(1.0, 1.0, 0.0, 0.10)
    robot_b = Robot(1.15, 1.0, 0.0, 0.15)
    robot_c = Robot(1.0, 1.15, 0.0, 0.15)

    # Créer la simulation et le contrôleur.
    simulation = Simulation(
        2.5, 2.5,
        [robot_a, robot_b, robot_c],
        0.1
    )

    controleur = Controleur(simulation)
    
    # Cas 1 : 2 voisins exercent une répulsion.
    rx, ry = controleur.calculer_repulsion(robot_a)
    
    assert rx == pytest.approx(-0.05)
    assert ry == pytest.approx(-0.05)
    
    # Cas 2 : les voisins sont trop éloignés.
    robot_b.x = 2.0
    robot_c.y = 2.0
    rx, ry = controleur.calculer_repulsion(robot_a)
    
    assert rx == pytest.approx(0.0)
    assert ry == pytest.approx(0.0)
    
def test_calculer_mouvement_aléatoire():
    """ 
    Vérifie que le mouvement aléatoire produit toujours un vecteur unitaire.
    """
    # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)
    
    # Répéter le test pour plusieurs directions aléatoires.
    for _ in range(100) :
        # Calcule un vecteur aléatoire. 
        nx, ny = controleur.calculer_mouvement_aleatoire()
        
        # Calculer sa norme.
        norme = (nx**2 + ny**2)**0.5
        
        # Vérifier que sa longueur est égale à 1.
        assert norme == pytest.approx(1.0)
        
def test_calculer_direction_deplacement(monkeypatch):
    """ 
    Vérifie que le contrôleur combine correctement les vecteurs d'attraction, de répulsion et de mouvement aléatoire.
    """
    # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)
    
    # Remplacer temporairement les 3 méthodes par des fonctions retournant des valeurs connues.
    monkeypatch.setattr(controleur, "calculer_attraction", lambda robot: (1.0, 0.0))
    monkeypatch.setattr(controleur, "calculer_repulsion", lambda robot: (-0.2, 0.3))
    monkeypatch.setattr(controleur, "calculer_mouvement_aleatoire", lambda: (0.0, 1.0))
    
    # Calculer la direction résultante.
    dx, dy = controleur.calculer_direction_deplacement(robot)
    
    assert dx == pytest.approx(-1.0)
    assert dy == pytest.approx(3.1)


def test_calculer_orientation_cible(monkeypatch):
    """ 
    Vérifie que le contrôleur calcule correctement l'orientation cible à partir du vecteur de déplacement.
    """
    # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)

    # Définir les vecteurs et leurs angles attendus.
    cas_tests = [
        ((1.0, 0.0), 0.0),
        ((0.0, 1.0), math.pi / 2),
        ((-1.0, 0.0), math.pi),
        ((0.0, -1.0), -math.pi / 2),
        ((1.0, 1.0), math.pi / 4)
    ]
    
    # Vérifier chaque direction.
    for vecteur, angle_attendu in cas_tests :
        # Imposer un vecteur de déplacement connu.
        monkeypatch.setattr(controleur, "calculer_direction_deplacement", lambda robot: vecteur)
        
        # Calculer l'orientation cible.
        angle = controleur.calculer_orientation_cible(robot)
        
        # Vérifier l'angle obtenu.
        assert angle == pytest.approx(angle_attendu)
    
    # Cas particulier : vecteur nul.
    robot.theta = 1.2
    monkeypatch.setattr(controleur, "calculer_direction_deplacement", lambda robot: (0.0, 0.0))
    
    # Le robot doit conserver son orientation actuelle.
    angle = controleur.calculer_orientation_cible(robot)
    
    assert angle == pytest.approx(1.2)
    

def test_calculer_ecart_orientation(monkeypatch):
    """ 
    Vérifie que le contrôleur calcule correctement l'écart angulaire et choisit la rotation minimale.
    """
     # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)
    
    # Définir les orientations actuelles, les orientations cibles et les écarts attendus.
    cas_tests = [
        (0, 90, 90),
        (90, 0, -90),
        (170, -170, 20),
        (-170, 170, -20),
        (45, 45, 0)
    ]

    # Tester les différentes situations.
    for actuel, cible, attendu in cas_tests :
        # Définir l'orientation actuelle du robot.
        robot.theta = math.radians(actuel)
        
        # Imposer une orientation cible connue.
        monkeypatch.setattr(controleur, "calculer_orientation_cible", lambda robot: math.radians(cible))
        
        # Calculer l'écart angulaire.
        ecart = controleur.calculer_ecart_orientation(robot)
        
        assert ecart == pytest.approx(math.radians(attendu))


def test_calculer_vitesse_rotation(monkeypatch):
    """ 
    Vérifie que le contrôleur calcule correctement la vitesse angulaire et respecte ses limites.
    """
    # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)

    # Définir les écarts angulaires et les vitesses attendues.
    cas_tests = [
        (0, 0.0),
        (30, math.pi / 3),
        (-30, -math.pi / 3),
        (90, 2.0),
        (-90, -2.0)
    ]
    
    # Tester les différentes situations.
    for angle_degres, vitesse_attendue in cas_tests :
        
        # Convertir l'écart angulaire en radians.
        ecart = math.radians(angle_degres)

        # Imposer un écart angulaire connu.
        monkeypatch.setattr(controleur, "calculer_ecart_orientation", lambda robot: ecart)
        
        # Calculer la vitesse angulaire.
        omega = controleur.calculer_vitesse_rotation(robot)
        
        assert omega == pytest.approx(vitesse_attendue)


def test_calculer_vitesses_roues(monkeypatch):
    """ 
    Vérifie que le contrôleur calcule correctement les vitesses des roues gauche et droite.
    """
     # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)

    # Définir les vitesses angulaires et
    # les vitesses des roues attendues.
    cas_tests = [
        (0.0, 0.05, 0.05),
        (1.0, 0.0235, 0.0765),
        (-1.0, 0.0765, 0.0235)
    ]
    
    # Tester les différentes situations.
    for omega, vg_attendue, vd_attendue in cas_tests :
        # Imposer une vitesse angulaire connue.
        monkeypatch.setattr(controleur, "calculer_vitesse_rotation", lambda robot: omega)
        
        # Calculer les vitesses des roues.
        vg, vd = controleur.calculer_vitesses_roues(robot)
        
        assert vg == pytest.approx(vg_attendue)
        assert vd == pytest.approx(vd_attendue)
        

def test_appliquer_vitesses_roues(monkeypatch):
    """ 
    Vérifie que le contrôleur applique correctement les vitesses calculées aux deux roues du robot.
    """
    # Créer un robot et une simulation.
    robot = Robot(1.0, 1.0, 0.0, 0.10)
    simulation = Simulation(2.5, 2.5, [robot], 0.1)

    # Créer le contrôleur.
    controleur = Controleur(simulation)
    
    # Vérifier que les vitesses initiales sont nulles.
    assert robot.vitesse_gauche == pytest.approx(0.0)
    assert robot.vitesse_droite == pytest.approx(0.0)
    
    # Imposer des vitesses de roues connues.
    monkeypatch.setattr(controleur, "calculer_vitesses_roues", lambda robot: (0.0235, 0.0765))
    
    # Appliquer les vitesses au robot.
    controleur.appliquer_vitesses_roues(robot)

    assert robot.vitesse_gauche == pytest.approx(0.0235)
    assert robot.vitesse_droite == pytest.approx(0.0765)