import math

import pytest

from src.config import Parametres, ParametresArticle, appliquer_surcharges
from src.controller import Controleur, ControleurArticle
from src.experience import creer_simulation
from src.robot import Robot
from src.simulation import Simulation


def creer(robots, **parametres):
    sim = Simulation(2.5, 2.5, robots, 0.1)
    sim.controleur = ControleurArticle(sim, ParametresArticle(**parametres))
    return sim


def robot_seul(theta=0.0, x=1.0):
    return Robot(x, 1.25, theta, 0.08, groupe=1)  # la lumière est à (1.25, 1.25)


# ---------- répulsion (équation 2) et plafond f(.) ----------

def test_repulsion_k_fois_chevauchement_en_cm():
    robot = Robot(1.00, 1.25, 0.0, 0.08)
    voisin = Robot(1.12, 1.25, 0.0, 0.08)  # distance 12 cm, 2r = 16 cm : chevauchement 4 cm
    sim = creer([robot, voisin])
    rx, ry = sim.controleur.calculer_repulsion(robot)
    assert (rx, ry) == pytest.approx((-0.2 * 4, 0.0))  # k = 0.2, repoussé à l'opposé du voisin


def test_pas_de_repulsion_au_dela_de_2r():
    robot = Robot(1.0, 1.25, 0.0, 0.08)
    voisin = Robot(1.2, 1.25, 0.0, 0.08)  # 20 cm > 16 cm
    sim = creer([robot, voisin])
    assert sim.controleur.calculer_repulsion(robot) == (0.0, 0.0)


def test_repulsion_plafonnee():
    robot = Robot(1.0, 1.25, 0.0, 0.08)
    voisins = [Robot(1.02, 1.25, 0.0, 0.08) for _ in range(5)]  # 5 x (0.2 * 14) = 14 > 6.4
    sim = creer([robot] + voisins)
    rx, ry = sim.controleur.calculer_repulsion(robot)
    assert math.hypot(rx, ry) == pytest.approx(6.4)
    assert rx < 0


def test_le_robot_suppose_le_meme_rayon_chez_ses_voisins():
    petit = Robot(1.00, 1.25, 0.0, 0.08)
    grand = Robot(1.75, 1.25, 0.0, 0.40)  # à 75 cm l'un de l'autre
    sim = creer([petit, grand])
    # Le petit suppose un rayon de 8 cm chez son voisin : portée 16 cm, il ne ressent rien à 75 cm.
    assert sim.controleur.calculer_repulsion(petit) == (0.0, 0.0)
    # Le grand suppose un rayon de 40 cm chez son voisin : portée 80 cm, chevauchement de 5 cm.
    assert sim.controleur.calculer_repulsion(grand) == pytest.approx((0.2 * 5, 0.0))


# ---------- cycle : scan, rotation, avance ----------

def test_scan_robot_immobile():
    robot = robot_seul()
    sim = creer([robot])
    for _ in range(24):  # 2,4 s
        sim.effectuer_pas()
        assert (robot.vitesse_gauche, robot.vitesse_droite) == (0.0, 0.0)
    assert (robot.x, robot.y) == (1.0, 1.25)


def test_rotation_puis_avance_vers_la_lumiere():
    robot = robot_seul(theta=math.pi)  # tourné à l'opposé de la lumière
    sim = creer([robot], poids_aleatoire=0.0)
    for _ in range(37):  # fin de la rotation à 3,7 s
        sim.effectuer_pas()
    assert math.cos(robot.theta) == pytest.approx(1.0, abs=1e-6)  # orienté vers la lumière
    assert robot.x == pytest.approx(1.0)  # pas encore avancé

    for _ in range(13):  # phase d'avance : 1,3 s
        sim.effectuer_pas()
    vitesse_attendue = 0.128 * 1.0 / (1.0 + 0.0 + 6.4)  # norme 1, maximum possible 7.4
    assert robot.x == pytest.approx(1.0 + vitesse_attendue * 1.3, abs=1e-6)


def test_vitesse_proportionnelle_a_la_norme_et_bornee():
    robot = robot_seul()
    sim = creer([robot], poids_aleatoire=0.0)
    sim.temps = 4.0  # phase d'avance
    vg, vd = sim.controleur.calculer_vitesses_roues(robot)
    assert vg == vd == pytest.approx(0.128 / 7.4)

    # Un robot pressé par 5 voisins a une norme bien plus grande, donc une vitesse plus grande, mais bornée.
    voisins = [Robot(1.02, 1.25, 0.0, 0.08) for _ in range(5)]
    sim2 = creer([robot] + voisins, poids_aleatoire=0.0)
    sim2.temps = 4.0
    vg2, _ = sim2.controleur.calculer_vitesses_roues(robot)
    assert vg < vg2 <= 0.128


def test_bruit_conserve_pendant_tout_le_cycle():
    robot = robot_seul()
    sim = creer([robot])
    appels = []
    original = sim.controleur.calculer_mouvement_aleatoire
    sim.controleur.calculer_mouvement_aleatoire = lambda: appels.append(1) or original()

    for _ in range(50):  # un cycle complet de 5 s
        sim.effectuer_pas()
    assert len(appels) == 1  # un seul tirage par cycle

    for _ in range(50):  # deuxième cycle
        sim.effectuer_pas()
    assert len(appels) == 2


# ---------- intégration avec la config ----------

def test_le_mode_choisit_le_controleur():
    assert isinstance(creer_simulation(3, 0, Parametres()).controleur, Controleur)
    assert not isinstance(creer_simulation(3, 0, Parametres()).controleur, ControleurArticle)

    p = appliquer_surcharges(Parametres(), ["controleur.mode=article"])
    assert isinstance(creer_simulation(3, 0, p).controleur, ControleurArticle)


@pytest.mark.parametrize("surcharge", ["controleur.mode=autre", "controleur.mode=3",
                                       "article.duree_scan=4", "article.vitesse_max=0", "article.k_repulsion=-1"])
def test_config_article_invalide(surcharge):
    with pytest.raises(ValueError):
        appliquer_surcharges(Parametres(), [surcharge])


def test_segregation_avec_le_controleur_article():
    p = appliquer_surcharges(Parametres(), ["controleur.mode=article"])
    sim = creer_simulation(3, 0, p)
    for _ in range(int(300 / 0.1)):  # 5 minutes simulées
        sim.effectuer_pas()
    assert sim.calculer_erreur_segregation() <= 0.02
