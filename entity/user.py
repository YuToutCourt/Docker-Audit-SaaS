from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base

class User(Base):
    __tablename__ = 'User_'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255))
    enabled = Column(Integer, default=1)
    id_company = Column(Integer, ForeignKey('Company.id_company'))