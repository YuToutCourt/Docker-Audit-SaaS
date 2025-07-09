from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base, dbo
from icecream import ic

class User(Base):
    __tablename__ = 'User_'
    id_user = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255))
    enabled = Column(Integer, default=1)
    id_company = Column(Integer, ForeignKey('Company.id_company', ondelete='CASCADE'))
    is_admin = Column(Integer, default=0)  # 0 for user, 1 for admin

    def add(self):
        session = dbo()
        try:
            session.add(self)
            session.commit()
            session.close()
        except Exception as e:
            ic(e)
            session.rollback()
            session.close()

    @classmethod
    def delete_user_by_id(cls, id_user):
        session = dbo()
        try:
            user = session.query(cls).filter_by(id_user=id_user).first()
            if user:
                session.delete(user)
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
    def login_user(cls, username, password):
        from werkzeug.security import check_password_hash
        """Retourne l'utilisateur si username/password sont corrects et enabled, sinon None."""
        user = dbo().query(User).filter_by(username=username, enabled=1).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    @classmethod
    def get_all_users(cls):
        return dbo().query(cls).all()

    @classmethod
    def check_if_user_exist_by_username(cls, username):
        return True if dbo().query(cls).filter_by(username=username).first() else False

    @classmethod
    def get_user_by_id(cls, id_user):
        return dbo().query(cls).filter_by(id_user=id_user).first()

    @classmethod
    def get_count_user_by_id_company(cls, id_company):
        return dbo().query(cls).filter_by(id_company=id_company).count()

