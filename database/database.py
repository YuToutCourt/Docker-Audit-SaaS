import mysql.connector
from mysql.connector import Error
from icecream import ic

class DataBase:
    def __init__(self, host, user, password, database):
        """Initialisation de la connexion à la base de données."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        """Connexion à la base de données."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
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

    def insert(self, query, params=None, check_duplicates_query=None):
        """Insère une nouvelle donnée dans la base de données avec vérification de doublon."""
        if check_duplicates_query:
            # Vérification des doublons avant insertion
            if not self.select(check_duplicates_query, params):
                return self.execute_query(query, params)
            else:
                ic("Doublon détecté, insertion annulée.")
                return False
        else:
            return self.execute_query(query, params)

    def update(self, query, params):
        """Met à jour les données dans la base de données."""
        return self.execute_query(query, params)

    def select(self, query, params=None):
        """Sélectionne des données dans la base de données."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            ic(f"Erreur SQL: {e}")
            raise Exception(f"Erreur SQL: {e}")
