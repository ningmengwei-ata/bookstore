# 导入库的依赖
# 只是先单纯的复制 可后台删改
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
# from init_db.book import BookWhole


#生成 orm 基类
#这个地方大家都要改连自己本地的
# engine = create_engine('postgresql://postgres:123456@localhost:5432/bookstore',encoding='utf-8',echo=True)
engine = create_engine('postgresql+psycopg2://postgres:123456@localhost/bookstore',encoding='utf-8',echo=True)


Base=declarative_base()


# 按照schema创建数据库
# 用户表
class Users(Base):
    __tablename__ = 'usr'
    user_id = Column(String(256), primary_key=True,unique=True)# 类比loginaccount类比注册邮箱那种?
    #username= Column(String(128),nullable=False,unique=True)# 用户名 #哪一个是主键存疑
    password = Column(String(128), nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String(512), nullable=False)
    terminal = Column(String(64), nullable=False)
    address= Column(String(512))#用户收获地址，可空但最多只有一个

# 用户商店关系表
class User_store(Base):
    __tablename__ = 'user_store'
    user_id = Column(String(256), ForeignKey('usr.user_id'), nullable=False, index = True)
    store_id = Column(String(256), nullable=False, unique=True, index = True) # 这里的store不可能重复
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'store_id'),
        {},
    )


# 商店表（含书本信息）
class Store(Base):
    __tablename__ = 'store'
    store_id = Column(String(256), ForeignKey('user_store.store_id'), nullable=False, index = True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False, index = True)
    stock_level = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  # 售价
    __table_args__ = (
        PrimaryKeyConstraint('store_id', 'book_id'),
        {},
    )




# 下面连着3张是信息总表
# 取消的订单和待付款的订单的区别注意
# 待付款订单
class New_order_unpaid(Base):
    __tablename__ = 'new_order_unpaid'
    order_id = Column(String(512), primary_key=True)
    buyer_id = Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    commit_time = Column(DateTime, nullable=False)#订单下单提交时间


# 待发货订单
class New_order_undelivered(Base):
    __tablename__ = 'new_order_undelivered'
    order_id = Column(String(512), primary_key=True)
    buyer_id = Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    purchase_time = Column(DateTime, nullable=False)


# 待收货订单
class New_order_unreceived(Base):
    __tablename__ = 'new_order_unreceived'
    order_id = Column(String(512), primary_key=True)
    buyer_id = Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    purchase_time = Column(DateTime, nullable=False)
    receive_time = Column(DateTime, nullable=True) # yzySchema也是加了status
# 已取消订单
class New_order_canceled(Base):
    __tablename__ = 'new_order_canceled'
    order_id = Column(String(512), primary_key=True)
    buyer_id = Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    cancel_time = Column(DateTime, nullable=False)
   


# 订单明细表
class New_order_detail(Base):
    __tablename__ = 'new_order_detail'
    order_id = Column(String(512), nullable=False)
    book_id = Column(Integer, nullable=False)
    
    buyer_id=Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    store_id=Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'book_id'),
        {},
    )
# 遵照数据集的schema


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
    #picture=Column(LargeBinary)



DBSession = sessionmaker(bind=engine)
    # 创建session 对象
session = DBSession()
def init_testuser():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add_all([
        Users(user_id = 'lalala@ecnu.com',
            
            password = '123456',
            balance = 10000,#分 所有涉及钱的单位都是分:currency_unit TEXT,
            token = '***',
            terminal = 'Chrome'),
        Users(user_id = 'hahaa@ecnu.com',
            
            password = '123456',
            balance =8000,
            token = '***',
            terminal='Safari'),
        Users(user_id = 'lululu@ecnu.com',
            
            password = '123456',
            balance = 9000,
            token = '***',
            terminal='Edge')
    ])
    session.commit()

def init_teststore():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add_all([
        User_store(user_id = 'hahaa@ecnu.com',
                store_id = 'Lemon'),#store_id相当于商店名
        User_store(user_id = 'hahaa@ecnu.com',
                store_id = 'NaiXue'),
            #store_id相当于商店名 
    ])
    session.commit()
    session.add_all([
       Store(store_id = 'Lemon',
                    book_id = 1,
                    stock_level=10,
                    price=2599), # 价格单位是分
        Store(store_id = 'NaiXue',
                    book_id = 2,
                    stock_level=2,
                    price=29999) # 价格单位是分
    ])
    session.commit()




def init_testorder():
    # 已下单未付款
    OrderA = New_order_unpaid(order_id = 'order1',
                            buyer_id = 'lalala@ecnu.com',
                            store_id = 'Lemon',
                            price=2000,
                            commit_time = datetime.now(),
                            )  # 0为已付款，1为已发货，2为已收货
    # 已下单未付款详细信息
    Order_detailA = New_order_detail(order_id = 'order1',
                                    book_id = 1,
                                    buyer_id = 'lalala@ecnu.com',
                                    store_id = 'Lemon',
                                    count = 2,
                                    price = 2000)
    # 已付款未发货
    OrderB = New_order_undelivered(order_id = 'order2',
                            buyer_id = 'hahaa@ecnu.com',
                            store_id = 'NaiXue',
                            price = 10000,
                            purchase_time = datetime.now())
    Order_detailB = New_order_detail(order_id = 'order2',
   
                                    book_id = 2,
                                    buyer_id = 'hahaa@ecnu.com',
                                    store_id = 'NaiXue',
                                    count = 1,
                                    price = 10000)
    # 已发货未收货
    OrderC = New_order_unreceived(order_id = 'order3',
                            buyer_id = 'hahaa@ecnu.com',
                            store_id = 'NaiXue',
                            price = 10000,
                            purchase_time = datetime.now(),
                            # receiveTime=0#初始化为0表示还没有收到货
                            )
    Order_detailC = New_order_detail(order_id = 'order3',
                                    book_id = 2,
                                    buyer_id = 'hahaa@ecnu.com',
                                    store_id = 'NaiXue',
                                    count = 1,
                                    price = 10000)
    session.add_all([Order_detailC,Order_detailA,Order_detailB,OrderA,OrderB,OrderC])
    session.commit()
def init_books():
    '''
    导入书的详细信息是助教测试book.py里进行导入的
    '''
    # 这两杯独特的测试书是我自己加的
    session.add_all([
        BookWhole( book_id =1,
    title ='DB design Principle'),
    BookWhole( book_id =2,
    title ='Gone with the wind'),
    BookWhole( book_id =50,
    title ='Gone with the wind1')
    ])
    session.commit()
def init_search_test():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add_all([
        Users(user_id = 'search',
            password = '123456',
            balance = 9000,
            token = '***',
            terminal='Edge'),
    ])
    session.commit()
    session.add(User_store(user_id = 'search',
                store_id = 'Kadokawa'))
                #store_id相当于商店名)
    session.commit()
    session.add_all([
        Store(store_id = 'Kadokawa',
                    book_id = 50,
                    stock_level=10,
                    price=2599)
    ])
    session.commit()



def init_test_all():
    init_testuser()
    init_books()
    init_teststore()
    init_testorder()

#这个要从book信息中进行init
def init_search_author():
    return 

def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    #先drop再create
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # 提交即保存到数据库
    session.commit()
    # 关闭session
    session.close()


if __name__ == "__main__":
    # 创建数据库
    init()
    # 加入信息
    init_test_all()
    # 这个想提高覆盖率时必须有!
    init_search_test()
