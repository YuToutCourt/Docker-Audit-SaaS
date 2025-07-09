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