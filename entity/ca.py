from sqlalchemy import Column, Integer, String
from database.database import Base, dbo
from icecream import ic

class Ca(Base):
    __tablename__ = 'CA'
    id_ca = Column(Integer, primary_key=True, autoincrement=True)
    private_key = Column(String(255), unique=True)
    public_key = Column(String(255), unique=True)
    expiration_date = Column(String(255), nullable=False)


    @classmethod
    def get_ca_from_id(cls, ca_id):
        return dbo().query(cls).filter_by(id_ca=ca_id).first()

    @classmethod
    def get_publickey_from_ca_id(cls, ca_id):
        ca = dbo().query(cls).filter_by(id_ca=ca_id).first()
        return ca.public_key if ca else None

    @classmethod
    def add_new_pki(cls, priv, pub, expiration_date):
        session = dbo()
        ca = Ca(
            private_key=priv,
            public_key=pub,
            expiration_date=expiration_date,
        )
        session.add(ca)
        session.commit()
        ca_id = ca.id_ca
        session.close()
        return ca_id

    @classmethod
    def delete_ca_by_id(cls, id_ca):
        session = dbo()
        try:
            ca = session.query(cls).filter_by(id_ca=id_ca).first()
            if ca:
                session.delete(ca)
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
    def get_by_company(cls, company_id):
        """Récupérer la CA d'une entreprise"""
        # Cette méthode nécessite une jointure avec Company
        # Pour l'instant, retourner None
        return None