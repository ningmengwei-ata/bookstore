### Add_book完善 查询订单历史&手动取消订单

#### Add_book优化(hsy)

```python
books.book_intro=book['book_intro']
                books.content= book['content']
                books.tags=book['tags']
                
                self.session.add(books)
                print("book info success")
          ##这里添加seesion.commit
                self.session.commit()
            store=Store()
```

事务add_book是包括 添加图书 添加商店 这两步
因为我们最后才commit，就导致第一步的图书还没添加进去，就在做第二步的添加商店,而因为store里面的book_id必须存在在book表中，在重建数据库测试时会出现问题。在添加晚图书之后self.session.commit()即可解决





wwq

#### 1.优化数据库结构

(**注意运行测试前要先删除数据库重新运行 只运行init_database.py** )

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

#### 2.功能添加

1.添加查询订单历史功能 测试通过(postman测试方法已添加在doc的md文件中)

测试用例

- Test_ok 测试正常情况 （测试能否正确查到未付款、已付款未发货、已发货未收货、已收货的历史订单信息）
- 测试用户不存在
- 测试用户没有购买记录

2.添加手动取消订单功能 测试通过

测试用例

- 已付款未发货
- 未付款
- User_id不存在
- 已发货

#### 3.add_book完善

1.调整函数接口 传price 将用户定义的售价传入store中

1）修改be/view1/seller.py

def seller_add_book():

```python
code, message = s.add_book(user_id, store_id, book_info.get("id"),book_info.get("price"), json.dumps(book_info), stock_level)
```

传入用户输入的价格

2）修改be/model1/seller.py

```python
def add_book(self, user_id: str, store_id: str, book_id: str,price:int, book_json_str: str, stock_level: int):
```

```python
            store=Store()
            store.book_id=int(book_id)
            store.store_id=store_id
            store.stock_level=stock_level
            ###这里需改动 函数接口中增加price 这里为用户输入的价格 不是书的零售价 目前不影响测试
            #store.price=book['price']
            store.price=price
            self.session.add(store)
```

2.seller.py的add_book

```python
books.content= book['content']
books.tags=book['tags']
#将原先的book改为books       
self.session.add(books)
```

