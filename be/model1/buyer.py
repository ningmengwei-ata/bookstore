import sqlite3 as sqlite
import uuid
import json
import logging
import sys
sys.path.append("../")
from be.model1 import db_conn
from be.model1 import error
from datetime import datetime
import time
from init_db.init_database import Store,Users,User_store
from init_db.init_database import New_order_detail,New_order_undelivered
from init_db.init_database import New_order_unpaid,New_order_unreceived,New_order_canceled
#======如果不运行自动取消订单，请注释掉以下部分
import redis #为了实现自动删除超时订单
#连接redis数据库
r=redis.StrictRedis(host='localhost',port=6379,db=0,decode_responses=True)
#===================
class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
   #def new_order(self, user_id, store_id, id_and_count):
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            #uid 由'user_id'\_'store_id'_一个唯一标识符组成
            #下单成功后将uid赋值给order_id
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                # print(id_and_count)
                # print(book_id)
                # print(type(book_id))
                # print(count)
                # print(type(count))
                # # cursor = self.conn.execute(
                # #     "SELECT book_id, stock_level, book_info FROM store "
                # #     "WHERE store_id = ? AND book_id = ?;",
                # #     (store_id, book_id)

                # #不加这个转换 后面用%d select时会报错
                book_id=int(book_id)
                # print(type(book_id))
                #book = self.session.execute("SELECT  stock_level,price FROM store WHERE store_id = '%s'AND book_id = %d"%(store_id, book_id)).fetchone()
                book=self.session.query(Store).filter_by(book_id=book_id, store_id=store_id).first()
                #row = cursor.fetchone()
                if book is None:
                    return error.error_non_exist_book_id(str(book_id)) + (order_id, )

                # stock_level = book[0]
                # #print("stock_level:",stock_level)
                # price=book[1]
                stock_level = book.stock_level
                price=book.price
                # book_info = book[2]
                # book_info_json = json.loads(book_info)
                # price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(str(book_id)) + (order_id,)
                # 减库存，如果取消订单的话要加回来
                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count))
                cursor = self.session.query(Store).filter(Store.book_id==book_id, Store.store_id==store_id, Store.stock_level >= count)
                rowcount = cursor.update({Store.stock_level: Store.stock_level - count})
                # res = self.session.execute(
                #     "UPDATE store set stock_level = stock_level - %d WHERE store_id = '%s' and book_id = %d  and stock_level >=%d" % (
                #         count, store_id, book_id, count))
                #cursor=self.session.execute()
                #if res.rowcount == 0:
                if rowcount==0:
                    return error.error_stock_level_low(str(book_id)) + (order_id, )

                # self.conn.execute(
                #         "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #         "VALUES(?, ?, ?, ?);",
                #         (uid, book_id, count, price))
                # self.session.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) VALUES('%s',%d, %d, %d);" % (
                #         uid, book_id, count, price))
                new_order_info = New_order_detail(order_id=uid, book_id=book_id,buyer_id=user_id ,store_id=store_id, count=count, price=price)
                self.session.add(new_order_info)
            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id))
            #记录下单时间
            timenow =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #将新订单加入待付款
            # self.session.execute(
            #         "INSERT INTO new_order_unpaid(order_id, store_id, buyer_id,price,commit_time) VALUES('%s','%s','%s',%d,'%s');" % (
            #             uid, store_id, user_id,price,timenow))
            new_order_unpaid = New_order_unpaid(order_id=uid, store_id=store_id,buyer_id=user_id,price=price,commit_time=timenow)
            self.session.add(new_order_unpaid)
            self.session.commit()
            self.session.close()
            print("order_id",uid)
            #===============注释掉
            r.setex(uid,15,'order') #先设置30s，测试好之后再改成其他时间
            #===============
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        #conn = self.conn
        try:
            # cursor = conn.execute("SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?", (order_id,))
            # row = cursor.fetchone()
            #待支付中是否有该用户该订单
            # row = self.session.execute(
            # "SELECT buyer_id,price,store_id FROM new_order_unpaid WHERE order_id = '%s'" % (order_id)).fetchone()
            row=self.session.query(New_order_unpaid).filter_by(order_id=order_id).first()
            print(row)
            if row is None:
                return error.error_invalid_order_id(order_id)

            
            # buyer_id = row[0]
            # price=row[1]
            # store_id = row[2]
            buyer_id=row.buyer_id
            price=row.price
            store_id=row.store_id

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # cursor = conn.execute("SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,))
            # row = cursor.fetchone()
            # 检查密码 余额
            # row = self.session.execute(
            # "SELECT balance, password FROM usr WHERE user_id = '%s';" % (buyer_id)).fetchone()
            row=self.session.query(Users).filter_by(user_id=buyer_id).first()
            
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            check_password=row.password
            balance=row.balance
            #balance = row[0]
            #if password != row[1]:
            if password !=check_password:
                return error.error_authorization_fail()
            #记录卖家id
            # cursor = self.session.execute("SELECT store_id, user_id FROM user_store WHERE store_id = '%s';"%(store_id))
            # row = cursor.fetchone()
            row=self.session.query(User_store).filter_by(store_id=store_id).first()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            #seller_id = row[1]
            seller_id=row.user_id

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            #cursor = self.session.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = '%s';"%(order_id))
            cursor = self.session.query(New_order_detail).filter_by(order_id=order_id)
            total_price = 0
            for row in cursor.all():
                count = row.count
                price = row.price
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            #买家支付 余额扣钱
            #cursor = self.session.execute("UPDATE usr set balance = balance - %d WHERE user_id = '%s' AND balance >= %d"%(total_price, buyer_id, total_price))
            cursor = self.session.query(Users).filter(Users.user_id==buyer_id, Users.balance>=total_price)
            rowcount = cursor.update({Users.balance: Users.balance - total_price})
            if rowcount == 0:
                return error.error_not_sufficient_funds(order_id)
            #卖家加钱
            #cursor = self.session.execute("UPDATE usr set balance = balance + %d WHERE user_id = '%s'"%(total_price, seller_id))
            cursor = self.session.query(Users).filter(Users.user_id==seller_id)
            rowcount = cursor.update({Users.balance: Users.balance + total_price})
            if rowcount == 0:
                return error.error_non_exist_user_id(seller_id)
            # 删除待付订单
            #cursor = self.session.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s';"% (order_id ))
            
            query = self.session.query(New_order_unpaid).filter(New_order_unpaid.order_id == order_id)
            query.delete()
            print("*****")
            rowcount=query.first()
            #print(cursor.rowcount)
            #if cursor.rowcount == 0:
            if rowcount==0:
                return error.error_invalid_order_id(order_id)
            #删除订单的详细信息
            #还未发货暂不删除订单详细信息
            # cursor = self.session.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            
            #在待发货中加入该订单
            timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("******")
            new_orde = New_order_undelivered(
                order_id=order_id,
                buyer_id = buyer_id ,
                store_id=store_id,
                price=price,
                purchase_time=timenow
            )
            self.session.add(new_orde)
            # re=self.session.execute(
            # "INSERT INTO new_order_undelivered(order_id, buyer_id,store_id,price,purchase_time) VALUES('%s', '%s','%s',%d,'%s');" % (
            #     order_id, buyer_id, store_id, price,timenow))
            # print(re.rowcount)
            #self.session.commit()
            self.session.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
#买家充值
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            usr = self.session.query(Users).filter_by(user_id=user_id).first()
            #usr = self.session.execute("SELECT password  from usr where user_id= '%s'"%(user_id,)).fetchone()
            #row = cursor.fetchone()
            if usr is None:
                return error.error_authorization_fail()

            if usr.password != password:
                return error.error_authorization_fail()
            cursor = self.session.query(Users).filter(Users.user_id==user_id)
            rowcount = cursor.update({Users.balance: Users.balance + add_value})
            # cursor = self.session.execute(
            #     "UPDATE usr SET balance = balance + %d WHERE user_id = '%s'"%
            #     (add_value, user_id))
            
            #if cursor.rowcount == 0:
            if rowcount==0:
                return error.error_non_exist_user_id(user_id)

            self.session.commit()
            self.session.close()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"


    def receive_book(self,user_id:str,order_id:str):
        try:
            #判断该用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            print("用户存在")
            #判断该订单是否存在在未收货里面
            row=self.session.query(New_order_unreceived).filter_by(order_id=order_id)
            order=row.first()
            print("未收货订单",order)
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id=order.buyer_id
            #判断该用户是否有这个订单。。。。验证收货的人是否正确
            if user_id != buyer_id:
                return error.error_authorization_fail()

            #有该订单，收货
            #添加收货时间
            timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("******已收货")
            row.update({New_order_unreceived.receive_time:timenow})
            self.session.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


    # 买家查询 
    # 比较索引 和模糊查询的 检索效率
 
    def search_history_status(self,buyer_id:str,flag:int):
        try:
            if not self.user_id_exist(buyer_id):
                #print('********')
                code, mes = error.error_non_exist_user_id(buyer_id)
                return code, mes, " "
        #查所有订单
            if flag==0:
                record_listn=self.session.query(New_order_detail).filter(New_order_detail.buyer_id==buyer_id)
                print(record_listn)
                records=[]
                for record in record_listn:
                
                    records.append({
                    "order_id":record.order_id,
                    "buyer_id": record.buyer_id,
                    "store_id": record.store_id,
                    "book_id": record.book_id,
                    "count":record.count,
                    "price":record.price
                    })
                self.session.close()  
        #未付款
        
            if flag==1:
                record_list1=self.session.query(New_order_unpaid).filter(New_order_unpaid.buyer_id==buyer_id,New_order_unpaid.commit_time!=None)
                print(record_list1)
                records=[]
                for record in record_list1:
                    record_infos = self.session.query(New_order_detail).filter_by(order_id=record.order_id).all()
                    records.append({
                    "order_id":record.order_id,
                    "buyer_id": record.buyer_id,
                    "store_id": record.store_id,
                    "commit_time":record.commit_time,
                    "status":'未付款',
                    "book_list": [
                        {"book_id": rei.book_id, "count": rei.count, "price": rei.price}
                        for rei in record_infos
                    ]
                    })
                self.session.close()                
        #已付款待发货
            if flag==2:
                record_list=self.session.query(New_order_undelivered).filter(New_order_undelivered.buyer_id==buyer_id,New_order_undelivered.purchase_time!=None)
                print(record_list)
                records=[]
                for record in record_list:
                    record_infos = self.session.query(New_order_detail).filter_by(order_id=record.order_id).all()
                    records.append({
                    "order_id":record.order_id,
                    "buyer_id": record.buyer_id,
                    "store_id": record.store_id,
                    "purchase_time":record.purchase_time,
                    "status":'已付款待发货',
                    "book_list": [
                        {"book_id": rei.book_id, "count": rei.count, "price": rei.price}
                        for rei in record_infos
                    ]
                    })
                self.session.close()
        #已发货待收货
            if flag==3:
                record_list2=self.session.query(New_order_unreceived).filter(New_order_unreceived.buyer_id==buyer_id,New_order_unreceived.purchase_time!=None)
                print(record_list2)
                records=[]
                for record in record_list2:
                    record_infos = self.session.query(New_order_detail).filter_by(order_id=record.order_id).all()
                    records.append({
                    "order_id":record.order_id,
                    "buyer_id": record.buyer_id,
                    "store_id": record.store_id,
                    "purchase_time":record.purchase_time,
                    "status":'已发货待收货',
                    "book_list": [
                        {"book_id": rei.book_id, "count": rei.count, "price": rei.price}
                        for rei in record_infos
                    ]
                    })
                self.session.close()
        #已收货
            if flag==4:
                record_list3=self.session.query(New_order_unreceived).filter(New_order_unreceived.buyer_id==buyer_id,New_order_unreceived.receive_time!=None)
                print(record_list3)
                records=[]
                for record in record_list3:
                    record_infos = self.session.query(New_order_detail).filter_by(order_id=record.order_id).all()
                    records.append({
                    "order_id":record.order_id,
                    "buyer_id": record.buyer_id,
                    "store_id": record.store_id,
                    "receive_time":record.receive_time,
                    "status":'已收货',
                    "book_list": [
                        {"book_id": rei.book_id, "count": rei.count, "price": rei.price}
                        for rei in record_infos
                        ]
                    })
                self.session.close()
            if flag==5:
                record_list4=self.session.query(New_order_canceled).filter(New_order_canceled.buyer_id==buyer_id,New_order_canceled.cancel_time!=None)
                print(record_list4)
                records=[]
                for record in record_list4:
                    record_infos = self.session.query(New_order_detail).filter_by(order_id=record.order_id).all()
                    records.append({
                    "order_id":record.order_id,
                    "buyer_id": record.buyer_id,
                    "store_id": record.store_id,
                    "cancel_time":record.cancel_time,
                    "status":'已取消',
                    "book_list": [
                        {"book_id": rei.book_id, "count": rei.count, "price": rei.price}
                        for rei in record_infos
                        ]
                    })
                self.session.close()

        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", records

    def cancel(self,buyer_id:str, order_id:str):
        if not self.user_id_exist(buyer_id):
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes
        #是否属于未付款订单
        store=self.session.query(New_order_unpaid).filter(New_order_unpaid.buyer_id==buyer_id,New_order_unpaid.commit_time!=None).first()
        
        if store is not None:
            store_id=store.store_id
            price=store.price
            
            query = self.session.query(New_order_unpaid).filter(New_order_unpaid.order_id == order_id)
            query.delete()
        else:
            # 是否属于已付款且未发货订单
            order_info=self.session.query(New_order_undelivered).filter(New_order_undelivered.buyer_id==buyer_id,New_order_undelivered.order_id==order_id,New_order_undelivered.purchase_time!=None).first()
           
            if order_info is not None:
                store_id=order_info.store_id
                price=order_info.price
                
                #删除订单
                query = self.session.query(New_order_undelivered).filter(New_order_undelivered.order_id == order_id,New_order_undelivered.purchase_time!=None)
                query.delete()
                
                # 卖家减钱
                #查询卖家
                user_id=self.session.query(User_store).filter(User_store.store_id==store_id).first()
                
                cursor = self.session.query(Users).filter_by(user_id=user_id.user_id)
                rowcount = cursor.update({Users.balance: Users.balance-price})
               
                #买家加钱
                cursor = self.session.query(Users).filter_by(user_id=buyer_id)
                rowcount = cursor.update({Users.balance: Users.balance+price})
                
            else:
                #已发货 无法取消 需要申请售后
                #无法取消
                return error.error_invalid_order_id(order_id)
        #加入new_order_cancel中
        timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cancel_order = New_order_canceled(order_id=order_id, buyer_id=buyer_id ,store_id=store_id,  price=price,cancel_time=timenow)
        self.session.add(cancel_order)
        self.session.commit()
        #加库存
        store=self.session.query(Store).filter_by(store_id=store_id)
        stores=store.first()
        cursor = self.session.query(New_order_detail).filter(New_order_detail.order_id==order_id,New_order_detail.book_id==stores.book_id).first()
        
        count=cursor.count
        # cursor = self.session.query(Store).filter(Store.book_id==book_id, Store.store_id==store_id, Store.stock_level >= count)
        # rowcount = cursor.update({Store.stock_level: Store.stock_level - count})
        store.update({Store.stock_level: Store.stock_level + count})
        # rowcount = self.session.query(Store).update({Store.stock_level: Store.stock_level+count})
        
        self.session.commit()
        self.session.close()
        return 200, 'ok'
    
    def test_auto_cancel(self,order_id:str):
        unpaid=self.session.query(New_order_unpaid).filter(New_order_unpaid.order_id==order_id).first()
        canceled=self.session.query(New_order_canceled).filter(New_order_canceled.order_id==order_id).first()
        if unpaid !=None and canceled ==None:
            return 600,'未删除失效订单'
        elif unpaid == None and canceled != None:
            return 200,'ok'
        elif unpaid == None and canceled ==None:
            return 518,'订单失踪'
        else:
            return 518,'订单冲突'

    # EXPLAIN ANALYZE SELECT DISTINCT book_id FROM search_book_intro  WHERE tsv_column @@ '美丽' LIMIT 100
    def search_functions_limit(self,store_id:str,search_type:str,search_input:str,field:str)->(int, [dict]):
        time1=time.time()
        res=[]
        resglobal=[]
        # 下面这种模糊查询的方式是不好用的
        # EXPLAIN ANALYZE SELECT DISTINCT book_id FROM search_book_intro  WHERE tsv_column @@ '美丽' LIMIT 100
        # 首先利用索引搜索全局
        rows=self.session.execute("SELECT DISTINCT book_id FROM %s WHERE tsv_column @@ '%s' LIMIT 100"%(field,search_input)).fetchall()
        if len(rows)!=0:
            for row in rows:
                restmp={}
                book_global_id=row[0]#?
                ans=self.session.execute("SELECT author,title,book_intro,original_price,tags from book where book_id ='%s' " % (book_global_id)).fetchone()
                restmp['book_id']=book_global_id
                restmp['author']=ans[0]
                restmp['title']=ans[1]
                restmp['book_intro']=ans[2]
                restmp['price']=ans[3]
                restmp['tags']=ans[4]
                resglobal.append(restmp) 
        else:
            restmp={}
            restmp['error_code[597]']="书库里找不到这个结果"
            res.append(restmp)
            return 599,res
        if search_type=='global':
            #需要加图再加图
            time2=time.time()
            timetmp={}
            timetmp['time complexity res']=time2-time1
            resglobal.insert(0,timetmp)   
            return 200,resglobal
        else : # 待DEBUG(应该是好的)
            # 首先获取该店的图书信息
            # 先要加store id不对的边缘检测?
            res=[]
            rows_likely_in_store=self.session.execute(
                "SELECT DISTINCT book_id,title,author,book_intro,tags from book where book.book_id in (SELECT DISTINCT book_id FROM %s WHERE tsv_column @@ '%s' LIMIT 100);"% (field,search_input)
                ).fetchall()
            
            for row in rows_likely_in_store:
                book_instore_id=row[0]#先获取book_id，毕竟一个书店有的书和全局有的书数据量相比还是小的
                restmp={}
                ans=self.session.execute("SELECT stock_level,price FROM store where store_id = '%s' and book_id = '%s'"%(store_id,book_instore_id)).fetchone()
                if ans ==None:
                    continue
                else:
                    stock=ans[0]
                    current_price=[1]
                    restmp['book_id']=row[0]
                    restmp['author']=row[2]
                    restmp['title']=row[1]
                    restmp['book_intro']=row[3]
                    restmp['book_tags']=row[4]
                    restmp['current_price']=current_price
                    restmp['stock_level']=stock
                    restmp['store_id']=store_id
                    res.append(restmp)
                #根据book_id和字典确定author的搜索结果。
            time2=time.time()
            timetmp={}
            timetmp['time complexity res']=time2-time1
            res.insert(0,timetmp)
            if(len(res)==1):
                restmp={}
                restmp['error_code[598]']="本店一本也没有！"
                res.append(restmp)
                return 599,res
            return 200,res