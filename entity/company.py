from database.database import DataBase

from icecream import ic

class Company:
    def __init__(self, id=None, name=None, company_agent_token=None):
        self.id = id
        self.name = name
        self.company_agent_token = company_agent_token

    def get_company_by_agent_token(self, token):
        db = DataBase()
        query = "SELECT * from Company where company_agent_token=%s"
        res = db.fetch_query(query=query, params=(token,))

        if res:
            self.id = res[0].get('id_company')
            self.name = res[0].get('name')
            self.company_agent_token = res[0].get('company_agent_token')

            return self

        return False

        
