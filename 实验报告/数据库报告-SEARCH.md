# 数据库报告-search

## search索引构建

### 要求

搜索图书
用户可以通过关键字搜索，参数化的搜索方式； 如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。 如果显示结果较大，需要分页 (使用全文索引优化查找)

## searchDB数据库的构建

在book表中，显然在4w条数据的大数据情况下，外加picture的BLOB类型字段,author_intro和book_intro中的TEXT类型字段内容过长的问题，如果单纯的在book表中进行关键字搜索，及时是使用了索引，也会导致搜索速度过慢而用户难以忍受的问题，所以决定将book表中的字段的一部分，分表对应author,title,tags,book_intro四列新建表格，以小部分的冗余存储为代价，建立数据库高效搜索效率。

## searchDB schema

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

## 关键字搜索实现

### 模糊和通配查询实现

在搜索功能实现的第一阶段，我最先想到的使用`like`进行通配查询，在相应的搜索字段中构建主键B-树索引，对应的SQL查询为`SELECT * from search_book_author where author like '%杨红%'；`

### 模糊查询的缺点

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

###### 在tsp_column上构建GIN索引

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

![截屏2021-01-11 10.31.47](/Users/chixinning/Library/Application Support/typora-user-images/截屏2021-01-11 10.31.47.png)

`SELECT * FROM book WHERE book_intro like '生活%'`

![截屏2021-01-11 10.38.01](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk0h0f8aj30yk06m0vj.jpg)

`SELECT * FROM book WHERE book_intro like '%生活'`

![截屏2021-01-11 10.38.25](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk0w3u89j30yk06m0vk.jpg)

可以很明显的看出，无论是前缀匹配还是后缀匹配中，即使是在book_intro字段建立了索引，这个执行时间也很可怕。是用户难以忍受的。

![截屏2021-01-11 10.42.41](https://tva1.sinaimg.cn/large/008eGmZEgy1gmjk5bsem5j315k072jv4.jpg)

## 分页查询

### 基本分页查询

一般性分页 使用 limit [offset,] rows 偏移量的问题在于如下两种：
如果偏移量固定，返回记录量对执行时间有什么影响？如分别比较
`select * from user limit 10000,1`;`
select * from user limit 10000,10;`
`select * from user limit 10000,100;`
`select * from user limit 10000,1000`;
`select * from user limit 10000,10000;`

这种分页查询机制，每次都会从数据库第一条记录开始扫描，越往后查询越慢，而 且查询的数据越多，也会拖慢总查询速度

### 引入search-id的分页查询优化与直接使用GIN INDEX+LIMIT的分页查询优化

利用覆盖索引优化
select * from user limit 10000,100;
select id from user limit 10000,100;

利用子查询优化
select * from user limit 10000,100;
select * from user where id>= (select id from user limit 10000,1) limit 100;(使用了索引id做主键比较(id>=)，并且子查询使用了覆盖索引进行优化。)

通过这种思路，可以引入search_id进行分页查询的优化

### 最终分页查询功能的实现

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

![截屏2021-01-10 21.22.48](/Users/chixinning/Library/Application Support/typora-user-images/截屏2021-01-10 21.22.48.png)

使用GIN-index,限制是285条(使用search_id 的主键B树索引的285条数据)

![截屏2021-01-10 21.21.20](https://tva1.sinaimg.cn/large/008eGmZEly1gmiwzj9777j31cq062wgq.jpg)![截屏2021-01-10 21.23.17](https://tva1.sinaimg.cn/large/008eGmZEly1gmix1llovxj31cq0dy10k.jpg)

## 后端代码实现

逻辑上来讲，任何一家书店拥有的书的数量，跟整个图书商城，比如当当，淘宝整个全站搜索库里的书的数量相比是很少的，所以，seachDB的四张表中的都是针对全部book库中的数据，对于每一个店家，没有额外进行建表的必要。

所以，在`SQL`查询语句确定了以后，后端实现的逻辑如下：

1. 首先获得book_db库中符合全局搜索的`book_id`
2. 对于全局搜索直接返回
3. 对于本店搜索，则使用子查询，搜索本店和全局检索出的`book_id`重复的部分。

为了节省篇幅，在此即不附后端实现的代码了，具体可以见`be/model1/buyer.py`下面的`search_functions_limit`函数。

## 总结与提升

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



