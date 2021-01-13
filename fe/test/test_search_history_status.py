import pytest

import time
import uuid
import pytest
import random
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book

class Test_search_history_status:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_search_order__buyer_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b


        yield
    # @pytest.mark.run(order=5)
    def test_ok(self):
        buy_time = random.randint(4, 10)#买buy_time次书，产生buytime个记录
        for i in range(buy_time):
            self.seller_id = "test_search_history_status_seller_{}".format(str(uuid.uuid1()))
            self.store_id = "test_search_history_status_id_{}".format(str(uuid.uuid1()))
            self.gen_book = GenBook(self.seller_id, self.store_id)
            self.seller = self.gen_book.seller
            ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
            self.buy_book_info_list = self.gen_book.buy_book_info_list
            assert ok

            self.total_price = 0
            for item in self.buy_book_info_list:
                book: Book = item[0]
                num = item[1]
                self.total_price = self.total_price + book.price * num
            code = self.buyer.add_funds(self.total_price + 100000)
            assert code == 200
            code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200
            flag = random.randint(0, 2)
            if flag != 0:
                code = self.buyer.payment(self.order_id)
                assert code == 200
                if flag == 1:
                    code = self.seller.deliver_book(self.seller_id, self.order_id)
                    assert code == 200
                    code = self.buyer.receive_book(self.buyer_id, self.order_id)
                    assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,0)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,1)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,2)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,3)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,4)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,5)
        assert code == 200

    def test_false_buyer(self):
        code = self.buyer.search_history_status(self.buyer_id+'s',0)
        assert code != 200
        code = self.buyer.search_history_status(self.buyer_id+'s',1)
        assert code != 200
        code = self.buyer.search_history_status(self.buyer_id+'s',2)
        assert code != 200
        code = self.buyer.search_history_status(self.buyer_id+'s',3)
        assert code != 200
        code = self.buyer.search_history_status(self.buyer_id+'s',4)
        assert code != 200
        code = self.buyer.search_history_status(self.buyer_id+'s',5)
        assert code != 200

    def test_no_record_buyer(self):
        code = self.buyer.search_history_status(self.buyer_id,0)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,1)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,2)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,3)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,4)
        assert code == 200
        code = self.buyer.search_history_status(self.buyer_id,5)
        assert code == 200
