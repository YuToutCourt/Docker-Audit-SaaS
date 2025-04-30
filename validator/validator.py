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
        token = kwargs.get('token')
        if not token:
            raise ValueError("Company agent token missing")
        
        if len(token) > 255:
            raise ValueError("Token length is incorrect.")

        date = kwargs.get('date')
        if not date:
            raise ValueError("Date is required")
        
        if len(date) != 19:
            raise ValueError("Date length is incorrect. Expected format: 'YYYY-MM-DD HH:MM:SS'")

        try:
            datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Invalid date format. Expected format: 'YYYY-MM-DD HH:MM:SS'")

        data = kwargs.get('data')
        if not data or not isinstance(data, str):
            raise ValueError("Data is required and must be a string")

        try:
            base64.b64decode(data, validate=True)
        except Exception:
            raise ValueError("Data must be in base64 format")

        id_agent = kwargs.get('id_agent')
        if not id_agent or not isinstance(id_agent, int):
            raise ValueError("ID agent is required and must be an integer")