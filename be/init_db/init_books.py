# 类比助教学长写的book.py
#与book.py一样
# 这个地方暂时没改 
"""
# -!- coding: utf-8 -!-
"""
import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json


class Bookinit:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
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

from sqlalchemy import create_engine  #, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import psycopg2
from datetime import datetime,time
engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)

Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()
class Book(Base):
    __tablename__ = 'book'
    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    original_price = Column(Integer) # 原价
    currency_unit = Column(Text)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    picture = Column(LargeBinary)

def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)
    session.commit()
    # 关闭session
    session.close()
    
class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "fe/data/book.db")
        self.db_l = os.path.join(parent_path, "fe/data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

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
            book = Bookinit()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

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

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books
    def send_info_to_db(self,start,size):
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
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]
            # tagenum=MyEnum(enum.Enum)
            thelist=[]#由于没有列表类型，故使用将列表转为text的办法
            for tag in tags.split("\n"):
                if tag.strip() != "":
                    # book.tags.append(tag)
                    thelist.append(tag)
            book.tags=str(thelist)#解析成list请使用eval()
            book.picture = None
            # thelistforpic=[]
            # for i in range(0, random.randint(0, 9)):
            if picture is not None:
                ##以下为查看图片代码
                # with open('code.png', 'wb') as fn:  # wb代表二进制文件
                #     fn.write(picture)
                # img = mpimg.imread('code.png', 0)
                # plt.imshow(img)
                # plt.axis('off')
                # plt.show()


                # encode_str = base64.b64encode(picture).decode('utf-8')
                # # book.pictures.append(encode_str)
                # print(type(encode_str))
                book.picture=picture

            session.add(book)
        session.commit()
        # 关闭session
        session.close()
    def send_info(self):
        bookdb.send_info_to_db(0, bookdb.get_book_count())#count=100 or 整张表

    def send_info_to_db_multipool(self,start,size):

        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (size, start))
        self.main1(cursor)
        session.commit()
        # 关闭session
        session.close()

    def row_iter(self,row):
        book = Book()
        book.id = row[0]
        book.title = row[1]
        book.author = row[2]
        book.publisher = row[3]
        book.original_title = row[4]
        book.translator = row[5]
        book.pub_year = row[6]
        book.pages = row[7]
        book.price = row[8]

        book.currency_unit = row[9]
        book.binding = row[10]
        book.isbn = row[11]
        book.author_intro = row[12]
        book.book_intro = row[13]
        book.content = row[14]
        tags = row[15]

        picture = row[16]
        # tagenum=MyEnum(enum.Enum)
        thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
        for tag in tags.split("\n"):
            if tag.strip() != "":
                # book.tags.append(tag)
                thelist.append(tag)
        book.tags = str(thelist)  # 解析成list请使用eval()
        book.picture = None
        # thelistforpic=[]
        # for i in range(0, random.randint(0, 9)):
        if picture is not None:
            ##以下为查看图片代码
            # with open('code.png', 'wb') as fn:  # wb代表二进制文件
            #     fn.write(picture)
            # img = mpimg.imread('code.png', 0)
            # plt.imshow(img)
            # plt.axis('off')
            # plt.show()

            # encode_str = base64.b64encode(picture).decode('utf-8')
            # # book.pictures.append(encode_str)
            # print(type(encode_str))
            book.picture = picture

        session.add(book)
    def main1(self,groups):  # nothing:3.12s nothing2:3.207s
        from multiprocessing.pool import Pool
        pool = Pool(os.cpu_count())
        #groups = [x for x in range(MAX_NUM)] 要遍历的东西
        pool.map(self.row_iter, groups)
        pool.close()
        pool.join()

    def send_info_multipool(self):
        bookdb.send_info_to_db_multipool(0, bookdb.get_book_count())#count=100 or 整张表
if __name__ == '__main__':

    # bookdb=BookDB()#单进程0.7148709297180176 多进程2.212113380432129
    bookdb=BookDB(large=True)#导入整张表 43988数据 还没跑通 不知道多进程会不会比单进程快
    # 单进程1033.8140s 多进程1035.624s 无任何速度提升
    print(bookdb.get_book_count())
    # for i in bookdb.get_book_info(0,bookdb.get_book_count()):
    #     print(i.tags)
    init()
    import time
    start = time.time()
    bookdb.send_info()
    # bookdb.send_info_multipool()#多进程
    end = time.time()
    print (end-start)