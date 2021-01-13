# 导入库的依赖
# 只是先单纯的复制 可后台删改
import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String #区分大小写
from sqlalchemy import create_engine, PrimaryKeyConstraint,Float
from sqlalchemy.ext.declarative import declarative_base
# 创建表中的字段(列)
from sqlalchemy import Column
# 表中字段的属性
from sqlalchemy import Integer, String, ForeignKey,Text,LargeBinary,DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import re
import jieba.analyse
import time

#生成 orm 基类
#这个地方大家都要改连自己本地的
# engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)
engine = create_engine('postgresql://postgres:123456@localhost:5432/bookstore',encoding='utf-8',echo=True)
# engine = create_engine('postgresql://postgres:123456@localhost:5432/bookshop',encoding='utf-8',echo=True)


# 暂时只需要跑init_database.py 
Base=declarative_base()

#再定义一次防止出现foreignKey错误
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
    price = Column(Integer,nullable=True)  # 原价
    binding = Column(Text,nullable=True)
    isbn = Column(Text,nullable=True)
    author_intro = Column(Text,nullable=True)
    book_intro = Column(Text,nullable=True)
    content = Column(Text,nullable=True)
    tags = Column(Text,nullable=True)
    # picture = Column(LargeBinary,nullable=True)#暂时测一下
class SearchTitle(Base):
    __tablename__ = 'search_title'
    search_id=Column(Integer,autoincrement=True,primary_key=True)
    title = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)

class SearchAuthor(Base):
    __tablename__ = 'search_author'
    search_id=Column(Integer,autoincrement=True,primary_key=True)
    author = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)

class SearchBookIntro(Base):
    __tablename__ = 'search_book_intro'
    search_id=Column(Integer,autoincrement=True,primary_key=True)
    book_intro = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
class SearchTags(Base):
    __tablename__ = 'search_book_tags'
    search_id=Column(Integer,autoincrement=True,primary_key=True)
    tags = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
#建立全局索引的多个数据库copy
cop = re.compile("[^\u4e00-\u9fa5^.^a-z^A-Z^0-9]")#只保留汉字和英文，去除所有字符

class SearchDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "fe/data/book.db")#注意这里的路径

        self.db_l = os.path.join(parent_path, "fe/data/book_lx.db")#这里的大测试集还没改
        print(self.db_l)
        print("*********************************************")
        if large:
            self.book_db = self.db_s
        else:
            self.book_db = self.db_l
    def init_title_books(self):
        # 使用2-gram的方式存放title_books
        # 2-gram粒度太细了
        # 大部分书的title还是短的
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        # Base.metadata.drop_all(engine)#drop掉旧的
        Base.metadata.create_all(engine)
        rows = session.execute("SELECT book_id, title FROM book;").fetchall()
        for row in rows:
            title_string = cop.sub("", row.title)
            if len(title_string)==0:
                title_string=row.title
            title_row_to_insert=SearchTitle()
            title_row_to_insert.title=title_string
            title_row_to_insert.book_id=row.book_id
            session.add(title_row_to_insert)
            session.commit()

            # title_string_len=len(title_string)
            # for k in range(1, title_string_len + 1):
            #     index_begin=k-1
            #     index_end=k+1
            #     strtmp=title_string[index_begin:index_end]
            #     if strtmp=='' or strtmp==' ' :
            #         continue
            #     title_row_to_insert=SearchTitle()
            #     title_row_to_insert.title=strtmp
            #     title_row_to_insert.book_id=row.book_id
            #     session.add(title_row_to_insert)
            #     session.commit()
        session.close()
        

    def init_author_books(self):
        #注意author和title的切词粒度
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        # Base.metadata.drop_all(engine)#drop掉旧的
        Base.metadata.create_all(engine)
        rows = session.execute("SELECT book_id, author FROM book;").fetchall()
        for row in rows:
            row_to_insert=SearchAuthor()
            if(row.author==None):
                to_string='佚名'
                row_to_insert.author=to_string
                row_to_insert.book_id=row.book_id
                session.add(row_to_insert)
                session.commit()
                
            else:
                to_string = cop.sub("", row.author)
                '''比较不同分词对召回率的比较：下面这个第一个杨红樱就查不出来'''
                # if len(to_string)==0:
                #     to_string=row.author
                # row_to_insert.author=to_string
                # row_to_insert.book_id=row.book_id
                # session.add(row_to_insert)
                # session.commit() 
                if len(to_string)==0:
                    to_string=row.author
                to_string_len=len(to_string)
                # for k in range(1, to_string_len + 1):
                #     row_to_insert=SearchAuthor()
                #     if to_string[k - 1] == '':
                #         continue
                #     if to_string[k - 1] == '美' or to_string[k - 1] == '英':
                #         continue
                #     j = to_string[:k]
                #     row_to_insert.author=j
                #     row_to_insert.book_id=row.book_id
                #     session.add(row_to_insert)
                #     session.commit()
                # 下面把作者的姓加进去提高召回率
                # 杨红和杨分词对于分词起来说真的挺难:D
                row_to_insert=SearchAuthor()
                row_to_insert.author=to_string[0]
                row_to_insert.book_id=row.book_id
                session.add(row_to_insert)
                session.commit()
                row_to_insert=SearchAuthor()
                row_to_insert.author=to_string
                row_to_insert.book_id=row.book_id
                session.add(row_to_insert)
                session.commit()
                # 然后下面这个才是2-GRAM;
                for k in range(1, to_string_len + 1):
                    index_begin=k-1
                    index_end=k+1
                    strtmp=to_string[index_begin:index_end]
                    if strtmp=='' or strtmp==' ' :
                        continue
                    else:
                        row_to_insert=SearchAuthor()
                        row_to_insert.author=strtmp
                        row_to_insert.book_id=row.book_id
                        session.add(row_to_insert)
                        session.commit()
        session.close()
        
    # def init_info_books(self):
    #     DBSession = sessionmaker(bind=engine)
    #     session = DBSession()
    #     # Base.metadata.drop_all(engine)#drop掉旧的
    #     Base.metadata.create_all(engine)
    #     rows = session.execute("SELECT book_id, book_intro FROM book;").fetchall()
    #     for row in rows:
    #         if(row.book_intro==None):
    #             to_string="简介暂无"
    #         else:
    #             # jieba.
    #             to_string = cop.sub("", row.book_intro)
    #             if len(to_string)==0:
    #                 to_string=row.book_intro
    #         row_to_insert=SearchBookIntro()
    #         row_to_insert.book_intro=to_string
    #         row_to_insert.book_id=row.book_id
    #         session.add(row_to_insert)
    #         session.commit()
    #     session.close()
        
    def init_tags_books(self):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        # Base.metadata.drop_all(engine)#drop掉旧的
        Base.metadata.create_all(engine)
        rows = session.execute("SELECT book_id, tags FROM book;").fetchall()
        for row in rows:
            if(row.tags==None):
                to_string="tags暂无"
            else:
                to_string=row.tags
                print(type(to_string))# 这里tags的类型是str
                tags_split_list=to_string.split(',')[1:-2]
                print( tags_split_list)
                first_tag=to_string.split(',')[0].split('{')[1]
                last_tag=to_string.split(',')[-1].split('}')[1]
                tags_split_list.insert(0,first_tag)
                tags_split_list.insert(-1,last_tag)
                print( tags_split_list)
                for tag in tags_split_list:
                    if tag==' 'or tag=='':
                        continue
                    row_to_insert=SearchTags()
                    row_to_insert.tags=tag
                    row_to_insert.book_id=row.book_id
                    session.add(row_to_insert)
                    session.commit()
        session.close()
    def init_book_intro_keywords(self):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        # Base.metadata.drop_all(engine)#drop掉旧的
        Base.metadata.create_all(engine)
        rows = session.execute("SELECT book_id, book_intro FROM book;").fetchall()
        for row in rows:
            if(row.book_intro==None):
                to_string="简介暂无"
            else:
                # to_string = cop.sub("", row.book_intro)
                # 最多保留book_intro中20个关键词,其实这也就相当于空间变成20倍了:D
                keywords_textrank_list = jieba.analyse.textrank(row.book_intro)
                if len(keywords_textrank_list)>20:
                    keywords_textrank_list=keywords_textrank_list[:20]
                # print(len(keywords_textrank_list))
                if len(keywords_textrank_list)==0:
                    to_string="简介关键词暂无"
                    row_to_insert=SearchBookIntro()
                    row_to_insert.book_intro=to_string
                    row_to_insert.book_id=row.book_id
                    session.add(row_to_insert)
                    session.commit()
                else:
                    for keyword in keywords_textrank_list:
                        row_to_insert=SearchBookIntro()
                        row_to_insert.book_intro=str(keyword)
                        row_to_insert.book_id=row.book_id
                        session.add(row_to_insert)
                        session.commit()
        session.close()

        



if __name__ == '__main__':

    sdb=SearchDB()
    time1=time.time()
    # Base.metadata.drop_all(engine)#drop掉旧的
    Base.metadata.create_all(engine)
    # sdb.init_author_books()#控制分词粒度为:1/12/123/1234...
    # sdb.init_tags_books()#把tags当作关键词拆开
    # sdb.init_title_books()#2-gram
    sdb.init_book_intro_keywords()# 提取book_intro的关键词作为jieba分词的效果，分词粒度影响了检索的复杂度 
    time2=time.time()
    print(time2-time1)#我自己测从scratch开始大概是7s左右:D

    # session.close()
