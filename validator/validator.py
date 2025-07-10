import re

class Validator:
    """Classe pour valider les paramètres"""
    
    def check_param(self, **kwargs):
        """
        Valider les paramètres fournis
        
        Args:
            **kwargs: Paramètres à valider
            
        Raises:
            ValueError: Si un paramètre est invalide
        """
        for param_name, value in kwargs.items():
            if value is None:
                raise ValueError(f"Le paramètre {param_name} ne peut pas être None")
            
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"Le paramètre {param_name} ne peut pas être vide")

            # Validation spécifique selon le paramètre
            if param_name == "username":
                self._validate_username(value)
            elif param_name == "password":
                self._validate_password(value)
            elif param_name == "name":
                self._validate_name(value)
            elif param_name == "id_company":
                self._validate_id(value)
    
    def _validate_username(self, username):
        """
        Valider un nom d'utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            
        Raises:
            ValueError: Si le nom d'utilisateur est invalide
        """
        if len(username) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        
        if len(username) > 50:
            raise ValueError("Le nom d'utilisateur ne peut pas dépasser 50 caractères")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores")
    
    def _validate_password(self, password):
        """
        Valider un mot de passe
        
        Args:
            password (str): Mot de passe
            
        Raises:
            ValueError: Si le mot de passe est invalide
        """
        if len(password) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères")
        
        if len(password) > 100:
            raise ValueError("Le mot de passe ne peut pas dépasser 100 caractères")
    
    def _validate_name(self, name):
        """
        Valider un nom
        
        Args:
            name (str): Nom
            
        Raises:
            ValueError: Si le nom est invalide
        """
        if len(name) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        
        if len(name) > 100:
            raise ValueError("Le nom ne peut pas dépasser 100 caractères")
        
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            raise ValueError("Le nom ne peut contenir que des lettres, chiffres, espaces, tirets et underscores")
    
    def _validate_id(self, id_value):
        """
        Valider un ID
        
        Args:
            id_value: ID à valider
            
        Raises:
            ValueError: Si l'ID est invalide
        """
        try:
            id_int = int(id_value)
            if id_int <= 0:
                raise ValueError("L'ID doit être un nombre positif")
        except (ValueError, TypeError):
            raise ValueError("L'ID doit être un nombre entier valide")