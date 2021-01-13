import sys
sys.path.append("../")
from be.model1 import store
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint,and_
from sqlalchemy.orm import sessionmaker
from init_db.init_database import Users
from init_db.init_database import User_store
class DBConn:
    def __init__(self):
        engine = create_engine('postgresql://postgres:123456@localhost:5432/bookstore')
        Base = declarative_base()
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        #self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        # cursor = self.conn.execute("SELECT user_id FROM user WHERE user_id = ?;", (user_id,))
        # row = cursor.fetchone()
        # user=self.session.execute("SELECT user_id FROM usr WHERE user_id = '%s';" % (user_id,)).fetchone()
        user=self.session.query(Users).filter_by(user_id=user_id).first()
        if user is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        row = self.session.execute("SELECT book_id FROM store WHERE store_id = '%s' AND book_id = '%s';"%
        (store_id, book_id)).fetchone()
        #row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        # cursor = self.conn.execute("SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,))
        # row = cursor.fetchone()
        # store=self.session.execute("SELECT store_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
        store=self.session.query(User_store).filter_by(store_id=store_id).first()
        if store is None:
            return False
        else:
            return True
