# 2020.12.20更新(cxn)

cxn: 第一轮初始化数据库，添加了一些样例/用户和一点书(书的信息是我自己插进去的，等会再研究怎么把所有书的数据按照助教学长的格式读入进去) <br>

## 运行方式：
### 先要把把本地数据库连接的用户名和密码改了
就是下面这个地方<br>
engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)<br>
cd 进be/init_db/文件夹, `python init_database.py'
## 亟待解决的问题
1. user_id和username还留不留，我写成user_id=user_Login_account,就类似于我们日常用的淘宝用户名和注册邮箱
2. 书的详细信息存储表格的设计
3. git协作和咋设成私有仓库的还没太学会Orz

# 2021.1.2更新(cxn)
图书基本schema与助教数据集中schema保持一致
将图片BLOB数据分离另新建表：
> 原要求2.核心数据使用关系型数据库（PostgreSQL或MySQL数据库）。 blob数据（如图片和大段的文字描述）可以分离出来存其它NoSQL数据库或文件系统。

# 2021.1.3更新(cxn)
 初始化数据库执行 init_database.py
 最终的book-schema
class BookWhole(Base):
    # PostgreSQL提供text类型， 它可以存储任何长度的字符串。
​    __tablename__ = 'book'
​    book_id = Column(Integer, primary_key=True,autoincrement=True)#自增
​    title = Column(Text, nullable=False)
​    author = Column(Text,nullable=True)
​    publisher = Column(Text,nullable=True)
​    original_title = Column(Text,nullable=True)
​    translator = Column(Text,nullable=True)
​    pub_year = Column(Text,nullable=True)
​    pages = Column(Integer,nullable=True)
​    price = Column(Integer,nullable=True)  
​    binding = Column(Text,nullable=True)
​    isbn = Column(Text,nullable=True)
​    author_intro = Column(Text,nullable=True)
​    book_intro = Column(Text,nullable=True)
​    content = Column(Text,nullable=True)
​    tags = Column(Text,nullable=True)

> - 先执行init_database.py，再执行book.py    
>   如果遇到报错，unable to opendatabase file,是执行文件的路径的问题，需要在DB这个目录下执行 `python init_db/book.py`而不是在 init_db这个目录下执行`python book.py`不然就会报错！！！！
>
> - 报没有table 'book‘ 错误可能是因为book_db的路径没有设置正确，可以尝试将图书数据的绝对路径写在`BookDB   __init__   else `后面。

图片另建新表跟检索有关
所有价格都是分：原爬下来的没单位我也默认成分了。
如果遇到报错 可能需要执行drop table book cascade;
图书库的数据量可以在book.py下的`init_postgresql(self,start,size)`里面更改，通过参数更改数量。
豆瓣3G多的数据暂时没有放进来，所以fe/data/book.db和fe/data/book_lx.db是一样的，太大了，git不方便
用Navicat可以打开book.db文件，看看里面数据长啥样子可以从这里



# 2021.1.3 更新   ER图设计（hsy）

- 完成了出版ER图设计，由ER图可以导出8个表格，都已有构建和初始化代码。

- ER图位置： init_db/ER图.png

# 2021.1.8 更新 数据库new_order_detail优化(wwq)
应用驱动优化

由于在查询历史订单功能中遇到之前的表结构查询效率较慢，需要查询一个buyer的所有订单时，要在usr_store里查user买过的store的store_id, 再在store查买过的book_id 再在new_order_detail查book_id对应的具体信息。

故在new_order_detail中添加冗余，添加store_id和buyer_id。

这样的修改方便用户查询所有订单信息，也方便卖家查自己店铺的所有订单信息。

```python
# 订单明细表
class New_order_detail(Base):
    __tablename__ = 'new_order_detail'
    order_id = Column(String(512), nullable=False)
    book_id = Column(Integer, nullable=False)
    store_id=Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    buyer_id=Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'book_id'),
        {},
    )
```

由于数据库的修改，需要对应修改init_database的数据初始化以及buyer.py中的new_order函数

```python
 new_order_info = New_order_detail(order_id=uid, book_id=book_id,buyer_id=user_id ,store_id=store_id, count=count, price=price)
                self.session.add(new_order_info)
```

从而避免向非空属性插入空值的报错
# 2021.1.9 更新 数据库优化(wwq)
应用驱动优化
添加new_order_cancel表
```python
class New_order_canceled(Base):
    __tablename__ = 'new_order_canceled'
    order_id = Column(String(512), primary_key=True)
    buyer_id = Column(String(256), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(256), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    cancel_time = Column(DateTime, nullable=False)
```


淘宝应用中new_order_detail包括用户的所有订单，也应包含new_order_cancel。new_order_cancel与new_order_undelivered等的并集为new_order。这样的添加使得订单的结构更加完善。对应需要修改手动删除 自动删除以及查询订单历史的函数

# 2021.1.9 更新  Search搜索库建立更新 (cxn)
最终数据库执行顺序:
1. init_database.py
2. book.py(可以及时在里面调一些参数)
3. search.py
4. Navicat可视化查看
5. 配置好zh-parser以后，比较方便得到反馈的是在Navicat里直接按条复制执行`search-index.sql`中得到，最好是一条条复制方便及时显示报错。

> search_index.txt/test_search_again.sql是我备份用的，你们可以直接忽略
> 我自己测试4w条书的book_intro分词后的库初始化![大致时间](https://tva1.sinaimg.cn/large/008eGmZEgy1gmh79ud7tbj31h10mpgth.jpg)
> 我自己测试4w条书的其它分词初始化大致时间总体还是在可接受的范围内。
![其它三项初始化时间](https://tva1.sinaimg.cn/large/008eGmZEly1gmh7cm39inj31wy08ajws.jpg)

