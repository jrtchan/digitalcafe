import pymongo

myclient = pymongo.MongoClient("mongodb+srv://jrtchan18:smurfsaur@cluster0.dfmc3x7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

products_db = myclient["products"]
order_management_db = myclient["order_management"]

def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code},{"_id":0})

    return product


def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list


def get_branch(code):
    branches_coll = products_db["branches"]

    branch = branches_coll.find_one({"code":code})
    return branch

def get_branches():
    branch_list = []
    branches_coll = products_db["branches"]

    for p in branches_coll.find({}):
        branch_list.append(p)

    return branch_list

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert_one(order)

def get_past_orders(username):
    orders_coll = order_management_db["orders"]
    # Query MongoDB to retrieve past orders for the given username
    past_orders = orders_coll.find({"username": username})
    # Convert MongoDB cursor to a list of dictionaries
    past_orders_list = list(past_orders)
    return past_orders_list

def update_password(username, new_password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({"username": username}, {"$set": {"password": new_password}})

