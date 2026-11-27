import math
import random
from src.config import ParametresArticle, ParametresControleur


class Controleur :
    """ 
    Représente le contrôleur autonome des robots.
    
    Responsabilités : 
        - Déterminer le comportement des robots.
        - Prendre en compte l'attraction vers la lumière.
        - Prendre en compte la répulsion entre robots.
        - Ajouter une composante de mouvement aléatoire.
        - Calculer les vitesses des roues gauche et droite.
    
    Le contrôleur utilise les informations de la simulation pour décider des déplacements des robots.
    """
    def __init__(self, simulation, parametres=None):
        
        # Référence à l'environnement de simulation.
        self.simulation = simulation
        
        # Paramètres du contrôleur (poids, vitesses, gain). Voir src/config.py.
        self.parametres = parametres if parametres is not None else ParametresControleur()
    
    def calculer_attraction(self, robot):
        """ 
        Calcule le vecteur unitaire d'attraction d'un robot vers la source lumineuse centrale.
        
        Paramètre :
        robot : robot dont on calcule l'attraction.
        
        Retourne :
        (ax, ay) : composantes du vecteur d'attraction.
        """
        # Récupérer la direction de la lumière.
        angle = self.simulation.calculer_direction_lumiere(robot)
        
        # Calculer les composantes du vecteur unitaire.
        ax = math.cos(angle)
        ay = math.sin(angle)
        
        return (ax, ay)
    
    def calculer_repulsion(self, robot):
        """ 
        Récupère le vecteur de répulsion totale exercée par les voisins du robot.
        
        Paramètre :
        robot : robot dont on calcule la répulsion.
        
        Retourne :
        (rx, ry) : composantes du vecteur de répulsion totale.
        """
        # Demander à la simulation de calculer la répulsion exercée par les voisins.
        rx, ry = self.simulation.calculer_repulsion_totale(robot)
        
        return (rx, ry)
    
    def calculer_mouvement_aleatoire(self):
        """ 
        Calcule un vecteur unitaire de direction aléatoire.
        
        Génère un angle aléatoire entre 0 et 2pi. Calcule les composantes du vecteur associé.
        
        Retourne :
        (nx, ny) : composante du vecteur aléatoire.
        """
        # Génerer un angle aléatoire en radians.
        angle = random.uniform(0, 2 * math.pi)
        
        # Calculer les composantes du vecteur unitaire.
        nx = math.cos(angle)
        ny = math.sin(angle)
        
        return (nx, ny)
    
    def calculer_direction_deplacement(self, robot):
        """ 
        Calcule la direction de déplacement d'un robot en combinant attraction, répulsion et aléatoire.
        
        Paramètre : 
        robot : robot dont on calcule la direction.
        
        Retourne :
        (dx, dy) : composantes du vecteur résultant.
        """
        # Coefficients des comportements (modifiables dans la configuration).
        poids_attraction = self.parametres.poids_attraction
        poids_repulsion = self.parametres.poids_repulsion
        poids_aleatoire = self.parametres.poids_aleatoire
        
        # Calculer les 3 composantes.
        ax, ay = self.calculer_attraction(robot)
        rx, ry = self.calculer_repulsion(robot)
        nx, ny = self.calculer_mouvement_aleatoire()
        
        # Combiner les composantes selon leurs poids.
        dx = (poids_attraction * ax) + (poids_repulsion * rx) + (poids_aleatoire * nx)
        dy = (poids_attraction * ay) + (poids_repulsion * ry) + (poids_aleatoire * ny)
        
        return (dx, dy)
    
    def calculer_orientation_cible(self, robot):
        """ 
        Calcule l'orientation cible d'un robot à partir de son vecteur de déplacement.
        
        Paramètre : 
        robot : robot dont on calcule l'orientation.
        
        Retourne :
        angle : orientation cible en radians.
        """
        # Calculer le vecteur de déplacement.
        dx, dy = self.calculer_direction_deplacement(robot)
        
        # Vérifier que le vecteur n'est pas nul.
        if math.hypot(dx, dy) < 1e-12:
            return robot.theta
        
        # Calculer l'angle cible du déplacement.
        angle = math.atan2(dy, dx)
        
        return angle
    
    def calculer_ecart_orientation(self, robot):
        """ 
        Calcule l'écart angulaire entre l'orientation actuelle du robot et son orientation cible.
        
        Paramètre :
        robot : robot dont on calcule l'écart.
        
        Retourne :
        ecart : angle de rotation nécessaire, normalisé entre -pi et pi.
        """
        # Calculer l'orientation cible du robot.
        angle_cible = self.calculer_orientation_cible(robot)
        
        # Calculer la différence avec l'orientation actuelle.
        ecart = angle_cible - robot.theta
        
        # Normaliser l'écart entre -pi et pi.
        ecart = (ecart + math.pi) % (2 * math.pi) - math.pi
        
        return ecart
    
    def calculer_vitesse_rotation(self, robot):
        """ 
        Calcule la vitesse angulaire souhaitée du robot à partir de son écart d'orientation.
        
        Paramètre :
        robot : robot dont on calcule la rotation.
        
        Retourne :
        omega : vitesse angulaire en radians/s
        """
        # Paramètres du contrôleur (modifiables dans la configuration).
        kp = self.parametres.kp_rotation
        vitesse_angulaire_max = self.parametres.vitesse_angulaire_max
        
        # Calcule l'écart entre l'orientation actuelle et l'orientation cible.
        ecart = self.calculer_ecart_orientation(robot)
        
        # Calculer la vitesse de rotation proportionnelle.
        omega = kp * ecart 
        
        # Limiter la vitesse angulaire.
        omega = max(-vitesse_angulaire_max, min(omega, vitesse_angulaire_max))
        
        return omega
    
    def calculer_vitesses_roues(self, robot):
        """ 
        Calcule les vitesses des roues gauche et droite à partir des vitesses linéaire et angulaire souhaitées.
        
        Paramètre :
        robot : robot dont on calcule les vitesses.
        
        Retourne :
        (vg, vd) : vitesses des roues gauche et droite en mètres/s.
        """
        # Vitesse linéaire constante (modifiable dans la configuration).
        vitesse_lineaire = self.parametres.vitesse_lineaire
        
        # Calculer la vitesse angulaire souhaitée.
        omega = self.calculer_vitesse_rotation(robot)
        
        # Récupérer la distance entre les 2 roues.
        distance_roues = robot.distance_roues
        
        # Calculer la vitesse de chaque roue.
        vg = vitesse_lineaire - (omega * distance_roues) / 2
        vd = vitesse_lineaire + (omega * distance_roues) / 2
        
        return (vg, vd)
    
    def appliquer_vitesses_roues(self, robot):
        """ 
        Applique aux roues du robot les vitesses calculées par le contrôleur.
        
        Paramètre :
        robot : robot dont on met à jour les vitesses des roues.
        """
        # Calculer les vitesses des roues.
        vg, vd = self.calculer_vitesses_roues(robot)
        
        # Appliquer les vitesses calculées au robot.
        robot.vitesse_gauche = vg
        robot.vitesse_droite = vd


class ControleurArticle(Controleur) :
    """
    Contrôleur fidèle à l'article (Chen et al., AAMAS 2012, section 2.2).

    Chaque robot répète un cycle de 5 s, synchrone pour tous les robots :
        1. Scan (2,4 s) : le robot tourne sur lui-même pour percevoir ses voisins. Il ne se déplace pas.
        2. Rotation (1,3 s) : il s'oriente vers la direction choisie.
        3. Avance (le reste du cycle, 1,3 s) : il avance en ligne droite.

    La direction est choisie une seule fois par cycle (équation 1) :
        v = v_taxis + c_rand * v_rand + f(v_repul)
    - v_taxis : vecteur unitaire vers la lumière.
    - v_rand : vecteur unitaire de direction aléatoire, conservé pendant tout le cycle.
    - v_repul : somme, sur les voisins, de k * (2*r_i - d_ij) dirigé à l'opposé du voisin (équation 2).
      Chaque robot suppose que ses voisins ont le même rayon virtuel que lui.
      La norme de la somme est plafonnée par f(.).

    La vitesse d'avance est proportionnelle à la norme de v : le maximum possible
    (poids_attraction + poids_aleatoire + plafond_repulsion = 8) correspond à la vitesse maximale du robot.

    Différence restante avec l'article : la perception est exacte (pas de robots fusionnés ni masqués).
    """
    def __init__(self, simulation, parametres=None):
        super().__init__(simulation)

        # Paramètres propres à ce contrôleur. Voir la section [article] de src/config.py.
        self.parametres = parametres if parametres is not None else ParametresArticle()

        # Décision de chaque robot pour le cycle courant : id(robot) -> (numéro de cycle, angle cible, vitesse).
        self.decisions = {}

    def calculer_norme_maximale(self):
        """
        Calcule la norme maximale possible du vecteur résultant (1 + 0.6 + 6.4 = 8 dans l'article).
        """
        p = self.parametres
        return p.poids_attraction + p.poids_aleatoire + p.plafond_repulsion

    def calculer_phase(self):
        """
        Détermine la position dans le cycle de contrôle à partir du temps simulé.

        Retourne :
        (numero_cycle, temps_dans_le_cycle) : le temps est en secondes, entre 0 et duree_cycle.
        """
        p = self.parametres
        temps = self.simulation.temps
        numero_cycle = int(temps / p.duree_cycle + 1e-9)
        temps_dans_cycle = max(0.0, temps - numero_cycle * p.duree_cycle)
        return numero_cycle, temps_dans_cycle

    def calculer_repulsion(self, robot):
        """
        Calcule la répulsion totale selon l'équation 2 de l'article, plafonnée par f(.).

        Pour chaque voisin à moins de 2*r_i : norme = k * (2*r_i - d_ij), avec le chevauchement en cm.

        Retourne :
        (rx, ry) : composantes du vecteur de répulsion totale, de norme au plus plafond_repulsion.
        """
        p = self.parametres
        rx = 0.0
        ry = 0.0

        voisins = self.simulation.detecter_voisins(robot, 2 * robot.rayon_virtuel)
        for voisin in voisins :
            # Chevauchement perçu, converti en centimètres (unité supposée de l'équation 2).
            chevauchement_cm = self.simulation.calculer_chevauchement_virtuel(robot, voisin) * 100.0
            ux, uy = self.simulation.calculer_direction_repulsion(robot, voisin)
            rx += p.k_repulsion * chevauchement_cm * ux
            ry += p.k_repulsion * chevauchement_cm * uy

        # Fonction f(.) : limiter la norme de la répulsion totale.
        norme = math.hypot(rx, ry)
        if norme > p.plafond_repulsion :
            rx *= p.plafond_repulsion / norme
            ry *= p.plafond_repulsion / norme

        return (rx, ry)

    def calculer_direction_deplacement(self, robot):
        """
        Calcule le vecteur résultant de l'équation 1 : attraction + bruit + répulsion plafonnée.

        Retourne :
        (dx, dy) : composantes du vecteur résultant.
        """
        p = self.parametres

        ax, ay = self.calculer_attraction(robot)
        rx, ry = self.calculer_repulsion(robot)
        nx, ny = self.calculer_mouvement_aleatoire()

        dx = (p.poids_attraction * ax) + (p.poids_aleatoire * nx) + rx
        dy = (p.poids_attraction * ay) + (p.poids_aleatoire * ny) + ry

        return (dx, dy)

    def decider(self, robot):
        """
        Choisit l'orientation cible et la vitesse d'avance du robot pour le cycle courant.

        La décision est prise une seule fois par cycle (au début, pendant le scan, quand les robots sont immobiles),
        donc le bruit est conservé pendant tout le cycle.

        Retourne :
        (angle_cible, vitesse_lineaire) : angle en radians, vitesse en m/s.
        """
        numero_cycle, _ = self.calculer_phase()

        decision = self.decisions.get(id(robot))
        if decision is not None and decision[0] == numero_cycle :
            return (decision[1], decision[2])

        dx, dy = self.calculer_direction_deplacement(robot)
        norme = math.hypot(dx, dy)

        if norme < 1e-12 :
            angle_cible = robot.theta
            vitesse = 0.0
        else :
            angle_cible = math.atan2(dy, dx)
            # Vitesse proportionnelle à la norme du vecteur, bornée à la vitesse maximale.
            vitesse = self.parametres.vitesse_max * min(norme, self.calculer_norme_maximale()) / self.calculer_norme_maximale()

        self.decisions[id(robot)] = (numero_cycle, angle_cible, vitesse)
        return (angle_cible, vitesse)

    def calculer_vitesses_roues(self, robot):
        """
        Calcule les vitesses des roues selon la phase du cycle (scan, rotation ou avance).

        Retourne :
        (vg, vd) : vitesses des roues gauche et droite en mètres/s.
        """
        p = self.parametres
        epsilon = 1e-9

        # La décision est prise dès le début du cycle, avant l'éventuel déplacement.
        angle_cible, vitesse = self.decider(robot)
        _, temps_cycle = self.calculer_phase()

        fin_scan = p.duree_scan
        fin_rotation = p.duree_scan + p.duree_rotation

        # Phase 1 : scan. Le robot tourne sur lui-même pour percevoir, sa position ne change pas.
        if temps_cycle < fin_scan - epsilon :
            return (0.0, 0.0)

        # Phase 2 : rotation vers la direction choisie, terminée exactement à la fin de la phase.
        if temps_cycle < fin_rotation - epsilon :
            ecart = (angle_cible - robot.theta + math.pi) % (2 * math.pi) - math.pi
            temps_restant = max(fin_rotation - temps_cycle, self.simulation.dt)
            omega = ecart / temps_restant

            # Limite physique : une roue ne dépasse pas vitesse_max.
            omega_max = 2 * p.vitesse_max / robot.distance_roues
            omega = max(-omega_max, min(omega, omega_max))

            return (-(omega * robot.distance_roues) / 2, (omega * robot.distance_roues) / 2)

        # Phase 3 : avance en ligne droite à la vitesse choisie.
        return (vitesse, vitesse)
