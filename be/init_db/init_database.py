# 导入库的依赖
# 只是先单纯的复制 可后台删改
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String #区分大小写
from sqlalchemy import create_engine, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
# 创建表中的字段(列)
from sqlalchemy import Column
# 表中字段的属性
from sqlalchemy import Integer, String, ForeignKey,Text,LargeBinary,DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime


#生成 orm 基类
#这个地方大家都要改连自己本地的
engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)


Base=declarative_base()


# 按照schema创建数据库
# 用户表
class User(Base):
    __tablename__ = 'usr'
    user_id = Column(String(128), primary_key=True,unique=True)# 类比loginaccount类比注册邮箱那种?
    username= Column(String(128),nullable=False,unique=True)# 用户名 #哪一个是主键存疑
    password = Column(String(128), nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String(512), nullable=False)
    terminal = Column(String(64), nullable=False)
    address= Column(String(512))#用户收获地址，可空但最多只有一个

# 用户商店关系表
class User_store(Base):
    __tablename__ = 'user_store'
    user_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False, index = True)
    store_id = Column(String(128), nullable=False, unique=True, index = True) # 这里的store不可能重复
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'store_id'),
        {},
    )


# 商店表（含书本信息）
class Store(Base):
    __tablename__ = 'store'
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False, index = True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False, index = True)
    stock_level = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  # 售价
    __table_args__ = (
        PrimaryKeyConstraint('store_id', 'book_id'),
        {},
    )



# class Book(Base):
#     __tablename__ = 'book'
#     book_id = Column(Integer, primary_key=True)
#     title = Column(Text, nullable=False)
#     author = Column(Text)
#     publisher = Column(Text)
#     original_title = Column(Text)
#     translator = Column(Text)
#     pub_year = Column(Text)
#     pages = Column(Integer)
#     original_price = Column(Integer)  # 原价
#     currency_unit = Column(Text)
#     binding = Column(Text)
#     isbn = Column(Text)
#     author_intro = Column(Text)
#     book_intro = Column(Text)
#     content = Column(Text)
#     tags = Column(Text)
#     picture = Column(LargeBinary)

# 下面连着3张是信息总表
# 取消的订单和待付款的订单的区别注意
# 待付款订单
class New_order_unpaid(Base):
    __tablename__ = 'new_order_unpaid'
    order_id = Column(String(128), primary_key=True)
    buyer_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    commitTime = Column(DateTime, nullable=False)#订单下单提交时间


# 待发货订单
class New_order_undelivered(Base):
    __tablename__ = 'new_order_undelivered'
    order_id = Column(String(128), primary_key=True)
    buyer_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    purchaseTime = Column(DateTime, nullable=False)


# 待收货订单
class New_order_unreceived(Base):
    __tablename__ = 'new_order_unreceived'
    order_id = Column(String(128), primary_key=True)
    buyer_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    purchaseTime = Column(DateTime, nullable=False)
    receiveTime = Column(DateTime, nullable=True) # yzySchema也是加了status


# 订单明细表
class New_order_detail(Base):
    __tablename__ = 'new_order_detail'
    order_id = Column(String(128), nullable=False)
    book_id = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'book_id'),
        {},
    )

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


DBSession = sessionmaker(bind=engine)
    # 创建session 对象
session = DBSession()
def init_testuser():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add_all([
        User(user_id = 'lalala@ecnu.com',
            username='cxn',
            password = '123456',
            balance = 100,
            token = '***',
            terminal = 'Chrome'),
        User(user_id = 'hahaa@ecnu.com',
            username='wwq',
            password = '123456',
            balance = 500,
            token = '***',
            terminal='Safari'),
        User(user_id = 'lululu@ecnu.com',
            username='hsy',
            password = '123456',
            balance = 300,
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
                            commitTime = datetime.now(),
                            )  # 0为已付款，1为已发货，2为已收货
    # 已下单未付款详细信息
    Order_detailA = New_order_detail(order_id = 'order1',
                                    book_id = 1,
                                    count = 2,
                                    price = 2000)
    # 已付款未发货
    OrderB = New_order_undelivered(order_id = 'order2',
                            buyer_id = 'hahaa@ecnu.com',
                            store_id = 'NaiXue',
                            price = 10000,
                            purchaseTime = datetime.now())
    Order_detailB = New_order_detail(order_id = 'order2',
                                    book_id = 2,
                                    count = 1,
                                    price = 10000)
    # 已发货未收货
    OrderC = New_order_unreceived(order_id = 'order3',
                            buyer_id = 'hahaa@ecnu.com',
                            store_id = 'NaiXue',
                            price = 10000,
                            purchaseTime = datetime.now(),
                            # receiveTime=0#初始化为0表示还没有收到货
                            )
    Order_detailC = New_order_detail(order_id = 'order3',
                                    book_id = 2,
                                    count = 1,
                                    price = 10000)
    session.add_all([Order_detailC,Order_detailA,Order_detailB,OrderA,OrderB,OrderC])
    session.commit()
def init_books():
    '''
    导入书的详细信息,这个还要再详细研究book.py
    '''
    session.add_all([
        Book( book_id =1,
    title ='DB design Principle'),
    Book( book_id =2,
    title ='Gone with the wind')
    ])
    session.commit()

def init_test_all():
    init_testuser()
    init_books()
    init_teststore()
    init_testorder()
    

def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    #先drop再create
    Base.metadata.drop_all(engine)
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
