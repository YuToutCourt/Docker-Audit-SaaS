from sqlalchemy import Column, Integer, String
from database.database import Base

class Company(Base):
    __tablename__ = 'Company'
    id_company = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    company_agent_token = Column(String(255), unique=True)

        
