import pytest
import uuid
# from fe.access.new_buyer import register_new_buyer

from fe.access.seller import Seller
from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.book import Book

from fe import conf
import uuid
import random
import time
from fe.access.new_buyer import register_new_buyer

class TestSearchFunctions:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_search_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        yield
    def test_ok_author(self):
        search_type='global'
        search_input='杨红'
        search_field='search_author'
        store_id='Kadokawa'#需要提前后台注册好
        code=self.buyer.search_functions_limit(store_id,search_type,search_input,search_field)[0]
        print(code)
        assert code ==200
        search_type='instore'
        search_input='杨红'
        search_field='search_author'
        code=self.buyer.search_functions_limit(store_id,search_type,search_input,search_field)[0]
        assert code ==200
    #没有这家店
    def test_non_store_id_err(self):
        search_type='instore'
        store_id='Kad'#需要提前后台注册好
        search_input='咒术回战'
        search_field='search_title'
        code=self.buyer.search_functions_limit(store_id,search_type,search_input,search_field)[0]
        assert code ==599
    # book表就没有该字段：全局搜索
    def test_no_such_book_in_DB_err2(self):
        search_type='global'
        store_id='Kad'#需要提前后台注册好
        search_input='五条悟'
        search_field='search_book_intro'
        code=self.buyer.search_functions_limit(store_id,search_type,search_input,search_field)[0]
        assert code ==599
    # book表有该内容，但我们店没有
    def test_no_such_book_instore_err(self):
        search_type='instore'
        store_id='Kadokawa'#需要提前后台注册好
        search_input='美丽'
        search_field='search_book_intro'
        code=self.buyer.search_functions_limit(store_id,search_type,search_input,search_field)[0]
        assert code ==599

    







