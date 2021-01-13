import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json

from sqlalchemy import create_engine  #, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgresql+psycopg2://postgres:123456@localhost/bookstore',encoding='utf-8',echo=True)
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()

#这个是sqlite数据库，用于加载助教爬的数据库进我们自己的postgresql
class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit:str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []

class BookWhole(Base):
    # PostgreSQL提供text类型， 它可以存储任何长度的字符串。
    __tablename__ = 'book'
    book_id = Column(Integer, primary_key=True,autoincrement=True)#自增
    title = Column(Text, nullable=False)
    author = Column(Text,nullable=True)
    publisher = Column(Text,nullable=True)
    original_title = Column(Text,nullable=True)
    translator = Column(Text,nullable=True)
    pub_year = Column(Text,nullable=True)
    pages = Column(Integer,nullable=True)
    original_price = Column(Integer,nullable=True)  # 原价
    binding = Column(Text,nullable=True)
    isbn = Column(Text,nullable=True)
    author_intro = Column(Text,nullable=True)
    book_intro = Column(Text,nullable=True)
    content = Column(Text,nullable=True)
    tags = Column(Text,nullable=True)
    picture = Column(LargeBinary,nullable=True)#暂时测一下
# class BookImages(Base):
#     __tablename__ = 'book_images'#postgresql天生不区分大小写
#     picture_id = Column(Integer, primary_key=True,autoincrement=True)
#     book_id = Column(Integer, ForeignKey("book.book_id"))
#     picture_binary = Column(LargeBinary,nullable=True) # 图片命名：userId + 上传时间戳

class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "fe/data/book.db")#注意这里的路径

        self.db_l = os.path.join(parent_path, "fe/data/book_lx.db")#这里的大测试集还没改
        print(self.db_l)
        print("*********************************************")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = "D:/这学期/数据管理系统/大作业/项目/DB/fe/data/book.db"
            # self.book_db=self.db_s

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT count(id) FROM book")
        row = cursor.fetchone()
        return row[0]

    def get_book_info(self, start, size) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (size, start))
        for row in cursor:
            book = Book()
            book.id = int(row[0])#原book_id都是str
            # print(type(book.id))
            book.title = row[1]
            # print(type(book.title))
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.original_price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
                    
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode('utf-8')
                    book.pictures.append(encode_str)
            books.append(book)
            # print(tags.decode('utf-8'))
            print(type(book.id))
            print(type(book.title))
            print(book.currency_unit)
            
            # print(book.tags)
            # print(type(book.tags))#这里都是list类型的tags
            print(type(book.pictures))#这里pictures也是list类型
        # print(books)
        return books
    
    def init_postgresql(self,start,size):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (size, start))

        for row in cursor:
            book = BookWhole()
            # book_pic=BookImages()
            # book=BookWhole(title=row[1],author=row[2],publisher=row[3],)
            book.book_id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            # 这里加一个单位处理，统一换成分，
            # 我们的schema中的单位都是分
            price = row[8]
            book.original_price=price*100
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]
            tagListPostgresql=[]
            for tag in tags.split("\n"):
                if tag.strip() != "":
                    tagListPostgresql.append(tag)
            book.tags=tagListPostgresql
            book.picture=picture
            # if picture is not None:
            #     # book.picture=picture
            #     book_pic.book_id=book.book_id
            #     book_pic.picture_url=picture#这里暂时不是URL，先别管
            session.add(book)
            # session.add(book_pic)
            session.commit()
        session.close()


    
if __name__ == '__main__':

    bookdb=BookDB(large=False)
    # print(bookdb.get_book_count())
    # bookdb.get_book_info(1,10)#这里更改数目
    #Base.metadata.drop_all(engine)#drop掉旧的
    Base.metadata.create_all(engine)
    bookdb.init_postgresql(0,100)#这更改初始化的图书数目

    # session.close()



