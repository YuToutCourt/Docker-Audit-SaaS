from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base, dbo

class Report(Base):
    __tablename__ = 'Report'
    id_report = Column(Integer, primary_key=True, autoincrement=True)
    date_ = Column(String(255))
    dataB64 = Column(String)
    id_agent = Column(Integer, ForeignKey('Agent.id_agent', ondelete='CASCADE'))
    id_company = Column(Integer, ForeignKey('Company.id_company', ondelete='CASCADE'))
    salt = Column(String)


    @classmethod
    def add_new_report(cls, scan_date, dataB64, id_agent, id_company, salt):
        session = dbo()
        report = Report(
            date_=scan_date,
            dataB64=dataB64,
            id_agent=id_agent,
            id_company=id_company,
            salt=salt
        )
        session.add(report)
        session.commit()
        id_report = report.id_report
        session.close()
        return id_report

    @classmethod
    def get_by_agent_and_company(cls, agent_id, company_id):
        """Récupérer les rapports d'un agent et d'une entreprise"""
        return dbo().query(cls).filter_by(id_agent=agent_id, id_company=company_id).all()

    @classmethod
    def get_by_company(cls, company_id):
        """Récupérer tous les rapports d'une entreprise"""
        return dbo().query(cls).filter_by(id_company=company_id).all()

    @classmethod
    def get_by_id_and_agent_and_company(cls, report_id, agent_id, company_id):
        """Récupérer un rapport par ID, agent et entreprise"""
        return dbo().query(cls).filter_by(id_report=report_id, id_agent=agent_id, id_company=company_id).first()

    @classmethod
    def get_all(cls):
        """Récupérer tous les rapports"""
        return dbo().query(cls).all()

    def to_dict(self):
        """Convertir l'objet en dictionnaire"""
        return {
            'id_report': self.id_report,
            'date_': self.date_,
            'id_agent': self.id_agent,
            'id_company': self.id_company,
            'salt': self.salt
        }