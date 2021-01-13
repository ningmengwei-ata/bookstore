import time
import uuid
import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book

class Test_cancel:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.store_id = "test_cancel_store_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_cancel_seller_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel__buyer_{}".format(str(uuid.uuid1()))

        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller=gen_book.seller
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        self.password = self.buyer_id
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num
        code = self.buyer.add_funds(self.total_price+100000)
        assert code == 200

        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_ok_paid(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel(self.buyer_id,self.order_id)
        assert code == 200

    def test_false_buyer(self):
        code = self.buyer.cancel(self.buyer_id+'s',self.order_id)
        assert code != 200

    def test_ok_unpay(self):
        code = self.buyer.cancel(self.buyer_id, self.order_id)
        assert code == 200

    def test_cannot_cancel_order(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.deliver_book(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.cancel(self.buyer_id, self.order_id)
        assert code != 200