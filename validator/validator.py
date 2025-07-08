import base64
from datetime import datetime

class Validator:
    def __init__(self):
        self.rules = {
            
        }
    
    def check_param(self, **kwargs):
        """
        Vérifie la validité des paramètres envoyés.
        """
        # Vérification du token (optionnel)
        token = kwargs.get('token')
        if token is not None:
            if len(token) > 255:
                raise ValueError("Token length is incorrect.")

        # Vérification de la date
        date = kwargs.get('date')
        if date is not None:
            if len(date) != 19:
                raise ValueError("Date length is incorrect. Expected format: 'YYYY-MM-DD HH:MM:SS'")
            try:
                datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError("Invalid date format. Expected format: 'YYYY-MM-DD HH:MM:SS'")

        # Vérification du data (optionnel)
        if 'data' in kwargs:
            data = kwargs.get('data')
            if not data or not isinstance(data, str):
                raise ValueError("Data is required and must be a string")
            try:
                base64.b64decode(data, validate=True)
            except Exception:
                raise ValueError("Data must be in base64 format")

        # Vérification de id_agent (optionnel)
        if 'id_agent' in kwargs:
            id_agent = kwargs.get('id_agent')
            if not id_agent or not isinstance(id_agent, int):
                raise ValueError("ID agent is required and must be an integer")

        # Vérification du name (optionnel)
        if 'name' in kwargs:
            name = kwargs.get('name')
            if not name or not isinstance(name, str):
                raise ValueError("Name is required and must be a string")
            if len(name) > 255:
                raise ValueError("Name length is too long (max 255 characters)")