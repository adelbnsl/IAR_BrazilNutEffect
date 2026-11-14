
from src.robot import Robot
from src.simulation import Simulation
import matplotlib.pyplot as plt
import math

def afficher_simulation(simulation):
    """ 
    Affiche l'arène et les positions des robots.
    
    Groupe A : Bleu (rayon virtuel 0.10 m)
    Groupe B : Orange (rayon virtuel 0.15 m)
    """
    fig, ax = plt.subplots(figsize=(7, 7))
    
    for i, robot in enumerate(simulation.robots) :
        # Choisir la couleur selon le groupe.
        couleur = "blue" if robot.rayon_virtuel == 0.10 else "orange"
        
        # Dessiner le robot avec son rayon physique.
        cercle = plt.Circle((robot.x, robot.y), robot.rayon_physique, color = couleur, alpha = 0.8)
        ax.add_patch(cercle)
        
        # Afficher la direction du robot.
        longeur_fleche = 0.08
        dx = longeur_fleche * math.cos(robot.theta)
        dy = longeur_fleche * math.sin(robot.theta)
        ax.arrow(robot.x, robot.y, dx, dy, head_width=0.025, head_length=0.025, fc="black", ec="black", length_includes_head=True)
        
        # Afficher le numéro du robot. 
        ax.text(robot.x, robot.y + 0.07, str(i + 1), ha="center", fontsize=8)
    
    # Dimensions de l'arène.
    ax.set_xlim(0, simulation.largeur)
    ax.set_ylim(0, simulation.hauteur)
    
    # Respecter les proportions physiques 
    ax.set_aspect("equal")
    
    ax.set_xlabel("Position x (m)")
    ax.set_ylabel("Position y (m)")
    ax.set_title("Brazil Nut Effect - 20 robots")
    
    ax.grid(True, alpha=0.3)
    plt.show()
    
def main():
    """
    Initialise et lance la simulation du Brazil Nut Effect.
    """

    # Création des 20 robots
    robots = []

    # Groupe A : 10 robots
    for i in range(10):
        robot = Robot(
            x=0.0,
            y=0.0,
            theta=0.0,
            rayon_virtuel=0.10
        )
        robots.append(robot)

    # Groupe B : 10 robots
    for i in range(10):
        robot = Robot(
            x=0.0,
            y=0.0,
            theta=0.0,
            rayon_virtuel=0.15
        )
        robots.append(robot)

    # Placement provisoire sur une grille
    for i, robot in enumerate(robots):
        colonne = i % 5
        ligne = i // 5

        robot.x = 0.35 + colonne * 0.45
        robot.y = 0.40 + ligne * 0.55

    # Création de la simulation
    simulation = Simulation(
        largeur=2.5,
        hauteur=2.5,
        robots=robots,
        dt=0.1
    )

    simulation.nb_iterations_collisions = 20

    print("=== Brazil Nut Effect ===")
    print("Nombre de robots :", len(simulation.robots))
    print("Dimensions :", simulation.largeur, "x", simulation.hauteur, "m")

    return simulation


if __name__ == "__main__":
    simulation = main()
    afficher_simulation(simulation)
