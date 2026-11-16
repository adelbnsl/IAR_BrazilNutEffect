
from src.robot import Robot
from src.simulation import Simulation
import matplotlib.pyplot as plt
import math
from matplotlib.animation import FuncAnimation
from src.controller import Controleur
import random


def afficher_simulation(simulation):
    """
    Affiche et anime les robots dans l'arène.

    À chaque image :
    - La simulation avance d'un pas.
    - Les positions et orientations sont actualisées.
    - Le temps simulé est affiché.
    """

    fig, ax = plt.subplots(figsize=(7, 7))
    historique_temps = []
    historique_bleu = []
    historique_orange = []

    def mettre_a_jour(frame):

        # Avancer la simulation d'un pas.
        simulation.effectuer_pas()
        
        # Calculer la distance moyenne au centre pour chaque population.
        distance_bleue = simulation.calculer_distance_moyenne_population(0.10)
        distance_orange = simulation.calculer_distance_moyenne_population(0.15)
        
        # Enrengistrer le temps simulé.
        historique_temps.append(simulation.temps)
        
        # Enrengistrer les distances moyennes des deux populations.
        historique_bleu.append(distance_bleue)
        historique_orange.append(distance_orange)
        # Afficher les résultats dans le terminal.
        print(
        f"Temps : {simulation.temps:.1f} s | "
        f"Bleus : {distance_bleue:.3f} m | "
        f"Orange : {distance_orange:.3f} m"
        )

        # Effacer l'affichage précédent.
        ax.clear()

        # Dessiner les 20 robots.
        for i, robot in enumerate(simulation.robots):

            couleur = ("blue" if robot.rayon_virtuel == 0.10 else "orange")

            # Corps physique du robot.
            cercle = plt.Circle((robot.x, robot.y), robot.rayon_physique, color=couleur, alpha=0.8)
            ax.add_patch(cercle)

            # Orientation du robot.
            longueur_fleche = 0.08

            dx = longueur_fleche * math.cos(robot.theta)
            dy = longueur_fleche * math.sin(robot.theta)

            ax.arrow(robot.x, robot.y, dx, dy, head_width=0.025, head_length=0.025, fc="black", ec="black", length_includes_head=True)

            # Numéro du robot.
            ax.text(robot.x, robot.y + 0.07, str(i + 1), ha="center", fontsize=8)

        # Configuration de l'arène.
        ax.set_xlim(0, simulation.largeur)
        ax.set_ylim(0, simulation.hauteur)
        ax.set_aspect("equal")

        ax.set_xlabel("Position x (m)")
        ax.set_ylabel("Position y (m)")

        ax.set_title(
            f"Brazil Nut Effect - Temps : {simulation.temps:.1f} s"
        )

        ax.grid(True, alpha=0.3)

    # Animation : mise à jour toutes les 100 ms.
    animation = FuncAnimation(fig, mettre_a_jour, interval=100, cache_frame_data=False)

    plt.show()
    
    # Afficher le graphique de ségrégation après la fermeture de la fenêtre de simulation.
    if historique_temps:
        afficher_graphique_segregation(historique_temps, historique_bleu, historique_orange)

def afficher_graphique_segregation(historique_temps, historique_bleu, historique_orange):
    """
    Affiche l'évolution de la distance moyenne au centre pour les 2 populations de robots.

    Paramètres:
        historique_temps : liste des temps simulés.
        historique_bleu : distances moyennes des robots bleus.
        historique_orange : distances moyennes des robots oranges.
    """
    # Créer une nouvelle figure pour le graphique.
    fig, ax = plt.subplots(figsize=(9, 5))
    
    # Tracer les distances moyennes des deux populations.
    ax.plot(historique_temps, historique_bleu, color="blue", label="Robots Bleus (0.10m)")
    ax.plot(historique_temps, historique_orange, color="orange", label="Robots Oranges (0.15m)")
    
    # Ajouter les informations du graphique.
    ax.set_title("Evolution de la Ségrégation")
    ax.set_xlabel("Temps simulé (s)")
    ax.set_ylabel("Distance moyenne au centre (m)")
    
    # Afficher une grille et la légende.
    ax.grid(True)
    ax.legend()
    
    plt.show()
    
def main():
    """
    Initialise et lance la simulation du Brazil Nut Effect.
    """

    # Création des 20 robots.
    robots = []

    # Groupe A : 10 robots
    for i in range(10):
        robot = Robot(0.0, 0.0, 0.0, 0.10)
        robots.append(robot)

    # Groupe B : 10 robots.
    for i in range(10):
        robot = Robot(0.0, 0.0, 0.0, 0.15)
        robots.append(robot)

    # Mélanger aléatoirement les 2 populations de robots.
    random.shuffle(robots)
    # Placement provisoire sur une grille.
    for i, robot in enumerate(robots):
        colonne = i % 5
        ligne = i // 5

        robot.x = 0.35 + colonne * 0.45
        robot.y = 0.40 + ligne * 0.55

    # Création de la simulation.
    simulation = Simulation(2.5, 2.5, robots, 0.1)
    
    # Créer le contrôleur autonome des robots.
    controleur = Controleur(simulation)
    
    # Associer le contrôleur à la simulation.
    simulation.controleur = controleur

    simulation.nb_iterations_collisions = 20
    
    

    print("=== Brazil Nut Effect ===")
    print("Nombre de robots :", len(simulation.robots))
    print("Dimensions :", simulation.largeur, "x", simulation.hauteur, "m")

    return simulation


if __name__ == "__main__":
    simulation = main()
    afficher_simulation(simulation)
