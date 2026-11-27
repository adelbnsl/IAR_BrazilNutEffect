import pytest

from experiments.run_experiments import lancer_essai
from src.config import Parametres, appliquer_surcharges
from src.experience import calculer_effectifs, creer_simulation
from src.robot import Robot
from src.simulation import Simulation


def creer_sim(positions_groupes):
    """positions_groupes : liste de (distance_au_centre, groupe, rayon)."""
    robots = [Robot(1.25 + d, 1.25, 0.0, r, groupe=g) for d, g, r in positions_groupes]
    return Simulation(2.5, 2.5, robots, 0.1)


def test_se_nul_si_petits_au_centre():
    sim = creer_sim([(0.1, 1, 0.08), (0.2, 1, 0.08), (0.5, 2, 0.16), (0.6, 2, 0.16)])
    assert sim.calculer_erreur_segregation() == 0.0


def test_se_vaut_un_si_configuration_inversee():
    sim = creer_sim([(0.5, 1, 0.08), (0.6, 1, 0.08), (0.1, 2, 0.16), (0.2, 2, 0.16)])
    assert sim.calculer_erreur_segregation() == 1.0


def test_se_partiel():
    # Un petit (0.5) est plus loin que l'un des deux grands (0.3) : 2 paires ordonnées sur 8 sont fausses.
    sim = creer_sim([(0.1, 1, 0.08), (0.5, 1, 0.08), (0.3, 2, 0.16), (0.6, 2, 0.16)])
    assert sim.calculer_erreur_segregation() == pytest.approx(2 / 8)


def test_se_un_seul_groupe():
    sim = creer_sim([(0.1, 1, 0.08), (0.2, 1, 0.08)])
    assert sim.calculer_erreur_segregation() == 0.0


def test_se_sans_groupe_leve_erreur():
    sim = Simulation(2.5, 2.5, [Robot(1.0, 1.0, 0.0, 0.08)], 0.1)
    with pytest.raises(ValueError):
        sim.calculer_erreur_segregation()


@pytest.mark.parametrize("b, attendu", [(1, [5, 15]), (2, [11, 9]), (3, [15, 5]), (4, [17, 3]), (5, [18, 2])])
def test_effectifs_table_1_de_l_article(b, attendu):
    assert calculer_effectifs(20, [0.08, 0.08 * b]) == attendu


def test_creation_simulation_effectifs_et_groupes():
    sim = creer_simulation(b=3, graine=0)
    assert len(sim.robots) == 20
    assert sum(1 for r in sim.robots if r.groupe == 1) == 15
    assert sum(1 for r in sim.robots if r.groupe == 2) == 5


def test_essai_court_reproductible():
    parametres = appliquer_surcharges(Parametres(), ["experience.duree=20", "experience.periode_mesure=5"])
    tache = {"b": 3, "essai": 0, "graine": 7, "parametres": parametres}
    a = lancer_essai(tache)["resume"]["se_final"]
    b = lancer_essai(tache)["resume"]["se_final"]
    assert a == b and 0.0 <= a <= 1.0
