import base64
import jwt
import time
import logging
import sqlalchemy
import sys
sys.path.append("../")
import sqlite3 as sqlite
from be.model1 import error
from be.model1 import db_conn
from init_db.init_database import Users
# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)
    def register(self, user_id: str, password: str):
        #dump()
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            # self.conn.execute(
            #     "INSERT into user(user_id, password, balance, token, terminal) "
            #     "VALUES (?, ?, ?, ?, ?);",
            #     (user_id, password, 0, token, terminal), )
            # self.session.execute( "INSERT INTO usr (user_id, password, balance, token, terminal) values (:user_id, :password, 0, :token, :terminal)",{"user_id":user_id,"password": password,"token":token,"terminal":terminal })
            new_usr = Users(
                user_id=user_id,
                password = password,
                balance = 0,
                token = token,
                terminal = terminal
            )
            self.session.add(new_usr)
            self.session.commit()
        except sqlite.Error:
            return error.error_exist_user_id(user_id)
        return 200, "ok"
    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            # cursor = self.session.execute("DELETE from usr where user_id='%s'"% (user_id,))
            # if cursor.rowcount == 1:
            #     self.session.commit()
            # else:
            #     return error.error_authorization_fail()
            query = self.session.query(Users).filter(Users.user_id == user_id)
            query.delete()

            if query.first() is None:
                self.session.commit()
            else:
                return error.error_authorization_fail()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    

    def check_token(self, user_id: str, token: str) -> (int, str):
        #cursor = self.session.execute("SELECT token from user where user_id=?", (user_id,))
        #row=self.session.execute("SELECT token from usr where user_id='%s'" % (user_id)).fetchone()
        #row = cursor.fetchone()
        row=self.session.query(Users).filter(Users.user_id==user_id).first()
        if row is None:
            return error.error_authorization_fail()
        # db_token = row[0]
        db_token = row.token
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        # row=self.session.execute("SELECT password from usr where user_id=:user_id",
        #                                 {"user_id": user_id}).fetchone()
        #row= self.session.execute("SELECT password from user where user_id=?", (user_id,)).fetchone()
        #row = cursor.fetchone()
        row=self.session.query(Users).filter(Users.user_id==user_id).first()
        if row is None:
            return error.error_authorization_fail()
        #if password !=row[0]
        if password != row.password:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            # cursor = self.session.execute(
            #      "UPDATE usr set token= '%s' , terminal = '%s' where user_id = '%s'"% (token, terminal, user_id) )
            cursor=self.session.query(Users).filter(Users.user_id == user_id).first() 
            #if cursor.rowcount == 0:
            if cursor is None:
                return error.error_authorization_fail() + ("", )
            cursor.token = token
            cursor.terminal = terminal
            self.session.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            new_token = jwt_encode(user_id, terminal)

            # cursor = self.conn.execute(
            #     "UPDATE user SET token = ?, terminal = ? WHERE user_id=?",
            #     (dummy_token, terminal, user_id), )
            # cursor = self.session.execute(
            #      "UPDATE usr set token= '%s' , terminal = '%s' where user_id = '%s'"% (new_token, terminal, user_id) ) 
            cursor=self.session.query(Users).filter(Users.user_id == user_id).first()
            # if cursor.rowcount == 0:
            if cursor is None:
                return error.error_authorization_fail()
            cursor.token = new_token
            cursor.terminal = terminal
            self.session.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            # cursor = self.conn.execute(
            #     "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?",
            #     (new_password, token, terminal, user_id), )
            # cursor=self.session.execute(
            # "UPDATE usr set password = '%s',token='%s',terminal='%s' where user_id = '%s'"%(new_password, token, terminal,user_id), )
            cursor= self.session.query(Users).filter(Users.user_id == user_id).first()
            # if cursor.rowcount == 0:
            if cursor is None:
                return error.error_authorization_fail()
            cursor.password = new_password
            cursor.token = token
            cursor.terminal = terminal
            self.session.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 搜索是针对全部用户都拥有的功能
    # 关键字搜索，参数化搜索方式
    # 全站店铺搜索与当前店铺搜索
    # 全文索引优化查找
    # 范围：题目标签内容(book_intro)