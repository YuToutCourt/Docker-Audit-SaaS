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
            
        user = User.get_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return None
    
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