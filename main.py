import argparse
import math
import sys

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from src.config import Parametres, ajouter_arguments_config, appliquer_surcharges
from src.experience import creer_simulation

# Utilisation de la configuration
# -------------------------------
# Les paramètres de l'expérience (contrôleur, groupes de robots, durée, etc.) sont regroupés dans
# src/config.py (valeurs par défaut documentées) et dans config.json à la racine, chargé automatiquement.
# Le fichier peut être partiel : les paramètres absents gardent leur valeur par défaut.
#
#   python main.py                                    # lance l'animation avec config.json
#   python main.py --afficher-config                  # liste tous les paramètres (valeur, unité, description)
#   python main.py --config configs/ancien_main.json  # utilise un autre fichier de configuration
#   python main.py --set controleur.poids_aleatoire=0.6 --set visualisation.b=2
#                                                     # change des paramètres pour cet essai uniquement
#
# Priorité : valeurs par défaut < config.json (ou --config) < --set.
# Les listes s'écrivent sans espace : --set groupes.effectifs=[10,10] (entre guillemets sous PowerShell).

# Couleur d'affichage de chaque groupe (le groupe 1 a le plus petit rayon).
COULEURS_GROUPES = {1: "blue", 2: "orange"}


def calculer_distance_moyenne_groupe(simulation, groupe):
    """
    Calcule la distance moyenne au centre des robots d'un groupe.

    Retourne :
    Distance moyenne en mètres. 0.0 si le groupe est vide.
    """
    distances = [simulation.calculer_distance_centre(robot) for robot in simulation.robots if robot.groupe == groupe]
    return sum(distances) / len(distances) if distances else 0.0


def creer_animation(simulation, parametres):
    """
    Prépare la figure et l'animation des robots dans l'arène.

    À chaque image :
    - La simulation avance de visualisation.pas_par_image pas.
    - Les positions et orientations sont actualisées.
    - Le temps simulé et l'erreur de ségrégation sont affichés.

    Retourne :
    (fig, animation, historiques) où historiques est un dict de listes (temps, g1, g2, se).
    """
    fig, ax = plt.subplots(figsize=(7, 7))
    historiques = {"temps": [], "g1": [], "g2": [], "se": []}

    def mettre_a_jour(frame):

        # Avancer la simulation.
        for _ in range(parametres.visualisation.pas_par_image):
            simulation.effectuer_pas()

        # Mesurer la distance moyenne au centre de chaque groupe et l'erreur de ségrégation.
        distance_g1 = calculer_distance_moyenne_groupe(simulation, 1)
        distance_g2 = calculer_distance_moyenne_groupe(simulation, 2)
        erreur = simulation.calculer_erreur_segregation()

        # Enregistrer l'historique.
        historiques["temps"].append(simulation.temps)
        historiques["g1"].append(distance_g1)
        historiques["g2"].append(distance_g2)
        historiques["se"].append(erreur)

        # Afficher les résultats dans le terminal.
        print(
            f"Temps : {simulation.temps:.1f} s | "
            f"Groupe 1 : {distance_g1:.3f} m | "
            f"Groupe 2 : {distance_g2:.3f} m | "
            f"SE : {erreur:.3f}"
        )

        # Effacer l'affichage précédent.
        ax.clear()

        # Dessiner les robots.
        for i, robot in enumerate(simulation.robots):

            couleur = COULEURS_GROUPES.get(robot.groupe, "gray")

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

        ax.set_title(f"Brazil Nut Effect - Temps : {simulation.temps:.1f} s - SE : {erreur:.3f}")

        ax.grid(True, alpha=0.3)

    animation = FuncAnimation(fig, mettre_a_jour, interval=parametres.visualisation.intervalle_ms, cache_frame_data=False)
    return fig, animation, historiques


def afficher_simulation(simulation, parametres):
    """
    Affiche et anime les robots dans l'arène, puis les graphiques de ségrégation à la fermeture.
    """
    fig, animation, historiques = creer_animation(simulation, parametres)

    plt.show()

    # Afficher le graphique de ségrégation après la fermeture de la fenêtre de simulation.
    if historiques["temps"]:
        afficher_graphique_segregation(historiques, simulation)


def afficher_graphique_segregation(historiques, simulation):
    """
    Affiche l'évolution des distances moyennes au centre et de l'erreur de ségrégation.

    Paramètres:
        historiques : dict de listes (temps, g1, g2, se).
        simulation : simulation terminée (pour lire les rayons virtuels des groupes).
    """
    rayons = {}
    for robot in simulation.robots:
        rayons[robot.groupe] = robot.rayon_virtuel

    fig, (ax_distances, ax_se) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    # Distances moyennes des deux groupes.
    ax_distances.plot(historiques["temps"], historiques["g1"], color=COULEURS_GROUPES[1],
                      label=f"Groupe 1 (rayon {rayons.get(1, 0):.2f} m)")
    ax_distances.plot(historiques["temps"], historiques["g2"], color=COULEURS_GROUPES[2],
                      label=f"Groupe 2 (rayon {rayons.get(2, 0):.2f} m)")
    ax_distances.set_title("Evolution de la Ségrégation")
    ax_distances.set_ylabel("Distance moyenne au centre (m)")
    ax_distances.grid(True)
    ax_distances.legend()

    # Erreur de ségrégation.
    ax_se.plot(historiques["temps"], historiques["se"], color="black")
    ax_se.set_xlabel("Temps simulé (s)")
    ax_se.set_ylabel("Erreur de ségrégation (SE)")
    ax_se.set_ylim(-0.02, 1.0)
    ax_se.grid(True)

    plt.show()


def main(parametres=None):
    """
    Initialise la simulation du Brazil Nut Effect à partir des paramètres (config.json par défaut).
    """
    if parametres is None:
        parametres = Parametres.charger()

    # Création de la simulation : robots, groupes, contrôleur et paramètres.
    graine = parametres.experience.graine
    simulation = creer_simulation(parametres.visualisation.b, graine, parametres)

    print("=== Brazil Nut Effect ===")
    print("Nombre de robots :", len(simulation.robots))
    print("Facteur de rayon b :", parametres.visualisation.b)
    print("Dimensions :", simulation.largeur, "x", simulation.hauteur, "m")

    return simulation


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description="Animation de la simulation Brazil Nut Effect.")
    ajouter_arguments_config(parseur)
    args = parseur.parse_args()

    try:
        parametres = appliquer_surcharges(Parametres.charger(args.config), args.surcharges)
    except (ValueError, FileNotFoundError) as erreur:
        sys.exit(f"Erreur de configuration : {erreur}")

    if args.afficher_config:
        print(parametres.texte_aide())
        sys.exit(0)

    simulation = main(parametres)
    afficher_simulation(simulation, parametres)
