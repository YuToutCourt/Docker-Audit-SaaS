from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base, dbo
from icecream import ic

class Agent(Base):
    __tablename__ = 'Agent'
    id_agent = Column(Integer, primary_key=True, autoincrement=True)
    next_scan_date_ = Column(String(255))
    enabled = Column(Integer, default=1)
    health_check = Column(String(255))
    name = Column(String(255))
    id_company = Column(Integer, ForeignKey('Company.id_company', ondelete='CASCADE'))
    private_key = Column(String(255), nullable=True)
    public_key = Column(String(255), nullable=True)
    id_ca = Column(Integer, ForeignKey('CA.id_ca'))
    scan_interval = Column(Integer, default=86400)

    def add(self):
        session = dbo()
        try:
            session.add(self)
            session.commit()
            session.close()
            return True
        except Exception as e:
            ic(e)
            session.rollback()
            session.close()
            return False

    @classmethod
    def get_agent_from_cert(cls, pub):
        try:
            res = dbo().query(cls).filter_by(public_key=pub).first()
            return res if res else False
        except Exception as e:
            ic(e)
            return False


    @classmethod
    def check_if_agent_already_exist(cls, name, id_company):
        try:
            res = dbo().query(cls).filter_by(name=name, id_company=id_company).first()
            return True if res else False
        except Exception as e:
            ic(e)
            return False

    @classmethod
    def get_ca_id_from_cert(cls, pub):
        try:
            res = dbo().query(cls).filter_by(public_key=pub).first()
            return res.id_ca if res else False
        except Exception as e:
            ic(e)
            return False

    @classmethod
    def get_scan_date_from_cert(cls, pub):
        try:
            res = dbo().query(cls).filter_by(public_key=pub).first()
            return res.next_scan_date_ if res else False
        except Exception as e:
            ic(e)
            return False


    @classmethod
    def get_count_agent_by_id_company(cls, id_company):
        return dbo().query(cls).filter_by(id_company=id_company).count()
