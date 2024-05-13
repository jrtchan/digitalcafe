from flask import Flask,redirect
from flask import render_template
from flask import request
import database as db
import authentication
import logging
from flask import session
import ordermanagement as om
from database import get_past_orders
from bson.json_util import loads, dumps
from flask import make_response

app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)


    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a 
    # quantity of 1 for now

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods=['POST'])
def update_cart():
    if 'cart' not in session or not session['cart']:
        return redirect('/cart')  
    cart = session['cart']
    total_price = 0 
    for code, item in cart.items():
        qty_key = 'qty_' + str(code)
        if qty_key in request.form:
            new_qty = int(request.form[qty_key])
            if new_qty >= 1:
                item['qty'] = new_qty
                product = db.get_product(int(code))
                item['subtotal'] = product['price'] * new_qty  
                total_price += item['subtotal']  
    session['cart'] = cart  
    session['total_price'] = total_price  
    return redirect('/cart')  

@app.route('/removefromcart', methods=['GET', 'POST'])
def remove_from_cart():
    if 'cart' not in session or not session['cart']:
        return redirect('/cart')
    cart = session['cart']
    code_to_remove = request.args.get('code')
    if code_to_remove in cart:
        del cart[code_to_remove]
    session['cart'] = cart
    if not cart:
        session.pop('cart', None)
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/pastorders')
def past_orders():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect('/login')

    # Retrieve the username of the logged-in user
    username = session['user']['username']

    # Retrieve past orders for the logged-in user from the database
    orders = get_past_orders(username)

    # Render the past orders template with the retrieved orders
    return render_template('pastorders.html', page="Past Orders", orders=orders)

@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if 'user' not in session:
        return redirect('/login')

    error = None

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            error = "All fields are required."
        elif new_password != confirm_password:
            error = "New password and confirm password do not match."
        else:
            # Get the logged-in user's username
            username = session['user']['username']

            # Check if the old password matches
            is_valid_login, _ = authentication.login(username, old_password)
            if not is_valid_login:
                error = "Old password is incorrect."
            else:
                # Update the password in MongoDB
                db.update_password(username, new_password)
                return redirect('/passwordchanged')

    return render_template('changepassword.html', error=error)


@app.route('/passwordchanged')
def passwordchanged():
    return render_template('passwordchanged.html')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp
