import json

import pytest

from src.config import Parametres, ParametresControleur, appliquer_surcharges
from src.controller import Controleur
from src.experience import creer_simulation
from src.robot import Robot
from src.simulation import Simulation


# ---------- chargement et validation ----------

def test_valeurs_par_defaut_valides_et_identiques_a_l_ancien_code():
    p = Parametres()
    p.valider()
    assert (p.controleur.poids_attraction, p.controleur.poids_repulsion, p.controleur.poids_aleatoire) == (1.0, 10.0, 0.1)
    assert (p.controleur.kp_rotation, p.controleur.vitesse_angulaire_max, p.controleur.vitesse_lineaire) == (2.0, 2.0, 0.05)


def test_aller_retour_dictionnaire():
    p = Parametres()
    assert Parametres.depuis_dict(p.vers_dict()).vers_dict() == p.vers_dict()


def test_fichier_partiel_garde_les_valeurs_par_defaut(tmp_path):
    chemin = tmp_path / "c.json"
    chemin.write_text(json.dumps({"controleur": {"poids_aleatoire": 0.6}}), encoding="utf-8")
    p = Parametres.charger(str(chemin))
    assert p.controleur.poids_aleatoire == 0.6
    assert p.controleur.poids_repulsion == 10.0


def test_cles_commentaire_ignorees(tmp_path):
    chemin = tmp_path / "c.json"
    chemin.write_text(json.dumps({"_note": "x", "arene": {"_note": "y", "cote": 3}}), encoding="utf-8")
    assert Parametres.charger(str(chemin)).arene.cote == 3.0


def test_faute_de_frappe_signalee():
    with pytest.raises(ValueError, match="poids_aleatoir"):
        Parametres.depuis_dict({"controleur": {"poids_aleatoir": 0.6}})
    with pytest.raises(ValueError, match="Section inconnue"):
        Parametres.depuis_dict({"controlleur": {}})


def test_fichier_introuvable_et_json_invalide(tmp_path):
    with pytest.raises(FileNotFoundError):
        Parametres.charger(str(tmp_path / "absent.json"))
    mauvais = tmp_path / "mauvais.json"
    mauvais.write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON"):
        Parametres.charger(str(mauvais))


@pytest.mark.parametrize("donnees", [
    {"simulation": {"dt": 0}},
    {"controleur": {"poids_repulsion": -1}},
    {"groupes": {"n_robots": 20, "effectifs": [10, 5]}},
    {"groupes": {"n_robots": 50}},
    {"controleur": {"poids_aleatoire": "fort"}},
    {"simulation": {"nb_iterations_collisions": 2.5}},
    {"experience": {"valeurs_b": []}},
])
def test_valeurs_invalides_refusees(donnees):
    with pytest.raises(ValueError):
        Parametres.depuis_dict(donnees)


def test_sauvegarde_puis_rechargement(tmp_path):
    p = appliquer_surcharges(Parametres(), ["groupes.effectifs=[10,10]"])
    chemin = str(tmp_path / "sortie.json")
    p.sauvegarder(chemin)
    assert Parametres.charger(chemin).vers_dict() == p.vers_dict()


# ---------- surcharges --set ----------

def test_surcharges():
    p = appliquer_surcharges(Parametres(), ["controleur.poids_aleatoire=0.6", "experience.valeurs_b=[2,3]",
                                            "groupes.effectifs=[10,10]", "experience.graine=5"])
    assert p.controleur.poids_aleatoire == 0.6
    assert p.experience.valeurs_b == [2, 3]
    assert p.groupes.effectifs == [10, 10]
    assert p.experience.graine == 5


@pytest.mark.parametrize("surcharge", ["controleur.poids_aleatoire", "poids=1", "controleur.inconnu=1",
                                       "inconnue.x=1", "controleur.poids_aleatoire=beaucoup"])
def test_surcharges_invalides(surcharge):
    with pytest.raises(ValueError):
        appliquer_surcharges(Parametres(), [surcharge])


# ---------- effet sur le contrôleur et la simulation ----------

def test_controleur_utilise_les_parametres():
    robot = Robot(1.0, 1.25, 0.0, 0.08, groupe=1)  # seul robot : pas de répulsion
    sim = Simulation(2.5, 2.5, [robot], 0.1)

    sim.controleur = Controleur(sim, ParametresControleur(poids_aleatoire=0.0, poids_attraction=3.0))
    dx, dy = sim.controleur.calculer_direction_deplacement(robot)
    assert (dx, dy) == pytest.approx((3.0, 0.0))  # la lumière est à droite, bruit nul

    sim.controleur = Controleur(sim, ParametresControleur(vitesse_lineaire=0.1))
    vg, vd = sim.controleur.calculer_vitesses_roues(robot)
    assert (vg + vd) / 2 == pytest.approx(0.1)


def test_controleur_sans_parametres_garde_le_comportement_historique():
    robot = Robot(1.0, 1.25, 0.0, 0.08)
    sim = Simulation(2.5, 2.5, [robot], 0.1)
    sim.controleur = Controleur(sim)
    vg, vd = sim.controleur.calculer_vitesses_roues(robot)
    assert (vg + vd) / 2 == pytest.approx(0.05)


def test_creer_simulation_applique_les_parametres():
    p = appliquer_surcharges(Parametres(), ["simulation.nb_iterations_collisions=7", "robot.rayon_physique=0.04",
                                            "controleur.poids_repulsion=3"])
    sim = creer_simulation(2.0, 0, p)
    assert sim.nb_iterations_collisions == 7
    assert all(r.rayon_physique == 0.04 for r in sim.robots)
    assert sim.controleur.parametres.poids_repulsion == 3.0


def test_ancien_main_reproductible_par_config():
    p = Parametres.charger("configs/ancien_main.json")
    sim = creer_simulation(p.visualisation.b, 0, p)
    rayons = sorted(r.rayon_virtuel for r in sim.robots)
    assert rayons == pytest.approx([0.10] * 10 + [0.15] * 10)
    assert sum(1 for r in sim.robots if r.groupe == 1) == 10


def test_configs_fournies_valides():
    Parametres.charger("config.json")
    Parametres.charger("configs/bruit_fort.json")
