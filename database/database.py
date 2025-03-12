import os
import mysql.connector
from mysql.connector import Error
from icecream import ic

from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
USER = os.getenv("USER_DB")
PASSWORD = os.getenv("PASSWORD_DB")
DATABASE = os.getenv("DATABASE")
PORT = os.getenv("PORT")

class DataBase:
    def __init__(self):
        """Initialisation de la connexion à la base de données."""
        self.host = HOST
        self.user = USER
        self.password = PASSWORD
        self.database = DATABASE
        self.port = PORT
        self.connection = None
        self.connect()

    def connect(self):
        """Connexion à la base de données."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port 
            )
            if self.connection.is_connected():
                ic("Connexion réussie à la base de données.")

        except Error as e:
            ic(f"Erreur lors de la connexion à MySQL: {e}")
            raise Exception(f"Erreur lors de la connexion à MySQL: {e}")
        
    def close(self):
        """Fermeture de la connexion."""
        if self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """Exécute une requête SQL (INSERT, UPDATE, DELETE)."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            ic(f"Erreur SQL: {e}")
            raise Exception(f"Erreur SQL: {e}")
        
    def fetch_query(self, query, params=None):
        """Exécute une requête SQL (SELECT) et retourne les résultats."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            ic(f"Erreur SQL: {e}")
            raise Exception(f"Erreur SQL: {e}")

    