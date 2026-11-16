import math
import random
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
    def __init__(self, simulation):
        
        # Référence à l'environnement de simulation.
        self.simulation = simulation
    
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
        # Définir les coefficients des comportements.
        poids_attraction = 1.0
        poids_repulsion = 10.0
        poids_aleatoire = 0.1
        
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
        # Définir les paramètres du contrôleur.
        kp = 2.0
        vitesse_angulaire_max = 2.0
        
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
        # Définir une vitesse linéaire constante.
        vitesse_lineaire = 0.05
        
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
