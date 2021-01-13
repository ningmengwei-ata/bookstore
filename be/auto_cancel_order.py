#为了自动取消添加的模块
import sys
# sys.path.append("d:\这学期\数据管理系统\大作业\项目\DB")
# sys.path.append("d:\这学期\数据管理系统\大作业\项目\DB\model1")
sys.path.append("../")
sys.path.append("../../")
import time
from datetime import datetime

import redis #为了实现自动删除超时订单
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint,and_
from sqlalchemy.orm import sessionmaker
from init_db.init_database import Store,Users,User_store
from init_db.init_database import New_order_detail,New_order_undelivered
from init_db.init_database import New_order_unpaid,New_order_unreceived,New_order_canceled

#连接postgres数据库
engine = create_engine('postgresql://postgres:123456@localhost:5432/bookstore')
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()

#连接redis数据库
r=redis.StrictRedis(host='localhost',port=6379,db=0,decode_responses=True)
# 创建pubsub对象，该对象订阅一个频道并侦听新消息：
pubsub=r.pubsub()

def event_hander(msg):
    # print('Handler',msg)
    order_id=str(msg['data'])
    print(order_id)
    #获取订单
    #从数据库中new_order_unpaid中找这个订单
    order=session.query(New_order_unpaid).filter(New_order_unpaid.order_id==order_id)
    #如果未找到，说明已付款，什么都不用做
    order_row=order.first()
    print(order_row)
    if order_row is None:
        return 200,"ok"

    buyer_id=order_row.buyer_id
    store_id=order_row.store_id
    price=order_row.price
    #如果能找到，就删除未支付订单
    order.delete()
    print("订单已删除")
    #添加到已删除订单中 加入new_order_cancel中
    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cancel_order = New_order_canceled(order_id=order_id, buyer_id=buyer_id ,store_id=store_id,  price=price,cancel_time=timenow)
    session.add(cancel_order)
    print("订单已添加")
    #将商店中的书籍书加回去
    detail_orders=session.query(New_order_detail).filter(New_order_detail.order_id==order_id)
    # 遍历商品
    for detail_order in detail_orders:
        # 获取订单中的商品数量
        count=detail_order.count
        book_id=detail_order.book_id
        print("count",count)
        # 添加回商店
        # 得到商店原本的数量
        cursor = session.query(Store).filter(and_(Store.book_id==book_id, Store.store_id==store_id))
        old_count = cursor.first().stock_level
        rowcount = cursor.update({Store.stock_level: old_count + count})
    print("订单已更新")
    #所有事物处理完后commit
    session.commit()
    session.close()
    return 200, "ok"

pubsub.psubscribe(**{'__keyevent@0__:expired':event_hander})
while True:
    # print("监控超时订单")
    #获得事件信息，有结果就会回调函数
    message=pubsub.get_message()
    time.sleep(0.1)