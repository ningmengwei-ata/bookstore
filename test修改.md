# 2021/1/6 test修改

hsy

* 因为原本的test代码中会因为导入图书的主码重复报错，因此相应的带动了相应部分代码



### be/model1/db_conn.py

1，连接数据库我用的postgres（用户名）和123456（密码）

### be/model1/seller.py

```
##重要！！！！！
            #判断书是否已经加在书里
            row = self.session.execute("SELECT book_id FROM book WHERE book_id = '%s';" % (book_id,)).fetchone()
            if row is None:
```

添加了判断书是不是在book表里，这样使得代码更加完善

 ### fe/access/book.py

1，将self.book_db = "D:/这学期/数据管理系统/大作业/项目/DB/fe/data/book.db"（路径改了，但是没有测试没改是不是可行）

### init_db/book.py

1，将book的price改为了original_price，为了和seller设定的price区分

2，book_db路径修改

3，去掉了用data.db设置主码（现在也可以修改回去）

### init_db/init_database.py

- 将所有表中的`user_id，store_id，buy_id`改为256的str，`order_id`改为512的str

(因为测试过程中生成的用户名和店铺名为长度为159的str，生成的订单是买家名和店铺名的join，因此需要设置长一点的str)







