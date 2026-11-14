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