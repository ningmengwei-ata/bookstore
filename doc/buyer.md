## 买家下单

#### URL：
POST http://[address]/buyer/new_order

#### Request

##### Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

##### Body:
```json
{
  "user_id": "buyer_id",
  "store_id": "store_id",
  "books": [
    {
      "id": "1000067",
      "count": 1
    },
    {
      "id": "1000134",
      "count": 4
    }
  ]
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
store_id | string | 商铺ID | N
books | class | 书籍购买列表 | N

books数组：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍的ID | N
count | string | 购买数量 | N


#### Response

Status Code:

码 | 描述
--- | ---
200 | 下单成功
5XX | 买家用户ID不存在
5XX | 商铺ID不存在
5XX | 购买的图书不存在
5XX | 商品库存不足

##### Body:
```json
{
  "order_id": "uuid"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
order_id | string | 订单号，只有返回200时才有效 | N


## 买家付款

#### URL：
POST http://[address]/buyer/payment

#### Request

##### Body:
```json
{
  "user_id": "buyer_id",
  "order_id": "order_id",
  "password": "password"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 买家用户密码 | N 


#### Response

Status Code:

码 | 描述
--- | ---
200 | 付款成功
5XX | 账户余额不足
5XX | 无效参数
401 | 授权失败 


## 买家充值

#### URL：
POST http://[address]/buyer/add_funds

#### Request



##### Body:
```json
{
  "user_id": "user_id",
  "password": "password",
  "add_value": 10
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
password | string | 用户密码 | N
add_value | int | 充值金额，以分为单位 | N


Status Code:

码 | 描述
--- | ---
200 | 充值成功
401 | 授权失败
5XX | 无效参数

# 买家发货

#### URL

POST http://[address]/buyer/receive_book

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$buyer id$",
  "order_id": "$order id$"
}
```

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 买家用户ID | N          |
| order_id | string | 订单ID     | N          |

#### Response

Status Code:

| 码   | 描述     |
| ---- | :------- |
| 200  | 发货成功 |
| 401  | 授权失败 |
| 5XX  | 无效参数 |

# 买家查询历史订单

#### URL：

POST http://[address]/buyer/search_history_status

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

##### Body:

```json
{
  "buyer_id": "user_id",
  "flag":flag
}
```

##### 属性说明：

| key      | 类型   | 描述         | 是否可为空 |
| -------- | ------ | ------------ | ---------- |
| buyer_id | string | 买家用户ID   | N          |
| flag     | int    | 买家查询状态 | N          |

flag:0 搜索全部订单

flag:1 搜索未付款订单

flag:2 搜索已付款待发货订单

flag:3 搜索已发货待收货订单

flag:4 搜索已收货订单

Status Code:

| 码   | 描述       |
| ---- | ---------- |
| 200  | 搜索成功   |
| 511  | 无效用户id |

如搜索

```
{
    "buyer_id":"lalala@ecnu.com",
    "flag":1
    
}
```

##### 搜索返回格式：

```json
{
    "history record": [
        {
            "book_list": [
                {
                    "book_id": 1,
                    "count": 2,
                    "price": 2000
                }
            ],
            "buyer_id": "lalala@ecnu.com",
            "commit_time": "Sat, 09 Jan 2021 13:56:31 GMT",
            "order_id": "order1",
            "status": "未付款",
            "store_id": "Lemon"
        }
    ],
    "message": "ok"
}
```

# 手动取消订单

#### URL：

POST http://[address]/buyer/cancel

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

##### Body:

```json
{
  "buyer_id": "$user_id$",
  "order_id": "$order id$"
  
}
```

##### 属性说明：

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| buyer_id | string | 买家用户ID | N          |
| order_id | string | 订单ID     | N          |

Status Code:

| 码   | 描述         |
| ---- | ------------ |
| 200  | 取消成功     |
| 511  | 无效用户id   |
| 518  | 无法取消订单 |