from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey

from database.database import Base

class Company(Base):
    __tablename__ = 'Company'
    id_company = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    company_pki_id = Column(Integer, ForeignKey('CA.id_ca'), nullable=False)

    @classmethod
    def get_ca_id_from_company_id(cls, session, id_company):
        return session.query(cls).filter_by(id_company=id_company).first()

    # TODO: DELETE THIS
    @classmethod
    def get_company_by_agent_token(cls, session, token):
        return session.query(cls).filter_by(company_agent_token=token).first()