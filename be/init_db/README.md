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

