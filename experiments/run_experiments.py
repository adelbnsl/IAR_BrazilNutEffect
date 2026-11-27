"""
Expériences de l'article (Chen et al., AAMAS 2012) en simulation.

Pour chaque facteur de rayon b, on lance plusieurs essais de n robots répartis en
2 groupes (rayons a et a*b). On mesure l'erreur de ségrégation (SE, équation 5)
et les distances finales au centre, puis on écrit des CSV et des figures
analogues aux figures 7, 8 et 9 de l'article.

Tous les paramètres viennent de la configuration (voir src/config.py et config.json).

Exemples (depuis la racine du projet) :

    python experiments/run_experiments.py                          # protocole de l'article (config.json)
    python experiments/run_experiments.py --essais 3 --duree 120   # essai rapide
    python experiments/run_experiments.py --b 2 3 --set controleur.poids_aleatoire=0.6
    python experiments/run_experiments.py --config configs/mon_essai.json --sortie results/essai1
    python experiments/run_experiments.py --afficher-config        # liste de tous les paramètres
    python experiments/run_experiments.py --figures-seulement      # refaire les figures depuis les CSV
    python experiments/run_experiments.py --set controleur.mode=article --b 3 --essais 2 --duree 120 #exemple rapide
"""

import argparse
import csv
import json
import os
import sys
import time
from multiprocessing import Pool

# Permet de lancer le script depuis n'importe où.
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from src.config import Parametres, ajouter_arguments_config, appliquer_surcharges
from src.experience import calculer_effectifs, creer_simulation, tirer_positions_initiales  # noqa: F401 (réexportés)


def lancer_essai(tache):
    """
    Exécute un essai complet (sans affichage).

    Paramètre : dictionnaire avec les clés b, essai, graine et parametres (objet Parametres).

    Retourne :
    dict avec 'resume' (une ligne pour essais.csv), 'serie' (SE au cours du temps)
    et 'distances' (distance finale de chaque robot).
    """
    b = tache["b"]
    parametres = tache["parametres"]
    dt = parametres.simulation.dt
    simulation = creer_simulation(b, tache["graine"], parametres)

    nb_pas = int(round(parametres.experience.duree / dt))
    pas_mesure = max(1, int(round(parametres.experience.periode_mesure / dt)))

    serie = [(simulation.temps, simulation.calculer_erreur_segregation())]
    for pas in range(1, nb_pas + 1):
        simulation.effectuer_pas()
        if pas % pas_mesure == 0 or pas == nb_pas:
            serie.append((simulation.temps, simulation.calculer_erreur_segregation()))

    # Distances finales au centre, par groupe.
    distances = [(robot.groupe, simulation.calculer_distance_centre(robot)) for robot in simulation.robots]
    petits = [d for g, d in distances if g == 1]
    grands = [d for g, d in distances if g == 2]

    resume = {
        "b": b,
        "essai": tache["essai"],
        "graine": tache["graine"],
        "n1": len(petits),
        "n2": len(grands),
        "se_final": serie[-1][1],
        "distance_moyenne_g1": sum(petits) / len(petits) if petits else float("nan"),
        "distance_moyenne_g2": sum(grands) / len(grands) if grands else float("nan"),
    }
    return {
        "resume": resume,
        "serie": [(b, tache["essai"], t, se) for t, se in serie],
        "distances": [(b, tache["essai"], g, d) for g, d in distances],
    }


# ----------------------------------------------------------------------------------------
# Entrées / sorties
# ----------------------------------------------------------------------------------------

CHAMPS_ESSAIS = ["b", "essai", "graine", "n1", "n2", "se_final", "distance_moyenne_g1", "distance_moyenne_g2"]


def ecrire_csv(chemin, champs, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        writer = csv.writer(fichier)
        writer.writerow(champs)
        writer.writerows(lignes)


def lire_csv(chemin):
    with open(chemin, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier))


def sauvegarder(dossier, resultats, parametres):
    os.makedirs(dossier, exist_ok=True)

    # Copie des paramètres utilisés : permet de refaire ou de comparer l'expérience plus tard.
    parametres.sauvegarder(os.path.join(dossier, "parametres.json"))
    resultats = sorted(resultats, key=lambda r: (r["resume"]["b"], r["resume"]["essai"]))

    ecrire_csv(
        os.path.join(dossier, "essais.csv"), CHAMPS_ESSAIS,
        [[r["resume"][c] for c in CHAMPS_ESSAIS] for r in resultats],
    )
    ecrire_csv(
        os.path.join(dossier, "serie_se.csv"), ["b", "essai", "temps", "se"],
        [ligne for r in resultats for ligne in r["serie"]],
    )
    ecrire_csv(
        os.path.join(dossier, "distances_finales.csv"), ["b", "essai", "groupe", "distance"],
        [ligne for r in resultats for ligne in r["distances"]],
    )


def afficher_resume(dossier):
    """Affiche, pour chaque b, les statistiques que l'article rapporte (moyenne, médiane, essais sans erreur)."""
    import statistics

    lignes = lire_csv(os.path.join(dossier, "essais.csv"))
    valeurs_b = sorted({float(l["b"]) for l in lignes})

    print("\n  b  | essais | SE moyen | SE médian | essais sans erreur")
    print("-----+--------+----------+-----------+-------------------")
    for b in valeurs_b:
        se = [float(l["se_final"]) for l in lignes if float(l["b"]) == b]
        sans_erreur = sum(1 for v in se if v == 0.0)
        print(f"{b:4g} | {len(se):6d} | {100 * statistics.mean(se):7.2f}% | {100 * statistics.median(se):8.2f}% | {sans_erreur}/{len(se)}")


# ----------------------------------------------------------------------------------------
# Figures (analogues aux figures 7, 8 et 9 de l'article)
# ----------------------------------------------------------------------------------------

def tracer_figures(dossier):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    essais = lire_csv(os.path.join(dossier, "essais.csv"))
    distances = lire_csv(os.path.join(dossier, "distances_finales.csv"))
    serie = lire_csv(os.path.join(dossier, "serie_se.csv"))
    valeurs_b = sorted({float(l["b"]) for l in essais})

    # Figure 7 : SE final en fonction de b.
    fig, ax = plt.subplots(figsize=(6, 4.5))
    donnees = [[float(l["se_final"]) for l in essais if float(l["b"]) == b] for b in valeurs_b]
    ax.boxplot(donnees, tick_labels=[f"{b:g}" for b in valeurs_b])
    ax.set_xlabel("Facteur de rayon b")
    ax.set_ylabel("Erreur de ségrégation (SE)")
    ax.set_ylim(-0.02, 1.0)
    ax.set_title("Erreur de ségrégation finale selon b")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "figure_se_vs_b.png"), dpi=150)
    plt.close(fig)

    # Figure 8 : distances finales au centre, par groupe.
    fig, ax = plt.subplots(figsize=(7, 4.5))
    largeur = 0.35
    for groupe, couleur, decalage in ((1, "tab:blue", -largeur / 2), (2, "tab:orange", largeur / 2)):
        donnees = [
            [float(l["distance"]) for l in distances if float(l["b"]) == b and int(l["groupe"]) == groupe]
            for b in valeurs_b
        ]
        positions = [i + 1 + decalage for i in range(len(valeurs_b))]
        boite = ax.boxplot(donnees, positions=positions, widths=largeur * 0.9, patch_artist=True)
        for patch in boite["boxes"]:
            patch.set_facecolor(couleur)
    ax.set_xticks(range(1, len(valeurs_b) + 1))
    ax.set_xticklabels([f"{b:g}" for b in valeurs_b])
    ax.set_xlabel("Facteur de rayon b")
    ax.set_ylabel("Distance au centre (m)")
    ax.set_title("Distances finales au centre (bleu : petits, orange : grands)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "figure_distances_vs_b.png"), dpi=150)
    plt.close(fig)

    # Figure 9 : SE au cours du temps, une courbe par essai, un panneau par b.
    fig, axes = plt.subplots(1, len(valeurs_b), figsize=(3.2 * len(valeurs_b), 3.6), sharey=True, squeeze=False)
    for ax, b in zip(axes[0], valeurs_b):
        essais_b = sorted({int(l["essai"]) for l in serie if float(l["b"]) == b})
        for essai in essais_b:
            points = [(float(l["temps"]) / 60, float(l["se"])) for l in serie
                      if float(l["b"]) == b and int(l["essai"]) == essai]
            ax.plot([p[0] for p in points], [p[1] for p in points], linewidth=0.8, alpha=0.7)
        ax.set_title(f"b = {b:g}")
        ax.set_xlabel("Temps (min)")
        ax.grid(True, alpha=0.3)
    axes[0][0].set_ylabel("Erreur de ségrégation (SE)")
    fig.tight_layout()
    fig.savefig(os.path.join(dossier, "figure_se_vs_temps.png"), dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------------------
# Programme principal
# ----------------------------------------------------------------------------------------

def analyser_arguments():
    parseur = argparse.ArgumentParser(
        description="Balayage du facteur de rayon b (article Brazil nut effect).",
        epilog="Tous les autres paramètres se règlent dans config.json ou avec --set section.cle=valeur "
               "(liste complète : --afficher-config).",
    )
    ajouter_arguments_config(parseur)
    parseur.add_argument("--b", type=float, nargs="+", help="valeurs de b (remplace experience.valeurs_b)")
    parseur.add_argument("--essais", type=int, help="essais par valeur de b (remplace experience.nb_essais)")
    parseur.add_argument("--duree", type=float, help="durée d'un essai en secondes (remplace experience.duree)")
    parseur.add_argument("--graine", type=int, help="graine de base (remplace experience.graine)")
    parseur.add_argument("--processus", type=int, default=os.cpu_count() or 1, help="nombre de processus en parallèle")
    parseur.add_argument("--sortie", default=os.path.join(RACINE, "results"), help="dossier de sortie (défaut : results/)")
    parseur.add_argument("--figures-seulement", action="store_true", help="ne pas relancer les essais, refaire les figures depuis les CSV")
    return parseur.parse_args()


def construire_parametres(args):
    """Priorité : valeurs par défaut < fichier de config < options --b/--essais/... < --set."""
    parametres = Parametres.charger(args.config)

    surcharges = []
    if args.b is not None:
        surcharges.append(f"experience.valeurs_b={json.dumps([int(b) if b.is_integer() else b for b in args.b])}")
    if args.essais is not None:
        surcharges.append(f"experience.nb_essais={args.essais}")
    if args.duree is not None:
        surcharges.append(f"experience.duree={args.duree}")
    if args.graine is not None:
        surcharges.append(f"experience.graine={args.graine}")

    return appliquer_surcharges(parametres, surcharges + args.surcharges)


def main():
    args = analyser_arguments()

    try:
        parametres = construire_parametres(args)
    except (ValueError, FileNotFoundError) as erreur:
        sys.exit(f"Erreur de configuration : {erreur}")

    if args.afficher_config:
        print(parametres.texte_aide())
        return

    if args.figures_seulement:
        tracer_figures(args.sortie)
        afficher_resume(args.sortie)
        print(f"Figures régénérées dans {args.sortie}")
        return

    e = parametres.experience

    # Une graine distincte par (b, essai), déterministe.
    taches = []
    for index_b, b in enumerate(e.valeurs_b):
        for essai in range(e.nb_essais):
            taches.append({"b": b, "essai": essai, "graine": e.graine + 1000 * index_b + essai, "parametres": parametres})

    print(f"{len(taches)} essais ({len(e.valeurs_b)} valeurs de b x {e.nb_essais}), "
          f"{e.duree:.0f} s simulées chacun, {args.processus} processus.")

    debut = time.time()
    resultats = []
    with Pool(args.processus) as pool:
        for i, resultat in enumerate(pool.imap_unordered(lancer_essai, taches), start=1):
            resultats.append(resultat)
            r = resultat["resume"]
            print(f"[{i:3d}/{len(taches)}] b={r['b']:g} essai={r['essai']:2d} "
                  f"SE={r['se_final']:.3f}  ({time.time() - debut:.0f} s écoulées)", flush=True)

    sauvegarder(args.sortie, resultats, parametres)
    tracer_figures(args.sortie)
    afficher_resume(args.sortie)
    print(f"\nRésultats, paramètres utilisés et figures écrits dans {args.sortie}")


if __name__ == "__main__":
    main()