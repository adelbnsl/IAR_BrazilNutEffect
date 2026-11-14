import math
class Robot :
    """
    Représente un robot mobile dans la simulation.
    
    Chaque robot possède :
        - Une position (x,y) dans l'arène.
        - Une orientation theta en radians.
        - Un rayon virtuel utilisé par le contrôleur.
        - Une vitesse pour chacune de ses deux roues.
    """
    
    def __init__(self, x, y, theta, rayon_virtuel):
        # Position initiale du robots (en mètres).
        self.x = x
        self.y = y
        
        # Orientation initiale (en radians).
        self.theta = theta
        
        # Rayon virtuel du robot (en mètres).
        self.rayon_virtuel = rayon_virtuel
        
        # Rayon physique du robot (en mètres). Utilisé pour les collisions avec les murs et les autres robots.
        self.rayon_physique = 0.035
        
        # Vitesse initiales des roues (en m/s).
        self.vitesse_gauche = 0.0
        self.vitesse_droite = 0.0 
        
        # Distance entre les deux roues du robot (en mètres).
        self.distance_roues = 0.053 
    
    
    def calculer_vitesse_lineaire(self):
        """
        Calcule la vitesse linéaire du robot à partir des vitesses de ses 2 roues.
        
        Retourne : float : vitesse linéaire en m/s. 
        """
        return (self.vitesse_gauche + self.vitesse_droite) / 2
    
    def calculer_vitesse_angulaire(self):
        """ 
        Calcule la vitesse angulaire du robot à partir des vitesses de ses 2 roues.
        
        Retourne : float : vitesse angulaire en rad/s.
        """
        return (self.vitesse_droite - self.vitesse_gauche) / self.distance_roues
    
    def mettre_a_jour_orientation(self, dt):
        """ 
        Met à jour l'orientation du robot.
        
        Paramètre : dt (float) : durée du pas de simulation en secondes.
        """
        omega = self.calculer_vitesse_angulaire()
        self.theta += omega * dt
        
    def mettre_a_jour_position(self, dt):
        """ 
        Met à jour la position du robot selon sa vitesse linéaire et son orientation.
        
        Paramètre : dt (float) : durée du pas de simulation en secondes.
        """
        v = self.calculer_vitesse_lineaire()
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        
    def deplacer(self, dt):
        """ 
        Effectue un pas de déplacement complet du robot.
        
        Fontionnement : 
        1. Met à jour la position avec l'orientation actuelle.
        2. Met à jour l'orientation selon la vitesse angulaire.
        
        Paramètre :
        dt (float) : durée du pas de simulation en secondes. 
        """
        self.mettre_a_jour_position(dt)
        self.mettre_a_jour_orientation(dt)