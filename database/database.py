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
dbo = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Database:
    def __init__(self):
        self.session = dbo()

    def close(self):
        self.session.close()

    def login_user(self, username, password):
        from entity.user import User  # Import ici pour éviter le circular import
        from werkzeug.security import check_password_hash
        """Retourne l'utilisateur si username/password sont corrects et enabled, sinon None."""
        user = self.session.query(User).filter_by(username=username, enabled=1).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    