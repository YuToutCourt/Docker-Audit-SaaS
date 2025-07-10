from werkzeug.security import check_password_hash
from entity.user import User

class AuthService:
    """Service pour l'authentification des utilisateurs"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authentifier un utilisateur avec username/password
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            
        Returns:
            User: Objet utilisateur si authentification réussie, None sinon
        """
        if not username or not password:
            return None
            
        # Utiliser login_user qui vérifie le statut enabled=1
        user = User.login_user(username, password)
        
        # Vérifier aussi que l'entreprise de l'utilisateur est active
        if user:
            from entity.company import Company
            company = Company.get_company_by_id(user.id_company)
            if company and company.enabled == 0:
                return None  # Entreprise désactivée
        
        return user
    
    @staticmethod
    def create_user(username, password, company_id, email=None, is_admin=False):
        """
        Créer un nouvel utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe (sera hashé)
            company_id (int): ID de l'entreprise
            email (str): Adresse email (optionnel)
            is_admin (bool): Si l'utilisateur est admin
            
        Returns:
            bool: True si création réussie, False sinon
        """
        try:
            from werkzeug.security import generate_password_hash
            
            user = User()
            user.username = username
            user.password = generate_password_hash(password)  # Hashage explicite
            user.id_company = company_id
            user.email = email
            user.is_admin = is_admin
            user.enabled = 1
            
            return user.add()
        except Exception as e:
            print(f"Erreur création utilisateur: {e}")
            return False 