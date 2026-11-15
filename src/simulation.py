import math
class Simulation:
    """ 
    Représente l'environnement de simulation.
    
    Responsabilités :
        - Définir les dimensions de l'arène.
        - Conserver la liste des robots.
        - Suivre le temps écoulé.
        - Gérer ultérieurement les déplacements et les interactions entre robots.
    """
    def __init__(self, largeur, hauteur, robots, dt):
        # Dimensions de l'arène (en mètres).
        self.largeur = largeur
        self.hauteur = hauteur
        
        # Liste des robots présents dans l'arène.
        self.robots = robots
        
        # Durée d'un pas de simulation (en secondes).
        self.dt = dt
        
        # Temps écoulé depuis le début.
        self.temps = 0.0
        
        # Position de la source lumineuse au centre de l'arène.
        self.lumiere_x = self.largeur / 2
        self.lumiere_y = self.hauteur / 2
        
        # Nombre de passages pour corriger les collisions.
        self.nb_iterations_collisions = 8
        
        # Chevauchement maximal toléré entre deux robots (en mètres).
        self.tolerance_collision = 0.0001
    
    def effectuer_pas(self):
        """ 
        Effectue un pas de simulation.
        
        Fonctionnement :
        1. Déplace chaque robot pendant dt secondes.
        2. Vérifie que chaque robot reste dans l'arène.
        3. Met à jour le temps écoulé dans la simulation.
        """
        # Déplacer tous les robots.
        for robot in self.robots :
            robot.deplacer(self.dt)
            # Empêcher le robot de sortir de l'arène.
            self.gerer_limites(robot)
        
        # Résoudre les collisions entre robots sur plusieurs itération.
        for iteration in range(self.nb_iterations_collisions) :
            for i in range(len(self.robots)) :
                for j in range(i + 1, len(self.robots)) :
                    robot1 = self.robots[i]
                    robot2 = self.robots[j]
                    
                    if self.detecter_collision(robot1, robot2) : 
                        self.resoudre_collision(robot1, robot2)
        
            # Nouvellle vérification des limites.
            for robot in self.robots :
                self.gerer_limites(robot)
            
            # Vérifier si la précision demandée est atteinte.
            chevauchement_max = self.calculer_chevauchement_max()
            
            if chevauchement_max <= self.tolerance_collision :
                break
            
        # Avancer le temps de simulation.
        self.temps += self.dt
        
    
    def gerer_limites(self, robot):
        """ 
            Empêche le centre d'un robot de sortir de l'arène.
            
            Paramètre :
            robot : robot dont on vérifie la position.
        """
        
        # Récupérer le rayon physique du robot.
        r = robot.rayon_physique
        
        # Limites horizontales.
        robot.x = max(r, min(self.largeur - r, robot.x))
        
        # Limites verticales.
        robot.y = max(r, min(self.hauteur - r, robot.y))
    
    def calculer_direction_lumiere(self, robot):
        """ 
        Calcule l'angle absolu entre la position du robot et la source lumineur centrale.
        
        Retourne :
        Angle en radians, compris entre -pi et pi.
        """
        dx = self.lumiere_x - robot.x
        dy = self.lumiere_y - robot.y
        
        return math.atan2(dy, dx)
    
    def calculer_ecart_lumiere(self, robot):
        """ 
        Calcule l'écart angulaire entre l'orientation du robot et la direction de la lumière.
        
        Retourne :
        Angle en radians dans [-pi, pi]. Positif : lumière à gauche. Négatif : lumière à droite. 0 : robot orienté vers la lumière.
        """
        direction_lumiere = self.calculer_direction_lumiere(robot)
        ecart = direction_lumiere - robot.theta
        
        # Ramener l'angle dans [-pi, pi].
        ecart = (ecart + math.pi) % (2 * math.pi) - math.pi
        return ecart
    
    
    def calculer_distance_lumiere(self, robot):
        """ 
        Calcule la distance euclidienne entre le robot et la source lumineuse centrale.
        
        Retourne :
        Distance en mètres.
        """     
        dx = self.lumiere_x - robot.x
        dy = self.lumiere_y - robot.y
        
        return math.sqrt(dx**2 + dy**2)
    
    
    def calculer_distance_robots(self, robot1, robot2):
        """ 
        Calcule la distance entre les centres de 2 robots.
        
        Retourne :
        Distance en mètres.
        """
        dx = robot2.x - robot1.x
        dy = robot2.y - robot1.y
        
        return math.sqrt(dx**2 + dy**2)
    
    def detecter_voisins(self, robot, distance_max):
        """ 
        Retourne les robots situé à une distance inférieure ou égale à distance_max.
        
        Paramètres : 
        robot : robot qui effectue la détection.
        distance_max : seuil de détection en mètres.
        
        Retourne :
        Liste des robots voisins détectés.
        """
        
        voisins = []
        for autre_robot in self.robots :
            
            # Un robot ne doit pas se détecter lui-même.
            if autre_robot is robot :
                continue
            
            distance = self.calculer_distance_robots(robot, autre_robot)
            
            if distance <= distance_max : 
                voisins.append(autre_robot)
        return voisins
    
    def calculer_chevauchement_virtuel(self, robot, voisin): 
        """ 
        Calcule le chevauchement virtuel entre un robot et un voisin. 
        
        Le robot suppose que son voisin possède le même rayon virtuel que lui.
        
        Retourne :
        Chevauchement en mètres. 0 si aucune interaction virtuelle.
        """
        distance = self.calculer_distance_robots(robot, voisin)
        
        distance_interaction = 2 * robot.rayon_virtuel
        
        return max(0.0, (distance_interaction - distance))    
    
    def calculer_direction_repulsion(self, robot, voisin):
        """ 
        Calcule un vecteur unitaire dirigé du voisin vers le robot étudié.
        
        Retourne :
        (ux, uy) : direction de répulsion. Si les deux robots occupent exactement la même position, retourne (0.0, 0.0).
        """
        dx = robot.x - voisin.x
        dy = robot.y - voisin.y
        
        distance = self.calculer_distance_robots(robot, voisin)
        
        if distance == 0 :
            return (0.0, 0.0)
        
        ux = dx / distance
        uy = dy / distance
        
        return (ux, uy)
    
    def calculer_repulsion_totale(self, robot):
        """ 
        Calcule la somme des contributions de répulsion virtuelle exercées par les voisins d'un robot.
        
        Retourne :
        (rx, ry) : composant du vecteur résultant.
        """
        rx = 0.0
        ry = 0.0
        
        distance_max = 2 * robot.rayon_virtuel
        
        voisins = self.detecter_voisins(robot, distance_max)
        for voisin in voisins :
            chevauchement = self.calculer_chevauchement_virtuel(robot, voisin)
            
            ux, uy = self.calculer_direction_repulsion(robot, voisin)
            
            rx += chevauchement * ux
            ry += chevauchement * uy
        return (rx, ry)
    
    
    
    def detecter_collision(self, robot1, robot2):
        """ 
        Vérifie si deux robot se chevauchent.
        
        Paramètres :
        robot1 : premier robot.
        robot2 : deuxième robot.
        
        Retourne :
        bool : True si les robots se chevauchent. false sinon.
        """
        # Vecteur entre les centre des robots.
        dx = robot2.x - robot1.x
        dy = robot2.y - robot1.y
        
        # Distance entre les centres
        distance = math.sqrt(dx**2 + dy**2)
        
        # Distance minimale autorisée 
        distance_min = (robot1.rayon_physique + robot2.rayon_physique)
        
        return distance < distance_min
    
    def resoudre_collision(self, robot1, robot2):
        """ 
        Corrige le chevauchement entre deux robots. Les deux robots sont déplacés équitablement dans des directions opposées.
        """
        # Vecteur entre les centre des robots.
        dx = robot2.x - robot1.x
        dy = robot2.y - robot1.y
        
        # Distance entre les centres.
        distance = math.sqrt(dx**2 + dy**2)
        
        # Distance minimale autorisée.
        distance_min = (robot1.rayon_physique + robot2.rayon_physique)
        
        # Aucun chevauchement. 
        if distance >= distance_min :
            return
        
        # Cas particulier : centres exactement superposées.
        if distance == 0 :
            dx = 1.0
            dy = 0.0
            distance = 1.0
        
        # Direction normalisée.
        ux = dx / distance
        uy = dy / distance
        
        # Quantité de chevauchement à corriger.
        chevauchement = distance_min - (math.sqrt((robot2.x - robot1.x)**2 + (robot2.y - robot1.y)**2))
        correction = chevauchement / 2
        
        # Eloigner les deux robots.
        robot1.x -= ux * correction
        robot1.y -= uy * correction
        
        robot2.x += ux * correction
        robot2.y += uy * correction
    
    
    def calculer_chevauchement_max(self):
        """ 
        Calcule le chevauchement maximal entre tous les robots.
        
        Retourne :
        Le chevauchement maximal en mètres. Retourne 0 si aucun robot ne se chevauche.
        """
        chevauchement_max = 0.0
        
        for i in range(len(self.robots)) :
            for j in range(i + 1, len(self.robots)) :
                robot1 = self.robots[i]
                robot2 = self.robots[j]
                
                # Distance entre les centres des robots.
                dx = robot2.x - robot1.x
                dy = robot2.y - robot1.y
                
                distance = math.sqrt(dx**2 + dy**2)
                
                # Distance minimale pour éviter un chevauchement.
                distance_min = (robot1.rayon_physique + robot2.rayon_physique)
                
                # Calculer le chevauchement de cette paire.
                chevauchement = max(0.0, distance_min - distance)
                
                # Conserver le plus grand chevauchement.
                chevauchement_max = max(chevauchement_max, chevauchement)
                
        return chevauchement_max