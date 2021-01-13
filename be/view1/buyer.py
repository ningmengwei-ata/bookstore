from flask import Blueprint
from flask import request
from flask import jsonify
from be.model1.buyer import Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code


#收货
@bp_buyer.route("/receive_book", methods=["POST"])
def receive_books():
    user_id: str = request.json.get("user_id") #判断该订单是不是该店家的
    order_id: str = request.json.get("order_id")
    print(user_id,order_id)
    b=Buyer()
    code, message = b.receive_book(user_id,order_id)

    return jsonify({"message":message}),code


@bp_buyer.route("/search_book_author", methods=["POST"])
def search_book_author_like():
    store_id=request.json.get("store_id")
    search_type=request.json.get("search_type")
    search_input=request.json.get("search_input")
    b = Buyer()
    code, message = b.search_book_author_like(store_id,search_type,search_input)
    return jsonify({"message": message,"code":code}),code 

@bp_buyer.route("/search_functions", methods=["POST"])
def search_functions():
    store_id=request.json.get("store_id")
    search_type=request.json.get("search_type")
    search_input=request.json.get("search_input")
    field=request.json.get("field")
    b = Buyer()
    code, message = b.search_functions(store_id,search_type,search_input,field)
    return jsonify({"message": message,"code":code}),code 
    
@bp_buyer.route("/search_functions_limit", methods=["POST"])
def search_functions_limit():
    store_id=request.json.get("store_id")
    search_type=request.json.get("search_type")
    search_input=request.json.get("search_input")
    field=request.json.get("field")
    b = Buyer()
    code, message = b.search_functions_limit(store_id,search_type,search_input,field)
    return jsonify({"message": message,"code":code}),code 
@bp_buyer.route("/search_history_status", methods=["POST"])
def search_history_status():
    user_id: str = request.json.get("buyer_id")
    flag:int=request.json.get("flag")
    b = Buyer()
    
    code, message,ret = b.search_history_status(user_id,flag)
    return jsonify({"message": message,"history record": ret}), code

@bp_buyer.route("/cancel", methods=["POST"])
def cancel():
    user_id: str = request.json.get("buyer_id")
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.cancel(user_id,order_id)
    return jsonify({"message": message}), code

@bp_buyer.route("/test_auto_cancel", methods=["POST"])
def test_auto_cancel():
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.test_auto_cancel(order_id)
    return jsonify({"message": message}), code