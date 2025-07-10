from entity.user import User
from entity.company import Company
from entity.agent import Agent
from entity.report import Report
from entity.ca import Ca
from services.auth_service import AuthService

class AdminService:
    """Service pour les fonctionnalités admin"""
    
    @staticmethod
    def get_all_users():
        """
        Récupérer tous les utilisateurs
        
        Returns:
            list: Liste des utilisateurs
        """
        try:
            users = User.get_all()
            return [user.to_dict() for user in users]
        except Exception as e:
            print(f"Erreur récupération utilisateurs: {e}")
            return []
    
    @staticmethod
    def create_user(username, password, company_id, email=None):
        """
        Créer un nouvel utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            company_id (int): ID de l'entreprise
            email (str): Adresse email (optionnel)
            
        Returns:
            bool: True si création réussie, False sinon
        """
        return AuthService.create_user(username, password, company_id, email)
    
    @staticmethod
    def delete_user(user_id):
        """
        Supprimer un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
            
        Returns:
            bool: True si suppression réussie, False sinon
        """
        try:
            return User.delete_user_by_id(user_id)
        except Exception as e:
            print(f"Erreur suppression utilisateur: {e}")
            return False
    
    @staticmethod
    def get_all_companies():
        """
        Récupérer toutes les entreprises
        
        Returns:
            list: Liste des entreprises
        """
        try:
            companies = Company.get_all()
            return [company.to_dict() for company in companies]
        except Exception as e:
            print(f"Erreur récupération entreprises: {e}")
            return []
    
    @staticmethod
    def create_company(name):
        """
        Créer une nouvelle entreprise
        
        Args:
            name (str): Nom de l'entreprise
            
        Returns:
            bool: True si création réussie, False sinon
        """
        try:
            from pki.certificate_manager import generate_entreprise_pki
            
            # Générer d'abord le certificat CA pour l'entreprise
            ca_id = generate_entreprise_pki(name)
            
            # Créer l'entreprise avec l'ID de la CA
            company = Company()
            company.name = name
            company.company_pki_id = ca_id
            
            return company.add()
        except Exception as e:
            print(f"Erreur création entreprise: {e}")
            return False
    
    @staticmethod
    def delete_company(company_id):
        """
        Supprimer une entreprise
        
        Args:
            company_id (int): ID de l'entreprise
            
        Returns:
            bool: True si suppression réussie, False sinon
        """
        try:
            return Company.delete_company_by_id(company_id)
        except Exception as e:
            print(f"Erreur suppression entreprise: {e}")
            return False
    
    @staticmethod
    def get_global_stats():
        """
        Récupérer les statistiques globales
        
        Returns:
            dict: Statistiques
        """
        try:
            total_users = len(User.get_all())
            total_companies = len(Company.get_all())
            total_agents = len(Agent.get_all())
            total_reports = len(Report.get_all())
            
            return {
                "total_users": total_users,
                "total_companies": total_companies,
                "total_agents": total_agents,
                "total_reports": total_reports
            }
        except Exception as e:
            print(f"Erreur récupération stats: {e}")
            return {
                "total_users": 0,
                "total_companies": 0,
                "total_agents": 0,
                "total_reports": 0
            } 

    @staticmethod
    def toggle_user_enabled(user_id):
        try:
            user = User.get_user_by_id(user_id)
            if not user:
                return False
            user.enabled = 0 if user.enabled else 1
            return user.update()
        except Exception as e:
            print(f"Erreur activation/désactivation utilisateur: {e}")
            return False 

    @staticmethod
    def toggle_company_enabled(company_id):
        try:
            company = Company.get_company_by_id(company_id)
            if not company:
                return False
            
            # Toggle le statut de l'entreprise
            company.enabled = 0 if company.enabled else 1
            
            # Cascade sur les utilisateurs de cette entreprise
            from entity.user import User
            users = User.get_all()
            for user in users:
                if user.id_company == company_id:
                    user.enabled = company.enabled
                    user.update()
            
            # Cascade sur les agents de cette entreprise
            from entity.agent import Agent
            agents = Agent.get_all()
            for agent in agents:
                if agent.id_company == company_id:
                    agent.enabled = company.enabled
                    agent.update()
            
            return company.update()
        except Exception as e:
            print(f"Erreur activation/désactivation entreprise: {e}")
            return False 