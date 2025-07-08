from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base
from icecream import ic

class Agent(Base):
    __tablename__ = 'Agent'
    id_agent = Column(Integer, primary_key=True, autoincrement=True)
    next_scan_date_ = Column(String(255))
    enabled = Column(Integer, default=1)
    health_check = Column(String(255))
    name = Column(String(255))
    id_company = Column(Integer, ForeignKey('Company.id_company'))
    private_key = Column(String(255), nullable=True)
    public_key = Column(String(255), nullable=True)
    id_ca = Column(Integer, ForeignKey('CA.id_ca'))
    

    @classmethod
    def add_new_agent(cls, session, name, priv, pub, id_company, id_ca):
        try:
            agent = Agent(
                name=name,
                next_scan_date_="1970/01/01 00:00:00",
                id_company= id_company,
                health_check=0,
                private_key=priv,
                public_key=pub,
                id_ca=id_ca
            )
            session.add(agent)
            session.commit()
            session.close()
            return True
        except Exception as e:
            ic(e)
            return False

    @classmethod
    def get_ca_id_from_cert(cls, session, pub):
        try:
            res = session.query(cls).filter_by(public_key=pub).first()
            return res.id_ca if res else False
        except Exception as e:
            ic(e)
            return False

    @classmethod
    def get_ca_id_from_company(cls, session, id_company):
        try:
            res = session.query(cls).filter_by(id_company=id_company).first()
            return res.id_ca if res else False
        except Exception as e:
            ic(e)
            return False

