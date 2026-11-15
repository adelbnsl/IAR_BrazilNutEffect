import pytest 
from src.robot import Robot
from src.simulation import Simulation
from src.controller import Controleur

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