

# 数据库finalproject实验报告

## 数据库设计

### ER图和导出的关系模型

- ER图

  ![ER图.png](http://ww1.sinaimg.cn/large/005ZSk16ly1gml580rb09j31hc0u0jxu.jpg)

- 导出的关系模型

  ![导出的关系模型.png](http://ww1.sinaimg.cn/large/005ZSk16ly1gml6j4iifcj30pg0dumxq.jpg)

### 具体表的结构设计

### 用户/商店表

**用户表**

| FIELD | User_id      | Password | Balance | Token  | Terminal | Address |
| ----- | ------------ | -------- | ------- | ------ | -------- | ------- |
| 类型  | String       | String   | Integer | String | String   | String  |
|       | 主键；唯一键 | 非空     | 非空    | 非空   | 非空     |         |

调整了原有用户表的结构，为收货发货做准备。当一个用户有多个收货地址时，可以考虑新增`user-address`表，满足一对多的关系。

**用户-商店关系表**

| FIELD | User_id | store_id   |
| ----- | ------- | ---------- |
| 类型  | String  | String     |
|       | 外键    | 唯一，非空 |

在数据库设计之初，我们在用户表中新增一列`username`，但是为了后面与test测试接口统一，将其删去。`username`和`user_id`的两个字段更符合真实场景中的设计逻辑，`user_id`可以是用户注册是的邮箱，手机号等，而`username`才是用户昵称等用户名。`store_id`也同理；

**商店表(商店-图书）关系表**

| FIELD | Store_id | Book_id | Stock_level | Price   |
| ----- | -------- | ------- | ----------- | ------- |
| 类型  | String   | String  | Integer     | Integer |
|       | 外键     | 外键    | 非空        | 非空    |

#### 订单总表

- 我们没有选择使用status_code：0，1，2，去将待发货订单，已发货待收货订单，已收获订单进行区分，而是新增了purchase_time和三张不同的订单类型的表，更好的支持用户查看交易时间，发货时间和收获时间。

- 逻辑上，订单表中的price与(商店-图书）关系表中的price字段的含义一致，都是具有时间变化性的价格，即不同的商家针对不同的书目有着自己的定价和折扣，更好的模拟淘宝真实的交易过程(如建议零售价，原价和购物券的叠加等)

**待付款订单**

当用户下单之后，订单会按照这个格式插入该表中。order_id为主码，区别不同的订单，buyer_id,store_id,price是为了方面查找订单数据。commit_time是为了记录提交订单时间和用于判断订单是否超时使用。

| FIELD | Order_id | buyer_id | Store_id | Price   | commit_time  |
| ----- | -------- | -------- | -------- | ------- | ------------ |
| 类型  | String   | String   | String   | Integer | DateTime     |
|       | 主键     | 外键     | 外键     |         | 订单提交时间 |

**待发货订单**

当用户付款之后，订单会按照这个格式插入该表中。order_id为主码，区别不同的订单，buyer_id,store_id,price是为了方面查找订单数据。purchase_time是为了记录付款订单时间。

| FIELD | Order_id | buyer_id | Store_id | Price   | Purchase_time |
| ----- | -------- | -------- | -------- | ------- | ------------- |
| 类型  | String   | String   | String   | Integer | DateTime      |
|       | 主键     | 外键     | 外键     |         | 订单付款时间  |

**待收货订单**

当卖家发货之后后，订单会按照这个格式插入该表中。order_id为主码，区别不同的订单，buyer_id,store_id,price是为了方面查找订单数据。send_time是为卖家发货时间，receive_time是记录买家的收货时间。

| FIELD | Order_id | buyer_id | Store_id | Price   | send_time    | Receive_time |
| ----- | -------- | -------- | -------- | ------- | ------------ | ------------ |
| 类型  | String   | String   | String   | Integer | DateTime     | DateTime     |
|       | 主键     | 外键     | 外键     |         | 订单发货时间 | 订单收货时间 |

这里新增一个收货时间字段。这样加的目的由于我们功能中不涉及对收货订单的评价，不需要另外增加待评价订单。通过receive_time区分已发货订单和未发货订单，并在查询用户订单功能中支持查询已收货和已发货未收货订单。

**已取消订单**

淘宝应用中new_order_detail包括用户的所有订单，也应包含new_order_cancel。new_order_cancel与new_order_undelivered等的并集为new_order。这样的添加使得订单的结构更加完善。对应需要修改手动删除，自动删除以及查询订单历史的函数。手动删除订单和自动删除后将对应订单插入该表。

| FIELD | Order_id | buyer_id | Store_id | Price   | CANCEL_time |
| ----- | -------- | -------- | -------- | ------- | ----------- |
| 类型  | String   | String   | String   | Integer | DateTime    |
|       | 主键     | 外键     | 外键     |         |             |

#### 订单明细表

对于订单类型区分有订单总表和订单明细表的原因：

**1.0版本**

| FIELD | order_id | Book_id | Count   | Price   |
| ----- | -------- | ------- | ------- | ------- |
| 类型  | String   | String  | Integre | Integer |
|       | 主键     | 外键    |         |         |

**针对查询优化的2.0版本**--应用驱动优化

由于在查询用户历史订单的功能应用中遇到之前的表结构查询效率较慢的问题，需要查询一个buyer的所有订单时，要在usr_store里查user买过的store的store_id, 再在store查买过的book_id 再在new_order_detail查book_id对应的具体信息。

故在new_order_detail中添加冗余属性store_id和buyer_id。

这样的修改方便用户查询所有订单信息，也方便卖家查自己店铺的所有订单信息。

| FIELD | order_id | Book_id | user_id | store_id | Count   | Price   |
| ----- | -------- | ------- | ------- | -------- | ------- | ------- |
| 类型  | String   | String  | String  | String   | Integer | Integer |
|       | 主键     | 外键    |         |          |         |         |



#### Book表(与book.db的schema基本保持一致)

- 在这里，书的概念要做详细说明，book_id不是表示的每一本书，而是每一类同名的书，如A店的《当代数据库管理系统》的book_id是1，B店的《当代数据库管理系统》这本书的book_id也是1，他们的book_id相同，但是不同店，甚至是同一个店不同的交易定价，这些书可以拥有属于自己的不同的价格。比如11.11那天0点A店的《当代数据库管理系统》这本书可以是30元，11.11日0点B店为29.99元。
- 在后续的进一步完善中，还可以使A店的《当代数据库管理系统》拥有不同的价格，在这里暂未实现
- 字段的text类型是为了全文索引功能的支持。

| FIELD | book_id    | Title | Author | Publisher | Original_title | translator | Pub_year | Pages | Original_price | Binding | Isbn | Author_intro | book_intro | cont ent | tags |
| ----- | ---------- | ----- | ------ | --------- | -------------- | ---------- | -------- | ----- | -------------- | ------- | ---- | ------------ | ---------- | -------- | ---- |
| 类型  | Integer    | Text  | Text   | Text      | Text           | Text       | Text     | Text  | Integer        | Text    | Text | Text         | Text       | Text     | Text |
|       | 主键，自增 | 非空  |        |           |                |            |          |       |                |         |      |              |            |          |      |





## 功能实现与性能分析

所有功能实现的数据库增删改查操作使用orm包装，避免sql注入，保障安全性，且实现了事务处理。

### user功能

#### **1.用户注册register**

功能实现：

1. 根据user_id判断该用户名是否已经存在。若已存在通error.error_exist_user_id(user_id)返回错误信息
2. 插入user_id、password、balance、token、termial信息至usr表。其中terminal由terminal_当前时间表示。token由jwt_encode生成。

性能分析：
         usr表一次根据user_id主键查询，一次插入。

#### **2.用户注销unregister**

功能实现：

1. 根据user_id查询该user是否存在。若不存在由error.error_authorization_fail()返回错误信息
2. 判断用户输入密码是否正确。若不正确由error.error_authorization_fail()返回错误信息
3. 删除根据user_id对应usr表中条目。

性能分析：
         usr表一次根据user_id主键查询，一次删除。

#### **3.用户登录login**

功能实现：

1. 根据user_id获取用户密码。
2. 与用户输入密码对比。若比对失败返回错误信息
3. 密码对比成功，更新usr中的token，terminal。

性能分析：
          usr表一次根据user_id主键查询，一次更新。

#### **4.用户登出logout**

功能实现：

1. 根据user_id调用check_token查询该user是否处于登陆状态。
2. 如果处于登陆状态则更新token。

性能分析：
           usr表一次根据user_id主键查询，一次更新。

#### **5.更改密码change_password**

功能实现：

1. 根据user_id获取用户原有密码,与用户输入的旧密码对比
2. 若比对成功，更新用户密码为当前输入的密码。

性能分析：
            usr表一次根据user_id主键查询，一次更新。

### buyer功能

#### **1.下单new_order**

功能实现：

1. 首先保证用户id和storeid存在，若不存在返回对应用户信息
2. 通过user_id，store_id，和唯一标识符相连生成uid
3. 根据订单信息在store表中查找商户中是否存在对应书籍和足够的库存。
4. 若满足对应条件，则在store中的库存减去下单的数量，并向new_order_detail表插入order_id,book_id,buyer_id,store_id,count,price属性信息
5. 记录下单时间，将订单信息插入new_order_unpaid

性能分析：

​         store表k次根据主键查询，k次更新，new_order_detail表k次插入，(k为订单中购买的书本数）new_order_unpaid表一次插入。

#### **2.支付payment**

功能实现：

1. 查询在new_order_unpaid表中是否存在属于用户的待付订单，获取订单总价，商户id。
2. 若存在，根据user_id获取用户密码。并与用户输入密码对比。
3. 比对成功，且用户余额大于待付价格，则付款成功，否则失败，返回对应错误信息。
4. 若付款成功，在usr表中给给买家减少余额，根据卖家id给增加卖家的余额
5. 在new_order_unpaid表中删除对应的待付订单信息
6. 记录当前时间，在待发货表new_order_undelivered表中加入订单信息和付款时间。

性能分析：
         new_order_unpaid表一次根据主键order_id查询，一次删除，user表两次根据主键user_id查询，两次更新（其中一次买家、一次卖家）new_order_undelivered表一次插入。

#### **3.买家充值add_funds**

功能实现：

1. 根据user_id获取用户信息，若记录不存在，返回error_authorization_fail()
2. 将密码与用户输入密码比对
3. 若密码正确，在usr表中更新用户余额。否则返回相应报错

性能分析：  

​         usr表一次根据主键user_id查询，一次更新。

#### **4.买家收货receive_book**

功能实现：

1. 根据传入的参数user_id获取用户信息，若记录不存在，返回`error.error_non_exist_user_id()`
2. 根据传入的参数order_id判断待收货的表里是否存在该记录，如果不存在，就返回`error_invalid_order_id(order_id)`
3. 判断订单中的买家和传入的buyer_id是否一致，如果不一致就返回`error_authorization_fail()`
4. 若订单存在，买家存在且匹配，在待收货表new_order_unreceived中添加买家收货的时间。

性能分析：

​		usr表一次查询；

​		new_order_unreceived表一次查询，一次更新。

测试用例：

1. 买家user_id不存在；

2. 订单order_id不存在；

3. 买家id存在但不匹配；

4. 买家和订单都存在，且相互匹配。

#### **5.查询历史订单信息**

​        为支持不同的查询订单需求，函数接口中除buyer_id另增加flag。类似淘宝查询界面，支持查询用户所有订单，待付款订单，已付款待发货订单，已发货待收货订单，已收货订单，已取消订单。通过flag进行区分。

功能实现：

查所有订单

1. 若用户不存在返回对应错误信息
2. 根据buyer_id查询new_order_detail
3. 查询成功，返回订单order_id，buyer_id，store_id，book_id，count和price信息。

查待待付款订单

1. 根据buyer_id和下单时间不为空在new_order_unpaid表中筛选记录
2. 对每一条记录，根order_id查询New_order_detail表，获取订单id，所购书籍列表（每本书的书名，价格，数量），下单时间，订单状态。
3. 将获取的记录包装成json对象，每个order下包含由订单id,下单时间，订单状态，所购书籍列表（书名，价格，数量）构成的数组。

查询已付款待发货订单，已发货待收货订单，已收货订单，已取消订单与查待待付款订单过程类似。只是返回订单状态不同，不再赘述。

性能分析：

​      查所有订单：new_order_unpaid表一次查询

​      查询待付款订单：new_order_unpaid表一次查询，对应new_order_detail表k次根据主键查询（k为new_order_unpaid的该用户待付记录数）

​      查询已付款待发货订单：new_order_undelivered表一次查询，对应new_order_undelivered表k次根据主键查询（k为new_order_undelivered的该用户待发货记录数）

​      查询已发货待收货订单：new_order_unreceived表一次查询，对应new_order_detail表k次根据主键查询（k为new_order_unreceived的该用户待收货记录数）

​     查询已取消订单：new_order_canceled表一次查询，对应new_order_canceled表k次根据主键查询（k为new_order_canceled的该用户已取消记录数）

 测试用例：

1. 正常情况（包括所有订单，待付款订单，已付款待发货订单，已发货待收货订单，已收货订单，已取消订单能否正常返回）
2. user_id不存在的情况
3. 用户无购买记录

#### **6.手动取消订单**

根据淘宝，如果卖家已发货需要申请售后来取消订单，这里我们只允许在未发货或未付款情况下才能取消订单

功能实现：

1. 根据order_id和buyer_id在new_order_unpaid中判断是否为待付款订单
2. 若是，在new_order_unpaid中删除对应订单
3. 根据order_id和buyer_id在new_order_undeliverd中判断是否为待发货订单
4. 确定订单未发货后。在usr表中更新买家余额增加该订单对应款项。
5. 在usr表中更新卖家余额减少该订单对应款项。
6. 在待发货表中删除对应记录。
7. 记录当前时间并将订单信息加入new_order_cancel表中。
8. 判断New_order_detail中的order_id是否为用户输入order_id，book_id是否与store对应，在new_order_detail表中筛选记录，在store表中将对应的书籍的库存加回。
9. 若不是上述两种情况，返回无法取消订单

性能分析：

​           new_order_unpaid表一次查询，一次删除，new_order_undelivered表一次查询，一次删除，new_order_cancel表一次插入，new_order_detail表一次查询，store表k次更新（k为购买书籍数），user表两次根据user_id主键查询，两次更新（一次买家、一次卖家）。 

测试用例： 

1. 已付款待发货
2. 未付款情况
3. user_id不存在情况
4. 已发货

#### **7.自动取消订单**

使用技术：

Redis键空间通知（过期回调）用户下单之后将订单id作为key，任意值作为值存入redis中，给这条数据设置过期时间，也就是订单超时的时间。

1，下载安装redis（电脑中和python中）

（以下方法仅针对windows电脑）

- 在redis文件中使用`redis-server.exe redis.windows.conf`启动redis

- 设置`redis.windows.conf`中的`notify-keyspace-events "EX"`（为了保证可以发出过期数据的数据）

  我们会收到关键事件通知，在keyevent频道中，我们会收到key作为消息。

- 可使用`redis-cli.exe --csv psubscribe '*' `测试服务是否打开

2，在python中使用redis，配置回调函数

注册回调函数来处理已发布的消息。消息处理程序只接受一个参数即消息。要使用消息处理程序订阅通道或模式，请将通道或模式名称作为关键字参数传递，其值为回调函数。当使用消息处理程序在通道或模式上读取消息时，将创建消息字典并将其传递给消息处理程序。在这种情况下，从*get_message（）*返回*None*值，因为消息已经处理完毕。

功能实现：

1. 在buyer()中的new_order函数中将订单号存入redis数据库中，并设置超时时间

2. 在回调函数auto_cancel_order中设置死循环，每当接收到一个过期数据，就将order_id解析出来。

3. 通过这个order_id判断能否找到未支付订单new_order_unpaid中的数据，
4. 如果存在，将其删除，在已取消订单new_order_canceled中添加该order和取消时间。
5. 如果不存在，说明该订单已被支付或者买家主动取消订单，则什么都不用处理。

```python
#连接redis数据库
r=redis.StrictRedis(host='localhost',port=6379,db=0,decode_responses=True)
# 创建pubsub对象，该对象订阅一个频道并侦听新消息：
pubsub=r.pubsub()
#收到消息的处理函数
 def event_hander(msg):
    # print('Handler',msg)
    order_id=str(msg['data'])
    print(order_id)
    #如果能找到订单，就删除未支付订单
    #添加到已删除订单中 
    #将商店中的书籍书加回去
#订阅过期数据
pubsub.psubscribe(**{'__keyevent@0__:expired':event_hander})
#死循环，当有数据过期时，调用函数event_hander处理过期数据
while True:
    # print("监控超时订单")
    #获得事件信息，有结果就会回调函数
    message=pubsub.get_message()
    time.sleep(0.1)
```

性能分析：

​           redis数据库一次更新（插入数据）。 

​			当接收到数据时，对new_order_unpaid一次查找；

​			当数据存在，对new_order_unpaid一次更新；对new_order_canceled一次更新。

测试用例： 

1. 未支付订单中超时
2. 未支付订单未超时

使用方法：

单独开一个进程运行自动取消订单的程序，然后再运行服务器app.py，可实现自动取消订单。测试也能够通过

- 如果不测试自动取消订单，将model1中带注释的代码注掉，然后再把test文件中的test_auto_model.py文件注掉，方便测试（因测试自动取消订单需要等待20s，如果不测试自动取消就没有必要）



### seller功能

#### **1.上架图书add_book**

实现两种版本可支持只上架图书，或可将书籍添加到book表中并上架图书（该版本可以不运行book.py导入数据，通过add_book函数插入书籍）

这里传参接口增加price属性，需要商家自己定价，而不是传入书籍的零售价。

版本1:

1. 检查user_id，store_id以及book_id是否已存在。若不存在返回对应错误信息
2. 将store_id, book_id, 出售价格插入store表。

性能分析：
         usr表一次根据主键user_id查询，store表一次根据主键store_id查询，book表一次根据主键book_id查询，store表一次插入。

版本2:

1. 在版本一的基础上增加根据book_id从book表查询判断书是否已经在book表中
2. 如果不在，插入书籍的所有信息

注意该版本事务add_book是包括添加图书，将书籍添加到商店这两步

我们初始代码是两步结束后才commit，就导致第一步的图书还没添加进去，就在做第二步的将书籍添加到商店,而因为store里面的book_id必须存在在book表中，在重建数据库测试时会出现问题。在添加完图书（做完第一步）之后添加self.session.commit()即可解决

性能分析：

​       usr表一次根据主键user_id查询，store表一次根据主键store_id查询，book表一次根据主键book_id查询,一次插入，store表一次插入。

#### **2.创建店铺create_store**

1. 检查user_id和store_id是否已存在。若不存在返回对应错误信息
2. 插入用户id，新建店铺store_id至user_store表。

性能分析：
        usr表一次根据主键user_id查询，store表一次根据主键store_id查询，user_store表一次插入。

#### **3.添加库存add_stock_level**

1. 检查user_id、store_id和book_id是否已存在。若不存在返回对应错误信息
2. 根据store_id, book_id对store表查询卖家商店中的书籍库存量，并在store表中更新库存，加上传入的库存数。

性能分析：
        usr表一次根据主键user_id查询，store表一次根据store_id主键查询，一次更新。

**4.卖家发货deliver_book(额外功能)**

1. 功能实现：

   1. 根据传入的参数user_id获取用户信息，若记录不存在，返回`error.error_non_exist_user_id()`
   2. 根据传入的参数order_id判断待发货的表里是否存在该记录，如果不存在，就返回`error_invalid_order_id(order_id)`
   3. 判断订单中的卖家和传入的seller_id是否一致，如果不一致就返回`error_authorization_fail()`
   4. 若订单存在，卖家存在且匹配，在待发货表new_order_undelivered删除该订单，在待收货表new_order_unreceived中添加该订单和发货时间。

   性能分析：

   ​		usr表一次查询；

   ​		new_order_undelivered表一次查询，一次更新。

   ​		new_order_unreceived表一次更新。

   测试用例：

   1. 买家user_id不存在；

   2. 订单order_id不存在；

   3. 卖家id存在但不匹配；

   4. 卖家和订单都存在，且相互匹配。



### 实验过程中遇到的问题和解决方法

#### **1.VScode中误报(import-error)解决**

在vscode中点击文件->首选项->设置，在搜索框中输入：pylintArgs

在搜索的结果Python>Linting:Pylint Args中点击添加项，分别添加—errors-only已及—disable=E0401，保存，退出设置，重启vscode既可解决

![w1.png](http://ww1.sinaimg.cn/large/005ZSk16ly1gml7fqbqrzj31ng0h2q6x.jpg)

#### **2.user_id = request.json.get("user_id", "")AttributeError: 'NoneType' object has no attribute 'get'**

postman测试的body没有设置为json格式导致前端无法解析

#### **3."'tuple' object has no attribute 'keys'"**

![w2.png](http://ww1.sinaimg.cn/large/005ZSk16ly1gml7gd6vexj31ls0gagox.jpg)

由于数据库语句书写格式错误，如应该应该是set xx,xx写出set xx and xx等

`"UPDATE usr set token= '%s' , terminal = '%s' where user_id = '%s'"`

#### **4.init_db文件夹中的book.py是插入书籍信息，但在vscode无法访问路径。**

将`self.book_db `改为绝对路径

#### **5.当运行测试时会报530error，发现无法插入数据**

将所有表中的`user_id，store_id，buy_id`改为256的str，`order_id`改为512的str(因为测试过程中生成的用户名和店铺名为长度为159的str，生成的订单是买家名和店铺名的join，因此需要设置长一点的str)

#### **6.运行init_database.py文件导入数据时会报错，键值不存在**

将每个表中的插入都commit，以免出现键值不存在的情况

```python
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
```

## 额外功能：Search功能实现

### search索引构建

### 要求

搜索图书
用户可以通过关键字搜索，参数化的搜索方式； 如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。 如果显示结果较大，需要分页 (使用全文索引优化查找)

### searchDB数据库的构建

在book表中，显然在4w条数据的大数据情况下，外加picture的BLOB类型字段,author_intro和book_intro中的TEXT类型字段内容过长的问题，如果单纯的在book表中进行关键字搜索，及时是使用了索引，也会导致搜索速度过慢而用户难以忍受的问题，所以决定将book表中的字段的一部分，分表对应author,title,tags,book_intro四列新建表格，以小部分的冗余存储为代价，建立数据库高效搜索效率。

### searchDB schema

具体建表代码见`init_db/search.py`，全文索引构建见`search-index.sql`，全文索引构建需要中文分词器`zhparser`

初始建表代码以search_title表为例子

```python
class SearchTitle(Base):
    __tablename__ = 'search_title'
    search_id=Column(Integer,autoincrement=True,primary_key=True)
    title = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
```

### Basic-Tables



`seach_author`:

![截屏2021-01-10 17.47.00](https://tva1.sinaimg.cn/large/008eGmZEgy1gmiqsn8jd6j30b203kt93.jpg)

`search_tags:`

![截屏2021-01-10 17.47.19](https://tva1.sinaimg.cn/large/008eGmZEgy1gmiqsts3gcj30ha03kaai.jpg)

`search_title:`

![截屏2021-01-10 17.48.27](https://tva1.sinaimg.cn/large/008eGmZEgy1gmiqu0enuzj30h003gt9b.jpg)

`search_book_intro`

![截屏2021-01-10 17.49.10](https://tva1.sinaimg.cn/large/008eGmZEgy1gmiqur99hkj30ck03gwez.jpg)

> 可以看出，在searchDB的每一张Table,我们只寻找一种高效的检索方式需要把book_id选出来即可。

### 关键字搜索实现

#### 模糊和通配查询实现

在搜索功能实现的第一阶段，我最先想到的使用`like`进行通配查询，在相应的搜索字段中构建主键B-树索引，对应的SQL查询为`SELECT * from search_book_author where author like '%杨红%'；`

#### 模糊查询的缺点

事实证明，对于这种用户输入字段的前后部分都是用了`%`的情况，尤其是相当于搜索`%s`时，即后缀匹配的情况时，我们建立在主键上默认的B树索引即失去了范围查询中的效率。所以，这种模糊查询的方式是不佳的。

使用`EXPLAIN ANAYLYZE`语句查看这种模糊匹配

后缀匹配时会导致我们的索引失效，最终还是全表扫描，在信息检索系统中，通过构建**轮排索引**可以避免这种全表扫描。

### 全文索引--postgresql全文索引GIN索引

#### Postgresql全文搜索：to_tsvector()和to_tsquery()

1. to_tsvector实际上把语句转换成了tsvector(文档格式-包含文档值和角标)

   如：

   `SELECT * FROM to_tsvector('parser_name',TEXT)`

   `Input:SELECT * FROM to_tsvector('parser_name','小明今天去上学')`

   `Output:'上学'：3 '去'：2 '小明'：1`

   通过output，我们可以看到“上学”对应位置3，“小明”对应语句的位置1，我们记住这种格式就行，后续会用到。

2. to_tsquery()，实际上就是一个传递的参数格式，可以搭配中文分词规则，把一句话拆成多个词传递过去

   `Input:SELECT * FROM to_tsvector('parser_name','小明今天去上学')`

   `Output:'上学'& '去'& '小明'`

3. 结合`to_tsvector()`和`to_tsquery()`,即可完成本次数据库的关键字全文搜索功能。

#### 全文搜索技术：分词

PSQL本身是不支持全文索引的，所以在分词解释器没有构建的情况下，`SELECT * FROM to_tsvector('parser_name','小明今天去上学')`的结果还是`'小明今天去上学':1`,这样我在整个字段上创建索引也不能达到用户输入模糊查询的效果，所以需要引入中文分词解释器`zhparser`

所以，在什么字段上构建索引是很重要的一件事。

在搜索系统中，分词很大的影响了了搜索系统的召回率和准确率，一起我们的4个基础table表的大小。

1. 分词粒度越精细，4个基础table表的大小越大，消耗的空间也越大，搜索的表格也越大。
2. 如果直接使用postgresql数据库内分词，如果以数据库能解决就不用其他外部工具甚至代码解决而不是先用外部程序进行分词新增列和行，会降低数据库全文搜索的效率，同时，也会有postgresql的程序执行效率很低，导致文章最后的分词函数占用大量CPU的问题。
3. 当然，当原始数据集过多，存储了外部分词结果的修改后的数据集就会成线性倍数的增长，消耗存储空间。这里有一个搜索效率和存储的trade-off

#### 最终全文搜索功能实现

##### 外部中文分词程序

###### Search_author

在对author字段进行分词初步索引的构建的时候，我尝试了3种分词方式，当然这3种分词方式本身也受：

1. 模拟用户输入的最长前缀：

   杨；杨红；杨红樱

   ````python
    for k in range(1, to_string_len + 1):
                       row_to_insert=SearchAuthor()
                       if to_string[k - 1] == '':
                           continue
                       if to_string[k - 1] == '美' or to_string[k - 1] == '英':
                           continue
                       j = to_string[:k]
                       row_to_insert.author=j
                       row_to_insert.book_id=row.book_id
                       session.add(row_to
   ````

2. 2-gram模型：

   杨红，红樱；(但仍把作者的姓加进去提高召回率，符合中文作者姓名和中文读者的搜索习惯)

3. 不提前分割，仅依赖zh-parser的预先分割功能生成新列。

   ```python
       if len(to_string)==0:
                       to_string=row.author
                   row_to_insert.author=to_string
                   row_to_insert.book_id=row.book_id
                   session.add(row_to_insert)
                   session.commit() 
   ```

最后的分词方式：

2-gram+存储作者姓和全称字段(如果全称字段被zh-parser自动分割，也仍然无法提高召回)

###### Search_book_intro

因为book_intro都是大量的文本，通过对文本提取关键词的方式进行分割，提取关键词的方法有很多，有TF-IDF,TextRank等。

这里使用基于图的TextRank方法提取关键词，限制关键词最多不超过20个，即修改后的search_book_intro表最大为原表的20倍。

###### Search_tags

tags是已提取好的标签，直接把tags拆开插入的修改后的表中。

###### Search_title

title字段和author字段都是短文本，他们最显著的区别是，姓名字段的字与字之间没有明显强烈的上下文关系，如杨红樱三个字与《一个狗娘养的自白》这个标题相比，显然是标题的字与字之间更具有上下文的关系，所以在search_title部分我没有采用形如search_author一样的粒度划分，而是直接采用了zh-parser本身分词功能对与search_title表格的修改。

###### **最终的修改表的语句如下：**

详见`search-index.sql`

```sql
ALTER TABLE search_author ADD COLUMN tsv_column tsvector;           
UPDATE search_author SET tsv_column = to_tsvector('zh', coalesce(author,''));   
CREATE INDEX idx_gin_author ON search_author USING GIN(tsv_column); // 
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_author FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', author);
```

我自己测试4w条书的book_intro分词后的库初始化![大致时间](https://tva1.sinaimg.cn/large/008eGmZEly1gmiw1dmxfyj31h10mpjzh.jpg)

我自己测试4w条书的其它分词初始化大致时间总体还是在可接受的范围内。

![其它三项初始化时间](https://tva1.sinaimg.cn/large/008eGmZEly1gmiw1emotgj31wy08awh2.jpg)

##### 索引构建--GIN

使用索引可以提高全文检索的效率，在postgresql官方文档中，官方推荐`GIN`通用倒排索引。而GIN索引的构建，根据postgresql官方的要求，必须指定分词规则。

`CREATE INDEX idx_gin_zh ON search_book_intro USING GIN(tsv_column); `

###### GINindex构建时间

PotsgreSQL提供的pg_trgm的扩展中有两种索引类型，一个是`gin`，一个是`gist`这两个选择的不同从使用上主要是`gist`构建速度比较快，搜索速度比`gin`慢，而`gin`相反，搜索速度很快，构建速度非常慢，而我在278549条数据上构建GIN索引大概只需要1.5s，还是可以在本次实验的数据规模上接受的，所以我直接使用了GIN-index。![截屏2021-01-10 20.53.06](https://tva1.sinaimg.cn/large/008eGmZEly1gmiw68ilkpj314606ogp0.jpg)

`TABLE search_author`的行数如下(使用代码解决分词后)

![截屏2021-01-10 20.54.15](https://tva1.sinaimg.cn/large/008eGmZEly1gmiw7fw21rj30vq066weq.jpg)

##### 搜索性能比较

以数据量最大的`TABLE search_book_intro`为例子

![截屏2021-01-10 20.58.19](https://tva1.sinaimg.cn/large/008eGmZEly1gmiwbkmqtpj30vq05u75p.jpg)

由上图可见数据量为70w行数据

###### 在tsv_column上构建GIN索引

![截屏2021-01-10 20.59.48](https://tva1.sinaimg.cn/large/008eGmZEly1gmiwd67ntcj30z605umz6.jpg)

第一次搜索`search_book_intro`关键词`世界`，用时为`0.529S`

![截屏2021-01-10 21.00.11](https://tva1.sinaimg.cn/large/008eGmZEly1gmiwdixzzbj30z607amzw.jpg)

第二次搜索`search_book_intro`关键词`世界`，用时为`0.006S`

![截屏2021-01-10 21.04.17](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjg1rdiicj315g0f8jv0.jpg)

###### 因为提前进行了外部分词，利用主键索引进行搜索

可以通过`EXPLAIN ANALYZE`命令查看两种搜索方式的对比

![截屏2021-01-10 21.08.59](https://tva1.sinaimg.cn/large/008eGmZEly1gmiwmp5hofj315g0h8gv3.jpg)

###### 没有提前进行外部分词，直接使用模糊查询的前后缀匹配

在没有进行分词的4w条数据上，直接进行前后缀匹配的模糊查询：

`SELECT * FROM book WHERE book_intro like '%生活%'`

![截屏2021-01-11 10.38.01](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk0h0f8aj30yk06m0vj.jpg)

`SELECT * FROM book WHERE book_intro like '生活%'`

![截屏2021-01-11 10.38.01](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk0h0f8aj30yk06m0vj.jpg)

`SELECT * FROM book WHERE book_intro like '%生活'`

![截屏2021-01-11 10.38.25](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk0w3u89j30yk06m0vk.jpg)

可以很明显的看出，无论是前缀匹配还是后缀匹配中，即使是在book_intro字段建立了索引，这个执行时间也很可怕。是用户难以忍受的。

![截屏2021-01-11 10.42.41](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk5bsem5j315k072jv4.jpg)

### 分页查询

#### 基本分页查询

一般性分页 使用 limit [offset,] rows 偏移量的问题在于如下两种：
如果偏移量固定，返回记录量对执行时间有什么影响？如分别比较
`select * from user limit 10000,1`;`
select * from user limit 10000,10;`
`select * from user limit 10000,100;`
`select * from user limit 10000,1000`;
`select * from user limit 10000,10000;`

这种分页查询机制，每次都会从数据库第一条记录开始扫描，越往后查询越慢，而 且查询的数据越多，也会拖慢总查询速度

#### 引入search-id的分页查询优化与直接使用GIN INDEX+LIMIT的分页查询优化

利用覆盖索引优化
select * from user limit 10000,100;
select id from user limit 10000,100;

利用子查询优化
select * from user limit 10000,100;
select * from user where id>= (select id from user limit 10000,1) limit 100;(使用了索引id做主键比较(id>=)，并且子查询使用了覆盖索引进行优化。)

通过这种思路，可以引入search_id进行分页查询的优化

#### 最终分页查询功能的实现

```sql
EXPLAIN ANALYZE SELECT DISTINCT book_id FROM search_book_intro WHERE book_id in (SELECT book_id FROM search_book_intro WHERE tsv_column @@ '美丽') LIMIT 100
- 在本次project中我使用的分页查询：
Limit  (cost=4719.78..4720.78 rows=100 width=4) (actual time=36.313..36.343 rows=100 loops=1)
  ->  HashAggregate  (cost=4719.78..4737.73 rows=1795 width=4) (actual time=36.312..36.331 rows=100 loops=1)
        Group Key: search_book_intro.book_id
        Batches: 1  Memory Usage: 73kB
        ->  Hash Join  (cost=341.50..4715.30 rows=1795 width=4) (actual time=1.014..35.925 rows=1976 loops=1)
              Hash Cond: (search_book_intro.book_id = search_book_intro_1.book_id)
              ->  Seq Scan on search_book_intro  (cost=0.00..3925.55 rows=163155 width=4) (actual time=0.649..15.253 rows=163155 loops=1)
              ->  Hash  (cost=340.28..340.28 rows=97 width=4) (actual time=0.232..0.234 rows=104 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 12kB
                    ->  HashAggregate  (cost=339.31..340.28 rows=97 width=4) (actual time=0.200..0.215 rows=104 loops=1)
                          Group Key: search_book_intro_1.book_id
                          Batches: 1  Memory Usage: 24kB
                          ->  Bitmap Heap Scan on search_book_intro search_book_intro_1  (cost=12.76..339.07 rows=98 width=4) (actual time=0.063..0.171 rows=104 loops=1)
                                Recheck Cond: (tsv_column @@ '''美丽'''::tsquery)
                                Heap Blocks: exact=100
                                ->  Bitmap Index Scan on idx_gin_zh  (cost=0.00..12.73 rows=98 width=0) (actual time=0.045..0.045 rows=104 loops=1)
                                      Index Cond: (tsv_column @@ '''美丽'''::tsquery)
Planning Time: 0.223 ms
Execution Time: 36.407 ms
```

使用GIN-index,限制是285条(其实这个限制了全局，比search_id的扫描范围要广一些)

![截屏2021-01-10 21.22.48](https://tva1.sinaimg.cn/large/008eGmZEgy1gml78bxduzj31cq0gmk1i.jpg)

使用GIN-index,限制是285条(使用search_id 的主键B树索引的285条数据)

![截屏2021-01-10 21.21.20](https://tva1.sinaimg.cn/large/008eGmZEly1gmiwzj9777j31cq062wgq.jpg)![截屏2021-01-10 21.23.17](https://tva1.sinaimg.cn/large/008eGmZEly1gmix1llovxj31cq0dy10k.jpg)

### 后端代码实现

逻辑上来讲，任何一家书店拥有的书的数量，跟整个图书商城，比如当当，淘宝整个全站搜索库里的书的数量相比是很少的，所以，seachDB的四张表中的都是针对全部book库中的数据，对于每一个店家，没有额外进行建表的必要。

所以，在`SQL`查询语句确定了以后，后端实现的逻辑如下：

1. 首先获得book_db库中符合全局搜索的`book_id`
2. 对于全局搜索直接返回
3. 对于本店搜索，则使用子查询，搜索本店和全局检索出的`book_id`重复的部分。

为了节省篇幅，在此即不附后端实现的代码了，具体可以见`be/model1/buyer.py`下面的`search_functions_limit`函数。

### 总结与提升

`SELECT * FROM search_author WHERE tsv_column @@'杨红'`

![截屏2021-01-10 21.31.11](https://tva1.sinaimg.cn/large/008eGmZEly1gmix9tk1rhj31cq0oqal5.jpg)

`SELECT * FROM search_author WHERE tsv_column @@'红樱'`

![截屏2021-01-10 21.31.47](https://tva1.sinaimg.cn/large/008eGmZEly1gmjjws5fvzj31cq05maam.jpg)

`SELECT * FROM search_author WHERE tsv_column @@'樱'`

![截屏2021-01-10 21.32.28](https://tva1.sinaimg.cn/large/008eGmZEly1gmixbcyvb9j31cq0nk778.jpg)

从上面这三个很简单的例子可以看出，搜索系统中最关注的准确率和召回率的提升，应更多的从分词规则的角度进行考虑，在数据库+信息检索的方面有待提升。

> 一般的，在检索系统中，人们倾向于接受不那么相关的结果，而不是返回一个0结果值的检索系统。

## 理论reference

1. [PostgreSQL全文检索简介](https://cloud.tencent.com/developer/article/1430039)
2. [MacOS系统上Postgresql中文全文搜索配置](https://behaiku.org/blog/textsearch-of-postgresql-on-macos/)
3. [PostgreSQL关于中文搜索的简单尝试](https://zhuanlan.zhihu.com/p/21530240)
4. [不要头大！基于PostgreSQL的全文搜索干货！](https://blog.csdn.net/weixin_37096493/article/details/106302184)
5. [PostgreSQL、MySQL高效分页方法探讨](https://segmentfault.com/a/1190000021287858)

## 开发流程

### 1.版本控制

以下是本次项目版本控制的部分截图：

![图片4.png](https://i.loli.net/2021/01/12/LOMRprxB5SbZzjE.png)

cxn在github中建仓库并添加合作者，直接fork原始数据库项目，另两位组员fork到自己的仓库并向该仓库发起pull request请求，所有合作者都可以merge request。

![图片6.png](https://i.loli.net/2021/01/12/1cgKVWQX7nP9y5i.png)

github首页commit书截图如下

![图片5.png](https://i.loli.net/2021/01/12/faziDCIukESj63Q.png)

### 2.测试驱动开发(TDD)

在所有测试功能实现时，我们首先编写test_case再对对应的后端功能进行编写完善。通过测试来推动整个开发的进行。这有助于编写简洁可用和高质量的代码，并项目整体的加速开发过程，提高了代码效率和覆盖率。



### 3.应用驱动优化

在功能实现的过程中发现初始表结构查询效率较低，故做了相应的修改和调整。在故在new_order_detail中添加冗余属性store_id和buyer_id。这样的修改方便用户查询所有订单信息，也方便卖家查自己店铺的所有订单信息。

同时在实现取消订单的过程中，考虑表结构的完整性另添加new_order_cancel表。

## 实验结果

1.共计50个test case，全部测试通过！

![图片1.png](https://i.loli.net/2021/01/12/2yzIQ13HoCNUcAm.png)

2.覆盖率达93%

![图片2.png](https://i.loli.net/2021/01/12/wKly9zFEjiMgpUW.png)

3.吞吐量与延迟

mac测试吞吐量达18750笔/秒
平均下单延迟0.03秒
平均付款延迟0.022秒

![图片3.png](https://i.loli.net/2021/01/12/edMq6oBPcbx9wI5.png)

## 小组分工

cxn：数据库初始设计，搜索图书功能设计，搜索功能实现，吞吐量测试，git版本控制，PPT制作，报告撰写

hsy：add_book优化，扩展功能的发货收货、自动取消订单，吞吐量测试，ER图制作，测试完善，git协作，PPT制作，报告撰写

wwq：基础功能实现，扩展功能的查询历史订单、手动取消订单，吞吐量测试，数据库结构优化，git协作，PPT制作，报告撰写

## 实验总结

善于利用postman测试代码中的问题

善于使用测试文件检验代码是否具有高可用性(测试驱动开发)
