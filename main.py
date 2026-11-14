
from src.robot import Robot
from src.simulation import Simulation


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
