from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base

class Agent(Base):
    __tablename__ = 'Agent'
    id_agent = Column(Integer, primary_key=True, autoincrement=True)
    next_scan_date_ = Column(String(255))
    enabled = Column(Integer, default=1)
    health_check = Column(String(255))
    name = Column(String(255))
    id_company = Column(Integer, ForeignKey('Company.id_company'))
    private_key = Column(String(255), nullable=True)

    @classmethod
    def add_new_agent(cls, session, priv, pub, expiration_date):
        agent = Agent(
            private_key=priv,
            public_key=pub,
            expiration_date=expiration_date,
        )
        session.add(ca)
        session.commit()
        return session.close()