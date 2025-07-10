from entity.agent import Agent
from entity.report import Report

class AgentService:
    """Service pour la gestion des agents"""
    
    @staticmethod
    def get_agents_by_company(company_id):
        """
        Récupérer tous les agents d'une entreprise
        
        Args:
            company_id (int): ID de l'entreprise
            
        Returns:
            list: Liste des agents
        """
        try:
            agents = Agent.get_by_company(company_id)
            return [agent.to_dict() for agent in agents]
        except Exception as e:
            print(f"Erreur récupération agents: {e}")
            return []
    
    @staticmethod
    def get_agent_by_id_and_company(agent_id, company_id):
        """
        Récupérer un agent par ID et entreprise
        
        Args:
            agent_id (int): ID de l'agent
            company_id (int): ID de l'entreprise
            
        Returns:
            dict: Données de l'agent ou None
        """
        try:
            agent = Agent.get_by_id_and_company(agent_id, company_id)
            return agent.to_dict() if agent else None
        except Exception as e:
            print(f"Erreur récupération agent: {e}")
            return None
    
    @staticmethod
    def create_agent(name, company_id):
        """
        Créer un nouvel agent
        
        Args:
            name (str): Nom de l'agent
            company_id (int): ID de l'entreprise
            
        Returns:
            bool: True si création réussie, False sinon
        """
        try:
            from datetime import datetime, timedelta
            from pki.certificate_manager import generate_agent_pki
            
            agent = Agent()
            agent.name = name
            agent.id_company = company_id
            agent.enabled = 1
            agent.next_scan_date_ = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            agent.health_check = 1  # Booléen : 1 pour OK
            agent.scan_interval = 86400  # 24 heures par défaut
            
            # Récupérer l'ID de la CA pour cette entreprise
            from entity.company import Company
            company = Company.get_company_by_id(company_id)
            if company:
                agent.id_ca = company.company_pki_id
                
                # Générer les certificats pour l'agent
                try:
                    cert_data = generate_agent_pki(company_id, name)
                    agent.public_key = cert_data["pub"]
                    agent.private_key = cert_data["priv"]
                except Exception as e:
                    print(f"Erreur génération certificats: {e}")
                    # Continuer sans certificats pour l'instant
            
            return agent.add()
        except Exception as e:
            print(f"Erreur création agent: {e}")
            return False
    
    @staticmethod
    def update_agent(agent_id, company_id, data):
        """
        Mettre à jour un agent
        
        Args:
            agent_id (int): ID de l'agent
            company_id (int): ID de l'entreprise
            data (dict): Nouvelles données
            
        Returns:
            bool: True si mise à jour réussie, False sinon
        """
        try:
            agent = Agent.get_by_id_and_company(agent_id, company_id)
            if not agent:
                return False
            
            # Mettre à jour les champs
            if 'name' in data:
                agent.name = data['name']
            if 'enabled' in data:
                agent.enabled = data['enabled']
            if 'scan_interval' in data:
                agent.scan_interval = data['scan_interval']
            
            return agent.update()
        except Exception as e:
            print(f"Erreur mise à jour agent: {e}")
            return False
    
    @staticmethod
    def delete_agent(agent_id, company_id):
        """
        Supprimer un agent
        
        Args:
            agent_id (int): ID de l'agent
            company_id (int): ID de l'entreprise
            
        Returns:
            bool: True si suppression réussie, False sinon
        """
        try:
            from database.database import Database
            
            db = Database()
            agent = db.session.query(Agent).filter_by(id_agent=agent_id, id_company=company_id).first()
            
            if not agent:
                db.close()
                return False
            
            db.session.delete(agent)
            db.session.commit()
            db.close()
            return True
        except Exception as e:
            print(f"Erreur suppression agent: {e}")
            return False
    
    @staticmethod
    def get_agent_certificate(agent_id, company_id):
        """
        Récupérer le certificat d'un agent
        
        Args:
            agent_id (int): ID de l'agent
            company_id (int): ID de l'entreprise
            
        Returns:
            dict: Données du certificat ou None
        """
        try:
            # Récupérer l'agent directement
            agent = Agent.get_by_id_and_company(agent_id, company_id)
            if not agent:
                return None
            
            # Retourner la clé publique de l'agent
            return {
                "certificate": agent.public_key,  # La clé publique de l'agent
                "private_key": agent.private_key  # La clé privée de l'agent (optionnel)
            }
        except Exception as e:
            print(f"Erreur récupération certificat: {e}")
            return None
    
    @staticmethod
    def get_agent_reports(agent_id, company_id):
        """
        Récupérer les rapports d'un agent
        
        Args:
            agent_id (int): ID de l'agent
            company_id (int): ID de l'entreprise
            
        Returns:
            list: Liste des rapports
        """
        try:
            reports = Report.get_by_agent_and_company(agent_id, company_id)
            return [report.to_dict() for report in reports]
        except Exception as e:
            print(f"Erreur récupération rapports: {e}")
            return []
    
    @staticmethod
    def get_all_reports_by_company(company_id):
        """
        Récupérer tous les rapports d'une entreprise
        
        Args:
            company_id (int): ID de l'entreprise
            
        Returns:
            list: Liste des rapports
        """
        try:
            reports = Report.get_by_company(company_id)
            return [report.to_dict() for report in reports]
        except Exception as e:
            print(f"Erreur récupération rapports: {e}")
            return []
    
    @staticmethod
    def download_report(agent_id, report_id, company_id, password):
        """
        Télécharger un rapport déchiffré
        
        Args:
            agent_id (int): ID de l'agent
            report_id (int): ID du rapport
            company_id (int): ID de l'entreprise
            password (str): Mot de passe pour déchiffrer
            
        Returns:
            bytes: Données PDF déchiffrées ou None
        """
        try:
            report = Report.get_by_id_and_agent_and_company(report_id, agent_id, company_id)
            if not report:
                return None
            
            # Logique de déchiffrement ici
            # Pour l'instant, retourner les données brutes
            return report.encrypted_data
        except Exception as e:
            print(f"Erreur téléchargement rapport: {e}")
            return None 

    @staticmethod
    def get_agent_name_by_id(agent_id):
        """
        Récupérer le nom d'un agent par ID
        """
        agent = Agent.get_by_id(agent_id)
        return agent.name if agent else None