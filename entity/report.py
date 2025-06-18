from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base

class Report(Base):
    __tablename__ = 'Report'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_ = Column(String(255))
    dataB64 = Column(String)
    id_agent = Column(Integer, ForeignKey('Agent.id_agent'))
    id_company = Column(Integer, ForeignKey('Company.id_company'))
        

