from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from icecream import ic
from database.database import Base, dbo

class Company(Base):
    __tablename__ = 'Company'
    id_company = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    company_pki_id = Column(Integer, ForeignKey('CA.id_ca', ondelete='CASCADE'), nullable=False )

    def add(self):
        session = dbo() 
        try:
            session.add(self)
            session.commit()
            return True
        except Exception as e:
            ic(e)
            session.rollback()
            session.close()
            return False

    def delete(self):
        session = dbo()
        try:
            session.delete(self)
            session.commit()
            session.close()
        except Exception as e:
            ic(e)
            session.rollback()
            session.close()

    @classmethod
    def get_ca_id_from_company_id(cls, id_company):
        return dbo().query(cls).filter_by(id_company=id_company).first()

    @classmethod
    def get_all_company(cls):
        return dbo().query(cls).all()


    @classmethod
    def get_company_by_id(cls, id_company):
        return dbo().query(cls).filter_by(id_company=id_company).first()


    @classmethod
    def get_ca_id_from_company(cls, id_company):
        try:
            res = dbo().query(cls).filter_by(id_company=id_company).first()
            return res.company_pki_id if res else False
        except Exception as e:
            ic(e)
            return False

    @classmethod
    def delete_company_by_id(cls, id_company):
        session = dbo()
        try:
            company = session.query(cls).filter_by(id_company=id_company).first()
            if company:
                # Récupérer l'ID de la CA avant de supprimer l'entreprise
                ca_id = company.company_pki_id
                
                # Supprimer d'abord la CA avec la même session
                from entity.ca import Ca
                ca = session.query(Ca).filter_by(id_ca=ca_id).first()
                if ca:
                    session.delete(ca)
                
                # Puis supprimer l'entreprise
                session.delete(company)
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            ic(e)
            session.rollback()
            session.close()
            return False

    @classmethod
    def get_all(cls):
        """Récupérer toutes les entreprises"""
        return dbo().query(cls).all()

    def to_dict(self):
        """Convertir l'objet en dictionnaire"""
        return {
            'id_company': self.id_company,
            'name': self.name,
            'company_pki_id': self.company_pki_id
        }
