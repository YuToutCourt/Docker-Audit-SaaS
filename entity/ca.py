from sqlalchemy import Column, Integer, String
from database.database import Base

class Ca(Base):
    __tablename__ = 'CA'
    id_ca = Column(Integer, primary_key=True, autoincrement=True)
    private_key = Column(String(255), unique=True)
    public_key = Column(String(255), unique=True)
    expiration_date = Column(String(255), nullable=False)


    @classmethod
    def get_ca_from_id(cls, session, ca_id):
        return session.query(cls).filter_by(id_ca=ca_id).first()

    @classmethod
    def add_new_pki(cls, session, priv, pub, expiration_date):
        ca = Ca(
            private_key=priv,
            public_key=pub,
            expiration_date=expiration_date,
        )
        session.add(ca)
        session.commit()
        return session.close()