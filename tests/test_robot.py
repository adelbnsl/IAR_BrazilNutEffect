
import math
import pytest

from src.robot import Robot


def test_initialisation_robot():
    """Vérifie les caractéristiques initiales d'un robot."""

    robot = Robot(
        x=1.0,
        y=1.5,
        theta=0.0,
        rayon_virtuel=0.08
    )

    assert robot.x == 1.0
    assert robot.y == 1.5
    assert robot.theta == 0.0
    assert robot.rayon_virtuel == 0.08

    assert robot.rayon_physique == pytest.approx(0.035)
    assert robot.distance_roues == pytest.approx(0.053)

    assert robot.vitesse_gauche == 0.0
    assert robot.vitesse_droite == 0.0


def test_vitesse_lineaire():
    """Vérifie le calcul de la vitesse linéaire."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.2
    robot.vitesse_droite = 0.4

    # v = (vg + vd) / 2
    vitesse_attendue = (0.2 + 0.4) / 2

    assert robot.calculer_vitesse_lineaire() == pytest.approx(
        vitesse_attendue
    )


def test_vitesse_angulaire():
    """Vérifie le calcul de la vitesse angulaire."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.2
    robot.vitesse_droite = 0.4

    # omega = (vd - vg) / L
    vitesse_attendue = (0.4 - 0.2) / 0.053

    assert robot.calculer_vitesse_angulaire() == pytest.approx(
        vitesse_attendue
    )


def test_orientation():
    """Vérifie la mise à jour de l'orientation."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.2
    robot.vitesse_droite = 0.4

    dt = 0.1

    omega = (0.4 - 0.2) / 0.053
    theta_attendu = omega * dt

    robot.mettre_a_jour_orientation(dt)

    assert robot.theta == pytest.approx(theta_attendu)


def test_position():
    """Vérifie le déplacement rectiligne du robot."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.2
    robot.vitesse_droite = 0.2

    dt = 0.5

    robot.mettre_a_jour_position(dt)

    # Distance parcourue = vitesse * temps = 0.1 m
    assert robot.x == pytest.approx(1.1)
    assert robot.y == pytest.approx(1.0)


def test_deplacement_complet():
    """
    Vérifie le déplacement et la rotation simultanés
    d'un robot différentiel.
    """

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.1
    robot.vitesse_droite = 0.2

    dt = 0.1

    v = (0.1 + 0.2) / 2
    omega = (0.2 - 0.1) / 0.053

    # Dans notre implémentation, la position est
    # mise à jour avant l'orientation.
    x_attendu = 1.0 + v * math.cos(0.0) * dt
    y_attendu = 1.0 + v * math.sin(0.0) * dt
    theta_attendu = omega * dt

    robot.deplacer(dt)

    assert robot.x == pytest.approx(x_attendu)
    assert robot.y == pytest.approx(y_attendu)
    assert robot.theta == pytest.approx(theta_attendu)


def test_deplacement_plusieurs_pas():
    """Vérifie que plusieurs déplacements s'accumulent."""

    robot = Robot(1.0, 1.0, 0.0, 0.08)

    robot.vitesse_gauche = 0.1
    robot.vitesse_droite = 0.1

    dt = 0.1

    for _ in range(5):
        robot.deplacer(dt)

    # 5 * 0.1 * 0.1 = 0.05 m
    assert robot.x == pytest.approx(1.05)
    assert robot.y == pytest.approx(1.0)
    assert robot.theta == pytest.approx(0.0)
