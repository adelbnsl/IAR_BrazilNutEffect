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