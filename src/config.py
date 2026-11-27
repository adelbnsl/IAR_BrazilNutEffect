"""
Paramètres de l'expérimentation, regroupés au même endroit.

Trois façons de les modifier, de la plus durable à la plus ponctuelle :

1. Modifier les valeurs par défaut ci-dessous (chaque paramètre a son unité et sa description).
2. Éditer le fichier `config.json` à la racine du projet. Il est chargé automatiquement s'il existe.
   Il n'a pas besoin de tout contenir : les paramètres absents gardent leur valeur par défaut.
   Les clés qui commencent par "_" sont ignorées (utile pour ajouter des commentaires).
3. En ligne de commande, pour un essai : --config autre.json et/ou --set section.cle=valeur
   Exemple : python main.py --set controleur.poids_aleatoire=0.6 --set visualisation.b=2

Ordre de priorité (le dernier gagne) : valeurs par défaut < config.json (ou --config) < --set.

Pour voir tous les paramètres avec leur valeur courante : python main.py --afficher-config
"""

import json
import os
from dataclasses import dataclass, field, fields

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_CONFIG_PAR_DEFAUT = os.path.join(RACINE, "config.json")


def _param(defaut, unite, aide):
    """Déclare un paramètre avec son unité et sa description."""
    if isinstance(defaut, list):
        return field(default_factory=lambda: list(defaut), metadata={"unite": unite, "aide": aide})
    return field(default=defaut, metadata={"unite": unite, "aide": aide})


# ----------------------------------------------------------------------------------------
# Sections de paramètres
# ----------------------------------------------------------------------------------------

@dataclass
class ParametresArene:
    cote: float = _param(2.5, "m", "Côté de l'arène carrée. La source lumineuse est placée au centre.")


@dataclass
class ParametresRobot:
    rayon_physique: float = _param(0.035, "m", "Rayon du corps réel du robot (e-puck : 3,5 cm). Sert aux collisions.")
    distance_roues: float = _param(0.053, "m", "Distance entre les deux roues (e-puck : 5,3 cm).")


@dataclass
class ParametresControleur:
    mode: str = _param("simple", "-", "Contrôleur utilisé : \"simple\" (celui du projet, paramètres ci-dessous) "
                                      "ou \"article\" (fidèle à l'article, paramètres de la section [article]).")
    poids_attraction: float = _param(1.0, "-", "Poids de l'attraction vers la lumière (article : 1).")
    poids_repulsion: float = _param(10.0, "-", "Poids de la répulsion entre robots. Appliqué à des chevauchements en mètres.")
    poids_aleatoire: float = _param(0.1, "-", "Poids du mouvement aléatoire, qui joue le rôle de la vibration (article : 0.6).")
    kp_rotation: float = _param(2.0, "1/s", "Gain proportionnel de la rotation vers l'orientation cible.")
    vitesse_angulaire_max: float = _param(2.0, "rad/s", "Vitesse de rotation maximale.")
    vitesse_lineaire: float = _param(0.05, "m/s", "Vitesse d'avance constante (e-puck : 0,128 m/s au maximum).")


@dataclass
class ParametresArticle:
    """Paramètres du contrôleur fidèle à l'article (utilisés si controleur.mode = "article")."""
    poids_attraction: float = _param(1.0, "-", "Poids de l'attraction vers la lumière (vecteur unitaire).")
    poids_aleatoire: float = _param(0.6, "-", "Poids c_rand du mouvement aléatoire (article : 0.6).")
    k_repulsion: float = _param(0.2, "1/cm", "Coefficient k de l'équation 2 : répulsion = k * (2r - d), avec 2r - d en cm (unité supposée).")
    plafond_repulsion: float = _param(6.4, "-", "Norme maximale de la répulsion totale, fonction f(.) de l'équation 1 (article : 6.4).")
    vitesse_max: float = _param(0.128, "m/s", "Vitesse maximale du robot, atteinte quand la norme du vecteur résultant vaut son maximum (e-puck : 12,8 cm/s).")
    duree_cycle: float = _param(5.0, "s", "Durée d'un cycle de contrôle (article : 5 s).")
    duree_scan: float = _param(2.4, "s", "Début de cycle : le robot tourne sur lui-même pour percevoir ses voisins, sans se déplacer.")
    duree_rotation: float = _param(1.3, "s", "Le robot s'oriente vers la direction choisie. Le reste du cycle (1,3 s par défaut) est consacré à l'avance.")


@dataclass
class ParametresSimulation:
    dt: float = _param(0.1, "s", "Durée d'un pas de simulation.")
    nb_iterations_collisions: int = _param(20, "-", "Passages de correction des collisions à chaque pas.")
    tolerance_collision: float = _param(0.0001, "m", "Chevauchement physique toléré entre deux robots.")


@dataclass
class ParametresGroupes:
    n_robots: int = _param(20, "-", "Nombre total de robots.")
    rayon_base: float = _param(0.08, "m", "Rayon virtuel a du petit groupe (article : 8 cm). Le grand groupe a pour rayon a*b.")
    effectifs: list = _param(None, "-", "Robots par groupe, par exemple [10, 10]. null : répartition automatique (équation 4 de l'article).")


@dataclass
class ParametresPlacement:
    pas_grille: float = _param(0.20, "m", "Espacement des points de la grille de départ (article : 20 cm).")
    taille_grille: int = _param(6, "-", "La grille de départ est carrée, de taille_grille x taille_grille points (article : 6).")


@dataclass
class ParametresExperience:
    valeurs_b: list = _param([1, 2, 3, 4, 5], "-", "Facteurs de rayon b à balayer (rayon du grand groupe = rayon_base * b).")
    nb_essais: int = _param(20, "-", "Nombre d'essais par valeur de b.")
    duree: float = _param(1200.0, "s", "Durée simulée d'un essai (article : 20 minutes).")
    periode_mesure: float = _param(10.0, "s", "Période d'enregistrement de l'erreur de ségrégation.")
    graine: int = _param(0, "-", "Graine de base du générateur aléatoire (reproductibilité).")


@dataclass
class ParametresVisualisation:
    b: float = _param(3.0, "-", "Facteur de rayon utilisé par main.py (animation).")
    intervalle_ms: int = _param(100, "ms", "Délai entre deux images de l'animation.")
    pas_par_image: int = _param(1, "-", "Pas de simulation avancés entre deux images (augmenter pour accélérer).")


@dataclass
class Parametres:
    arene: ParametresArene = field(default_factory=ParametresArene)
    robot: ParametresRobot = field(default_factory=ParametresRobot)
    controleur: ParametresControleur = field(default_factory=ParametresControleur)
    article: ParametresArticle = field(default_factory=ParametresArticle)
    simulation: ParametresSimulation = field(default_factory=ParametresSimulation)
    groupes: ParametresGroupes = field(default_factory=ParametresGroupes)
    placement: ParametresPlacement = field(default_factory=ParametresPlacement)
    experience: ParametresExperience = field(default_factory=ParametresExperience)
    visualisation: ParametresVisualisation = field(default_factory=ParametresVisualisation)

    # ------------------------------------------------------------------------------------
    # Conversion dictionnaire / JSON
    # ------------------------------------------------------------------------------------

    def vers_dict(self):
        """Retourne tous les paramètres sous forme de dictionnaire {section: {cle: valeur}}."""
        resultat = {}
        for section in fields(self):
            valeurs = getattr(self, section.name)
            resultat[section.name] = {
                champ.name: (list(getattr(valeurs, champ.name)) if isinstance(getattr(valeurs, champ.name), list)
                             else getattr(valeurs, champ.name))
                for champ in fields(valeurs)
            }
        return resultat

    @classmethod
    def depuis_dict(cls, donnees):
        """
        Construit les paramètres à partir d'un dictionnaire (partiel ou complet).

        Les paramètres absents gardent leur valeur par défaut. Les clés qui commencent par "_" sont ignorées.
        Lève ValueError si une section ou un paramètre est inconnu (ce qui détecte les fautes de frappe),
        ou si une valeur est invalide.
        """
        parametres = cls()
        sections = {section.name: section for section in fields(cls)}

        for nom_section, valeurs in donnees.items():
            if nom_section.startswith("_"):
                continue
            if nom_section not in sections:
                raise ValueError(f"Section inconnue : '{nom_section}'. Sections valides : {', '.join(sections)}.")
            if not isinstance(valeurs, dict):
                raise ValueError(f"La section '{nom_section}' doit contenir un objet {{...}}.")

            objet_section = getattr(parametres, nom_section)
            champs = {champ.name: champ for champ in fields(objet_section)}
            for cle, valeur in valeurs.items():
                if cle.startswith("_"):
                    continue
                if cle not in champs:
                    raise ValueError(f"Paramètre inconnu : '{nom_section}.{cle}'. Paramètres valides : {', '.join(champs)}.")
                setattr(objet_section, cle, _convertir(f"{nom_section}.{cle}", valeur, getattr(objet_section, cle), champs[cle]))

        parametres.valider()
        return parametres

    @classmethod
    def charger(cls, chemin=None):
        """
        Charge les paramètres depuis un fichier JSON.

        Si chemin est None, charge config.json à la racine du projet s'il existe,
        sinon retourne les valeurs par défaut.
        """
        if chemin is None:
            if not os.path.exists(CHEMIN_CONFIG_PAR_DEFAUT):
                return cls()
            chemin = CHEMIN_CONFIG_PAR_DEFAUT
        elif not os.path.exists(chemin):
            raise FileNotFoundError(f"Fichier de configuration introuvable : {chemin}")

        with open(chemin, encoding="utf-8") as fichier:
            try:
                donnees = json.load(fichier)
            except json.JSONDecodeError as erreur:
                raise ValueError(f"{chemin} n'est pas un JSON valide : {erreur}") from erreur
        return cls.depuis_dict(donnees)

    def sauvegarder(self, chemin):
        """Écrit tous les paramètres dans un fichier JSON."""
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(self.vers_dict(), fichier, indent=2, ensure_ascii=False)
            fichier.write("\n")

    # ------------------------------------------------------------------------------------
    # Validation et affichage
    # ------------------------------------------------------------------------------------

    def valider(self):
        """Vérifie la cohérence des paramètres. Lève ValueError sinon."""
        def exiger(condition, message):
            if not condition:
                raise ValueError(message)

        exiger(self.arene.cote > 0, "arene.cote doit être > 0.")
        exiger(self.robot.rayon_physique > 0, "robot.rayon_physique doit être > 0.")
        exiger(self.robot.distance_roues > 0, "robot.distance_roues doit être > 0.")

        c = self.controleur
        exiger(c.poids_attraction >= 0 and c.poids_repulsion >= 0 and c.poids_aleatoire >= 0,
               "Les poids du contrôleur doivent être >= 0.")
        exiger(c.vitesse_lineaire >= 0, "controleur.vitesse_lineaire doit être >= 0.")
        exiger(c.vitesse_angulaire_max > 0, "controleur.vitesse_angulaire_max doit être > 0.")
        exiger(c.kp_rotation > 0, "controleur.kp_rotation doit être > 0.")

        exiger(c.mode in ("simple", "article"), 'controleur.mode doit valoir "simple" ou "article".')

        a = self.article
        exiger(a.poids_attraction >= 0 and a.poids_aleatoire >= 0 and a.k_repulsion >= 0,
               "article.poids_attraction, article.poids_aleatoire et article.k_repulsion doivent être >= 0.")
        exiger(a.poids_attraction + a.poids_aleatoire + a.plafond_repulsion > 0 and a.plafond_repulsion >= 0,
               "article.plafond_repulsion doit être >= 0 et la somme des poids maximale > 0.")
        exiger(a.vitesse_max > 0, "article.vitesse_max doit être > 0.")
        exiger(a.duree_scan >= 0 and a.duree_rotation >= 0, "article.duree_scan et article.duree_rotation doivent être >= 0.")
        exiger(a.duree_scan + a.duree_rotation < a.duree_cycle,
               "article.duree_scan + article.duree_rotation doit être < article.duree_cycle (il faut du temps pour avancer).")

        exiger(self.simulation.dt > 0, "simulation.dt doit être > 0.")
        exiger(self.simulation.nb_iterations_collisions >= 1, "simulation.nb_iterations_collisions doit être >= 1.")
        exiger(self.simulation.tolerance_collision >= 0, "simulation.tolerance_collision doit être >= 0.")

        g = self.groupes
        exiger(g.n_robots >= 2, "groupes.n_robots doit être >= 2.")
        exiger(g.rayon_base > 0, "groupes.rayon_base doit être > 0.")
        if g.effectifs is not None:
            exiger(isinstance(g.effectifs, list) and len(g.effectifs) == 2
                   and all(isinstance(e, int) and e >= 0 for e in g.effectifs),
                   "groupes.effectifs doit être null ou une liste de 2 entiers, par exemple [10, 10].")
            exiger(sum(g.effectifs) == g.n_robots,
                   f"groupes.effectifs ({g.effectifs}) doit sommer à groupes.n_robots ({g.n_robots}).")

        exiger(self.placement.pas_grille > 0, "placement.pas_grille doit être > 0.")
        exiger(self.placement.taille_grille >= 1, "placement.taille_grille doit être >= 1.")
        exiger(g.n_robots <= self.placement.taille_grille ** 2,
               f"Pas assez de points de départ : {g.n_robots} robots pour une grille de "
               f"{self.placement.taille_grille}x{self.placement.taille_grille}.")
        exiger((self.placement.taille_grille - 1) * self.placement.pas_grille < self.arene.cote,
               "La grille de départ dépasse de l'arène (placement.pas_grille ou taille_grille trop grand).")

        e = self.experience
        exiger(len(e.valeurs_b) >= 1 and all(b > 0 for b in e.valeurs_b), "experience.valeurs_b doit contenir des valeurs > 0.")
        exiger(e.nb_essais >= 1, "experience.nb_essais doit être >= 1.")
        exiger(e.duree > 0, "experience.duree doit être > 0.")
        exiger(e.periode_mesure > 0, "experience.periode_mesure doit être > 0.")

        v = self.visualisation
        exiger(v.b > 0, "visualisation.b doit être > 0.")
        exiger(v.intervalle_ms >= 1, "visualisation.intervalle_ms doit être >= 1.")
        exiger(v.pas_par_image >= 1, "visualisation.pas_par_image doit être >= 1.")

    def texte_aide(self):
        """Retourne un tableau lisible : chaque paramètre, sa valeur courante, son unité et sa description."""
        lignes = []
        for section in fields(self):
            lignes.append(f"\n[{section.name}]")
            valeurs = getattr(self, section.name)
            for champ in fields(valeurs):
                valeur = json.dumps(getattr(valeurs, champ.name))
                unite = champ.metadata.get("unite", "")
                unite = f" {unite}" if unite and unite != "-" else ""
                lignes.append(f"  {section.name}.{champ.name} = {valeur}{unite}")
                lignes.append(f"      {champ.metadata.get('aide', '')}")
        return "\n".join(lignes).lstrip("\n")


def _convertir(nom, valeur, valeur_defaut, champ):
    """Vérifie le type d'une valeur lue dans un fichier ou en ligne de commande, et la convertit si besoin."""
    # effectifs : None ou liste (la validation fine est faite dans valider()).
    if champ.name == "effectifs":
        if valeur is not None and not isinstance(valeur, list):
            raise ValueError(f"{nom} doit être null ou une liste, par exemple [10, 10].")
        return valeur

    if isinstance(valeur_defaut, list):
        if not isinstance(valeur, list) or not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in valeur):
            raise ValueError(f"{nom} doit être une liste de nombres, par exemple [1, 2, 3].")
        return valeur

    if isinstance(valeur_defaut, str):
        if not isinstance(valeur, str):
            raise ValueError(f"{nom} doit être un texte, par exemple \"article\" (reçu : {valeur!r}).")
        return valeur

    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise ValueError(f"{nom} doit être un nombre (reçu : {valeur!r}).")

    if isinstance(valeur_defaut, int):
        if isinstance(valeur, float) and not valeur.is_integer():
            raise ValueError(f"{nom} doit être un entier (reçu : {valeur!r}).")
        return int(valeur)
    return float(valeur)


# ----------------------------------------------------------------------------------------
# Surcharges en ligne de commande
# ----------------------------------------------------------------------------------------

def appliquer_surcharges(parametres, surcharges):
    """
    Applique des surcharges de la forme "section.cle=valeur" et retourne de nouveaux paramètres.

    La valeur est lue comme du JSON : nombre (0.6), liste ([1,2,3]) ou null.
    """
    if not surcharges:
        return parametres

    donnees = parametres.vers_dict()
    for surcharge in surcharges:
        if "=" not in surcharge or "." not in surcharge.split("=", 1)[0]:
            raise ValueError(f"Surcharge invalide : '{surcharge}'. Format attendu : section.cle=valeur")
        chemin, texte = surcharge.split("=", 1)
        section, cle = chemin.strip().split(".", 1)
        try:
            valeur = json.loads(texte)
        except json.JSONDecodeError:
            # Un mot sans guillemets est lu comme du texte (ex. --set controleur.mode=article).
            # Si le paramètre attend un nombre, la validation refusera ce texte avec un message clair.
            valeur = texte.strip()
        if section not in donnees:
            raise ValueError(f"Section inconnue : '{section}'. Sections valides : {', '.join(donnees)}.")
        donnees[section][cle] = valeur
    return Parametres.depuis_dict(donnees)


def ajouter_arguments_config(parseur):
    """Ajoute à un argparse les options communes : --config, --set et --afficher-config."""
    parseur.add_argument("--config", help="fichier JSON de paramètres (défaut : config.json à la racine s'il existe)")
    parseur.add_argument("--set", dest="surcharges", action="append", default=[], metavar="SECTION.CLE=VALEUR",
                         help="surcharge un paramètre, répétable. Exemple : --set controleur.poids_aleatoire=0.6")
    parseur.add_argument("--afficher-config", action="store_true",
                         help="affiche tous les paramètres (valeur, unité, description) et quitte")


if __name__ == "__main__":
    # python -m src.config : affiche la configuration par défaut au format JSON (pour créer config.json).
    print(json.dumps(Parametres().vers_dict(), indent=2, ensure_ascii=False))
