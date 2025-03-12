from database.database import DataBase
from icecream import ic

class Report:
    def __init__(self, date=None, dataB64=None, id_agent=None, id_company=None):
        self.date_ = date
        self.dataB64 = dataB64
        self.id_agent = id_agent
        self.id_company = id_company

    def insert_data(self, date, data, id_agent, id_company):
        db = DataBase()

        query = """
        INSERT INTO Report (date_, dataB64, id_agent, id_company)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query=query, params=(date, data, id_agent, id_company,))
        

