from src.robot import Robot
from src.simulation import Simulation
import math

# Création de 2 robots avec 2 rayon_virtuel différents.
robot1 = Robot(x=1.0, y=1.5, theta=0.0, rayon_virtuel=0.08)
robot2 = Robot(x=1.5, y=1.0, theta=1.57, rayon_virtuel=0.24)

# Test du calcul de la vitesse linéaire
robot1.vitesse_gauche = 0.2
robot1.vitesse_droite = 0.4

print("=== Test vitesse linéaire ===")
print("Vitesse gauche :", robot1.vitesse_gauche)
print("Vitesse droite :", robot1.vitesse_droite)
print("Vitesse linéaire :", robot1.calculer_vitesse_lineaire(), "m/s")


# Test du calcul de la vitesse angulaire
print("=== Test vitesse angulaire ===")
print("Vitesse gauche :", robot1.vitesse_gauche)
print("Vitesse droite :", robot1.vitesse_droite)
print("Distance entre les roues :", robot1.distance_roues)
print("Vitesse angulaire :", robot1.calculer_vitesse_angulaire(), "rad/s")



#Regrouper ces robots dans une liste.
robots = [robot1, robot2]

# Affichage des caractéristiques des robots.
for i, robot in enumerate(robots, start=1):
    print(f"=== Robot {i} ===")
    print("Position :", (robot.x, robot.y))
    print("Orientation :", robot.theta)
    print("Rayon virtuel :", robot.rayon_virtuel)
    print("Vitesse gauche :", robot.vitesse_gauche)
    print("Vitesse droite :", robot1.vitesse_droite)


# Test de la mise à jour de l'orientation
print("=== Test mise à jour orientation ===")

# On remet l'orientation initiale à zéro
robot1.theta = 0.0

# Durée d'un pas de simulation : 0,1 seconde
dt = 0.1

print("Orientation avant :", robot1.theta, "rad")

# Mise à jour de l'orientation
robot1.mettre_a_jour_orientation(dt)

print("Orientation après :", robot1.theta, "rad")


# Test de la mise à jour de la position
print("=== Test mise à jour position ===")

# Position initiale du robot
robot1.x = 1.0
robot1.y = 1.0

# Orientation initiale : vers la droite
robot1.theta = 0.0

# Même vitesse pour les deux roues
robot1.vitesse_gauche = 0.2
robot1.vitesse_droite = 0.2

# Durée du déplacement
dt = 0.5

print("Position avant :", robot1.x, robot1.y)

# Déplacement du robot
robot1.mettre_a_jour_position(dt)

print("Position après :", robot1.x, robot1.y)


# Test du déplacement complet du robot
print("=== Test déplacement complet ===")

# Réinitialisation du robot
robot1.x = 1.0
robot1.y = 1.0
robot1.theta = 0.0

# La roue droite tourne plus vite que la gauche
robot1.vitesse_gauche = 0.1
robot1.vitesse_droite = 0.2

# Durée d'un pas de simulation
dt = 0.1

# Effectuer 5 pas de déplacement
for i in range(5):
    robot1.deplacer(dt)

    print(f"Pas {i + 1} :")
    print(f"  Position : ({robot1.x:.4f}, {robot1.y:.4f})")
    print(f"  Orientation : {robot1.theta:.4f} rad")


# Test de l'initialisation de la simulation
print("=== Test initialisation simulation ===")

simulation = Simulation(largeur=2.5, hauteur=2.5, robots=robots, dt=0.1)

print("Largeur de l'arène :", simulation.largeur, "m")
print("Hauteur de l'arène :", simulation.hauteur, "m")
print("Nombre de robots :", len(simulation.robots))
print("Pas de temps :", simulation.dt, "s")
print("Temps initial :", simulation.temps, "s")



# Test de plusieurs pas de simulation
print("=== Test des pas de simulation ===")

# Réinitialiser les positions des robots
robot1.x = 1.0
robot1.y = 1.0
robot1.theta = 0.0

robot2.x = 1.5
robot2.y = 1.5
robot2.theta = 0.0

# Définir les vitesses des roues
robot1.vitesse_gauche = 0.1
robot1.vitesse_droite = 0.1

robot2.vitesse_gauche = 0.1
robot2.vitesse_droite = 0.2

# Effectuer 5 pas de simulation
for i in range(5):
    simulation.effectuer_pas()

    print(f"=== Pas {i + 1} ===")
    print(f"Temps : {simulation.temps:.2f} s")

    for j, robot in enumerate(simulation.robots, start=1):
        print(
            f"Robot {j} : "
            f"({robot.x:.4f}, {robot.y:.4f}), "
            f"theta = {robot.theta:.4f} rad"
        )



# Test des limites de l'arène
print("=== Test limites de l'arène ===")

# Placer volontairement le robot hors de l'arène
robot1.x = -0.3
robot1.y = 2.8

print("Position avant :", robot1.x, robot1.y)

# Corriger la position du robot
simulation.gerer_limites(robot1)

print("Position après :", robot1.x, robot1.y)


# Test des limites pendant la simulation
print("=== Test limites automatiques ===")

# Placer le robot 1 près du mur droit
robot1.x = 2.48
robot1.y = 1.0
robot1.theta = 0.0

# Le robot avance vers la droite
robot1.vitesse_gauche = 0.2
robot1.vitesse_droite = 0.2

print("Position avant :", robot1.x, robot1.y)

# Effectuer 5 pas de simulation
for i in range(5):
    simulation.effectuer_pas()

    print(
        f"Pas {i + 1} : "
        f"Position = ({robot1.x:.4f}, {robot1.y:.4f})"
    )


# Test des limites avec le rayon physique
print("=== Test limites avec rayon physique ===")

# Placer le robot près du mur droit
robot1.x = 2.44
robot1.y = 1.0
robot1.theta = 0.0

# Le robot avance vers la droite
robot1.vitesse_gauche = 0.2
robot1.vitesse_droite = 0.2

print("Rayon physique :", robot1.rayon_physique, "m")
print("Position initiale :", robot1.x, robot1.y)

# Effectuer 5 pas de simulation
for i in range(5):
    simulation.effectuer_pas()

    print(
        f"Pas {i + 1} : "
        f"Position = ({robot1.x:.4f}, {robot1.y:.4f})"
    )


# Test de détection des collisions
print("=== Test détection collisions ===")

# Premier robot à une position fixe
robot1.x = 1.0
robot1.y = 1.0

# Deuxième robot à 5 cm du premier
robot2.x = 1.05
robot2.y = 1.0

print("=== Test 1 : robots proches ===")
print("Collision :", simulation.detecter_collision(robot1, robot2))

# Éloigner le deuxième robot à 20 cm
robot2.x = 1.20
robot2.y = 1.0

print("=== Test 2 : robots éloignés ===")
print("Collision :", simulation.detecter_collision(robot1, robot2))



# Test de résolution d'une collision
print("=== Test résolution collision ===")

# Placer deux robots à 5 cm l'un de l'autre
robot1.x = 1.0
robot1.y = 1.0

robot2.x = 1.05
robot2.y = 1.0

print("=== Avant correction ===")
print(f"Robot 1 : ({robot1.x:.4f}, {robot1.y:.4f})")
print(f"Robot 2 : ({robot2.x:.4f}, {robot2.y:.4f})")

print("Collision :", simulation.detecter_collision(robot1, robot2))

# Corriger le chevauchement
simulation.resoudre_collision(robot1, robot2)

print("=== Après correction ===")
print(f"Robot 1 : ({robot1.x:.4f}, {robot1.y:.4f})")
print(f"Robot 2 : ({robot2.x:.4f}, {robot2.y:.4f})")

print("Collision :", simulation.detecter_collision(robot1, robot2))



# Test des collisions automatiques
print("=== Test collisions automatiques ===")

# Position initiale des robots
robot1.x = 1.0
robot1.y = 1.0
robot1.theta = 0.0

robot2.x = 1.20
robot2.y = 1.0
robot2.theta = math.pi

# Les robots avancent l'un vers l'autre
robot1.vitesse_gauche = 0.1
robot1.vitesse_droite = 0.1

robot2.vitesse_gauche = 0.1
robot2.vitesse_droite = 0.1

# Simulation sur 10 pas
for i in range(10):
    simulation.effectuer_pas()

    distance = math.sqrt(
        (robot2.x - robot1.x)**2
        + (robot2.y - robot1.y)**2
    )

    print(
        f"Pas {i + 1} : "
        f"R1 = {robot1.x:.3f}, "
        f"R2 = {robot2.x:.3f}, "
        f"Distance = {distance:.3f}"
    )



# Préparation du test avec trois robots
print("=== Test avec trois robots ===")

robot3 = Robot(
    x=1.12,
    y=1.0,
    theta=0.0,
    rayon_virtuel=0.08
)

# Réinitialiser les positions
robot1.x = 1.0
robot1.y = 1.0

robot2.x = 1.06
robot2.y = 1.0

# Immobiliser les robots pour ce test
for robot in [robot1, robot2, robot3]:
    robot.vitesse_gauche = 0.0
    robot.vitesse_droite = 0.0

# Nouvelle simulation contenant trois robots
simulation3 = Simulation(
    largeur=2.5,
    hauteur=2.5,
    robots=[robot1, robot2, robot3],
    dt=0.1
)

print("Robot 1 :", robot1.x, robot1.y)
print("Robot 2 :", robot2.x, robot2.y)
print("Robot 3 :", robot3.x, robot3.y)



# Effectuer un pas de simulation
simulation3.effectuer_pas()

print("=== Après un pas de simulation ===")

# Afficher les positions
for i, robot in enumerate(simulation3.robots):
    print(f"Robot {i + 1} : x = {robot.x:.5f}")

# Vérifier les distances entre les robots
for i in range(len(simulation3.robots)):
    for j in range(i + 1, len(simulation3.robots)):

        robot_a = simulation3.robots[i]
        robot_b = simulation3.robots[j]

        distance = math.sqrt(
            (robot_b.x - robot_a.x)**2
            + (robot_b.y - robot_a.y)**2
        )

        collision = simulation3.detecter_collision(
            robot_a, robot_b
        )

        print(
            f"Robots {i + 1}-{j + 1} : "
            f"distance = {distance:.5f} m, "
            f"collision = {collision}"
        )


# Test des cinq itérations de correction
print("=== Test des 5 itérations ===")

# Réinitialiser les positions des trois robots
robot1.x = 1.0
robot1.y = 1.0

robot2.x = 1.06
robot2.y = 1.0

robot3.x = 1.12
robot3.y = 1.0

# Immobiliser les robots
for robot in simulation3.robots:
    robot.vitesse_gauche = 0.0
    robot.vitesse_droite = 0.0

# Effectuer un seul pas de simulation
simulation3.effectuer_pas()

# Afficher les nouvelles positions
for i, robot in enumerate(simulation3.robots):
    print(f"Robot {i + 1} : x = {robot.x:.6f}")

# Mesurer les distances
for i in range(len(simulation3.robots)):
    for j in range(i + 1, len(simulation3.robots)):

        robot_a = simulation3.robots[i]
        robot_b = simulation3.robots[j]

        distance = math.sqrt(
            (robot_b.x - robot_a.x)**2
            + (robot_b.y - robot_a.y)**2
        )

        chevauchement = max(
            0.0,
            robot_a.rayon_physique
            + robot_b.rayon_physique
            - distance
        )

        print(
            f"Robots {i + 1}-{j + 1} : "
            f"distance = {distance:.6f} m, "
            f"chevauchement = {chevauchement:.6f} m"
        )



# Vérification de la tolérance des collisions
print("=== Vérification de la tolérance ===")

tolerance = 0.0001  # 0.1 mm
chevauchement_max = 0.0

for i in range(len(simulation3.robots)):
    for j in range(i + 1, len(simulation3.robots)):

        robot_a = simulation3.robots[i]
        robot_b = simulation3.robots[j]

        distance = math.sqrt(
            (robot_b.x - robot_a.x)**2
            + (robot_b.y - robot_a.y)**2
        )

        chevauchement = max(
            0.0,
            robot_a.rayon_physique
            + robot_b.rayon_physique
            - distance
        )

        chevauchement_max = max(
            chevauchement_max,
            chevauchement
        )

print(f"Chevauchement maximal : {chevauchement_max:.8f} m")
print(f"Tolérance : {tolerance:.8f} m")
print("Tolérance respectée :", chevauchement_max <= tolerance)
