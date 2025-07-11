import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
USER = os.getenv("USER_DB")
PASSWORD = os.getenv("PASSWORD_DB")
DATABASE = os.getenv("DATABASE")
PORT = os.getenv("PORT")

# Chaîne de connexion SQLAlchemy pour MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Configuration optimisée du pool de connexions
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=False,
    poolclass=QueuePool,
    pool_size=20,  # Augmenté de 5 à 20
    max_overflow=30,  # Augmenté de 10 à 30
    pool_timeout=60,  # Augmenté de 30 à 60 secondes
    pool_recycle=3600,  # Recycler les connexions après 1 heure
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    connect_args={
        'connect_timeout': 60,
        'read_timeout': 60,
        'write_timeout': 60,
        'charset': 'utf8mb4',
        'autocommit': False,
        'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
    }
)

dbo = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Database:
    def __init__(self):
        self.session = dbo()

    def close(self):
        if self.session:
            self.session.close()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Fonction utilitaire pour gérer les connexions de manière sûre
def get_db_session():
    """Retourne une session de base de données avec gestion automatique de la fermeture"""
    db = Database()
    try:
        return db.session
    except Exception as e:
        db.close()
        raise e