### orm 完善

wwq

##### 修改

1.修改了init_db中的class名称，不影响表名

```
class Users(Base):
```

2.修改了所有数据库语句为orm格式 保证安全性 防止黑客攻击

3.注释掉了seller.py的tag格式转换，不影响test测试，可以让覆盖率增加1%

```
row=self.session.query(BookWhole).filter_by(book_id=book_id).first()
            if row is None:
                # book = json.loads(book_json_str)
                # thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
                # for tag in book.get('tags'):
                #     if tag.strip() != "":
                #         # book.tags.append(tag)
                #         thelist.append(tag)
                # book['tags'] = str(thelist) 
```

4.在seller.py 和buyer.py

插入数据后在self.session.commit()后添加了self.session.close()



##### **后期需要考虑的点**

1.seller.py add_book

1)目前插入书籍中没有插入图片

2）在向store中插入价格处

```
###这里需改动 函数接口中增加price 这里为用户输入的价格 不是书的零售价 目前不影响测试

store.price=books['price']
```

