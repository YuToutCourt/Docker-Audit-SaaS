import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
USER = os.getenv("USER_DB")
PASSWORD = os.getenv("PASSWORD_DB")
DATABASE = os.getenv("DATABASE")
PORT = os.getenv("PORT")

# Chaîne de connexion SQLAlchemy pour MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Database:
    def __init__(self):
        self.session = SessionLocal()

    def close(self):
        self.session.close()

    def login_user(self, username, password):
        from entity.user import User  # Import ici pour éviter le circular import
        """Retourne l'utilisateur si username/password sont corrects et enabled, sinon None."""
        user = self.session.query(User).filter_by(username=username, password=password, enabled=1).first()
        return user

# Utilisation :
# from database.database import SessionLocal
# session = SessionLocal()
# ...
# session.close()

    