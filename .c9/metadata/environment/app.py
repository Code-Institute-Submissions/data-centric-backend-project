{"changed":true,"filter":false,"title":"app.py","tooltip":"/app.py","value":"#Imports\nimport os\nimport math\nfrom flask import Flask, render_template, redirect, request, url_for, session, jsonify\nfrom flask_pymongo import PyMongo, pymongo\nfrom bson.objectid import ObjectId \nimport datetime\n\n\napp = Flask(__name__, static_url_path='/static')\n\n\n#App configuration -- table name and the link\napp.secret_key = 'any random string'\napp.config['MONG_DBNAME'] = 'DB_ecommerce_project'\napp.config['MONGO_URI'] = 'mongodb+srv://elias:kb01210012@myfirstcluster-uyvei.mongodb.net/DB_ecommerce_project?retryWrites=true'\n                            \n\nmongo = PyMongo(app)\n\n\n\n@app.route('/')\ndef index():\n    if 'username' in session:\n        return 'You are logged in as ' + session['username']\n    return render_template('index.html',\n    aside_products=mongo.db.products.find(),\n    electronics=mongo.db.products.find({'category_name':\"Electronics\"}),\n    homeGarden=mongo.db.products.find({'category_name':\"Home & Garden\"}),\n    motors=mongo.db.products.find({'category_name':\"Motors\"}))\n    \n#LOGIN FUNCTION   \n@app.route('/login', methods=['POST', 'GET'])\ndef login():\n    if request.method == 'GET': \n        return render_template('login.html')\n    else:\n        user = mongo.db.user\n        login_user = user.find_one({\n        'email': request.form.get('email'), \n        'password':request.form.get('password'\n        )})\n        \n        if login_user:\n            session['email'] = login_user['email']\n            session['name'] = login_user['name']\n            return redirect(url_for('user'))\n       \n        return 'Invalid username or password combination'\n        \n#LOGOUT FUNCTION\n@app.route('/logout')\ndef logout():\n    session['email'] = None\n    session['name'] = None\n    return redirect(url_for('login'))\n\n#REGISTER FUNCTION\n@app.route('/register', methods=['POST', 'GET'])\ndef register():\n    email = session.get('email')\n    if email:\n      return redirect(url_for('index'))\n\n    user = None\n    if request.method == 'POST':\n        name = request.form['username']\n        email = request.form['email']\n        password = request.form['password']\n        user = {'name': name, 'email': email, 'password': password}\n\n        if mongo.db.user.find_one({\"email\": email}):\n            return render_template('register.html',  error=\"user_exists\")\n        else:\n            mongo.db.user.insert_one(user)\n            return render_template('login.html', user=user, password=password)\n\n    return render_template('register.html')\n    \n#category 1 Eletronics\n@app.route('/electronics/')\n@app.route('/electronics/<page>/<limit>')\ndef electronics(page=1, limit=6):\n    page=int(page)\n    limit=int(limit)\n    skip = page * limit - limit\n    maximum = math.floor( (mongo.db.products.count_documents({})) / limit - 1)\n    electronics = list(mongo.db.products.find({'category_name':\"Electronics\"}).sort(\"$natural\", pymongo.DESCENDING).skip(skip).limit( limit ))\n    return render_template(\n        'electronics.html', \n        electronics=electronics,\n        page=page,\n        pages=range(1, maximum + 1),\n        maximum=maximum, \n        limit=limit\n    )\n\n#category 2  Home & Garden\n@app.route('/home_gardens/')\n@app.route('/home_gardens/<page>/<limit>')\ndef home_garden(page=1, limit=6):\n    limit = int(limit)\n    page = int(page)\n    skip = page * limit - limit\n    maximum = math.floor( (mongo.db.products.count_documents({})) / limit - 1)\n    homeGarden = list(mongo.db.products.find({'category_name':\"Home & Garden\"}).sort(\"$natural\", pymongo.DESCENDING).skip(skip).limit( limit ))\n    return render_template(\n        'home_garden.html',\n        homeGarden=homeGarden,\n        page=page,\n        pages=range(1, maximum + 1),\n        maximum=maximum, limit=limit)\n\n#category 3 Motors\n@app.route('/motors/')\n@app.route('/motors/<page>/<limit>')\ndef motors(page=1, limit=6):\n    limit = int(limit)\n    page = int(page)\n    skip = page * limit - limit\n    maximum = math.floor( (mongo.db.products.count_documents({})) / limit -1)\n    motors = list(mongo.db.products.find({'category_name':\"Motors\"}).sort(\"$natural\", pymongo.DESCENDING).skip(skip).limit( limit ))\n    return render_template(\n        'motors.html',\n        motors=motors,\n        page=page,\n        pages=range(1, maximum + 1),\n        maximum=maximum, limit=limit\n    )\n    \n@app.route('/view/product_id?=<id>')\ndef view(id):\n    mongo.db.products.find_one_and_update({\"_id\": ObjectId(id)}, {\"$push\": {\"views\": 1}})\n    return render_template('product.html')\n    \n    \n#REVIEW FUNCTION\n@app.route('/review/product_id?=<id>', methods=['POST', 'GET'])\ndef review(id):\n    now = datetime.datetime.now()\n    #have to fix no-logged user error\n    name=session['name']\n    print_post=request.form.get('review')\n    #Gets the product clicked on its link and display on the product.html page\n    reviews = mongo.db.products.find_one({\"_id\": ObjectId(id)})\n    if request.method == 'POST':\n        mongo.db.products.find_one_and_update({\"_id\": ObjectId(id)},{\n                    '$push':{'review':{\n                    'name': name,\n                    'post': print_post,\n                    'date': now.strftime(\"%d/%m/%Y\")\n                    }\n                }\n            }\n        )\n        #try to redirect to product.html\n        return redirect(url_for('review', id=id))\n    #Increments +1 view into the visited product by its id.\n    mongo.db.products.find_one_and_update({\"_id\": ObjectId(id)}, {\"$inc\": {\"views\": 1}})\n    return render_template('product.html', reviews=reviews)\n    \n@app.route('/delete_comment/product_id?=<id>/post_content?=<post_content>')\ndef delete_comment(id, post_content):\n    print('post_content',post_content)\n    mongo.db.products.update({\"_id\": ObjectId(id)},{\n        '$pull':{'review':{\n            'post':post_content\n            }\n        }\n    })\n    return redirect(url_for('review', id=id))\n\n#FORM TO CREATE NEW PRODUCT                                                   \n@app.route('/user')                                                             \ndef user():\n    items=mongo.db.products.find({'seller':session.get('name')})\n    category=mongo.db.category.find()\n    email = session.get('email')\n    if not email:\n        return redirect(url_for('login'))\n    return render_template('user.html', category=category, items=items)\n\n\n#CREATE FUNCTION\n@app.route('/insert_product', methods=['POST'])\ndef insert_product():\n    products=mongo.db.products\n    products.insert_one(request.form.to_dict())\n    return redirect(url_for('user'))\n    \n    \n#UPDATE FUNCTION\n@app.route('/update_product/<product_id>', methods=['POST'])\ndef update_product(product_id):\n    products = mongo.db.products\n    products.update({'_id': ObjectId(product_id)},\n        {\n        'category_name':request.form.get('category_name'),\n        'product_name':request.form.get('product_name'),\n        'price':request.form.get('price'),\n        'url':request.form.get('url'),\n        'seller':request.form.get('seller'),\n        'product_description': request.form.get('product_description'),\n        })\n    return redirect(url_for('user'), )\n\n    \n@app.route('/edit_product/<product_id>')\ndef edit_product(product_id):\n    the_product = mongo.db.products.find_one({\"_id\": ObjectId(product_id)})\n    all_categories = mongo.db.category.find()\n    return render_template('editproduct.html', product=the_product, categories=all_categories)\n\n    \n#DELETE FUNCTION  \n@app.route('/delete_product/<product_id>')\ndef delete_product(product_id):\n    mongo.db.products.remove({'_id':ObjectId(product_id)})\n    return redirect(url_for('user'))\n    \n\n    \n\nif __name__ == '__main__':\n    app.run(host=os.environ.get('IP'),\n            port=int(os.environ.get('PORT')),\n            debug=True)","undoManager":{"mark":-2,"position":100,"stack":[[{"start":{"row":165,"column":13},"end":{"row":165,"column":14},"action":"insert","lines":["d"],"id":24066},{"start":{"row":165,"column":14},"end":{"row":165,"column":15},"action":"insert","lines":["i"]},{"start":{"row":165,"column":15},"end":{"row":165,"column":16},"action":"insert","lines":["r"]},{"start":{"row":165,"column":16},"end":{"row":165,"column":17},"action":"insert","lines":["e"]}],[{"start":{"row":165,"column":11},"end":{"row":165,"column":17},"action":"remove","lines":["redire"],"id":24067},{"start":{"row":165,"column":11},"end":{"row":165,"column":19},"action":"insert","lines":["redirect"]}],[{"start":{"row":165,"column":19},"end":{"row":165,"column":21},"action":"insert","lines":["()"],"id":24068}],[{"start":{"row":165,"column":20},"end":{"row":165,"column":21},"action":"insert","lines":["u"],"id":24069},{"start":{"row":165,"column":21},"end":{"row":165,"column":22},"action":"insert","lines":["r"]},{"start":{"row":165,"column":22},"end":{"row":165,"column":23},"action":"insert","lines":["l"]}],[{"start":{"row":165,"column":20},"end":{"row":165,"column":23},"action":"remove","lines":["url"],"id":24070},{"start":{"row":165,"column":20},"end":{"row":165,"column":27},"action":"insert","lines":["url_for"]}],[{"start":{"row":165,"column":27},"end":{"row":165,"column":29},"action":"insert","lines":["()"],"id":24071}],[{"start":{"row":165,"column":28},"end":{"row":165,"column":30},"action":"insert","lines":["''"],"id":24072}],[{"start":{"row":165,"column":29},"end":{"row":165,"column":30},"action":"insert","lines":["u"],"id":24073},{"start":{"row":165,"column":30},"end":{"row":165,"column":31},"action":"insert","lines":["s"]},{"start":{"row":165,"column":31},"end":{"row":165,"column":32},"action":"insert","lines":["e"]},{"start":{"row":165,"column":32},"end":{"row":165,"column":33},"action":"insert","lines":["r"]}],[{"start":{"row":164,"column":23},"end":{"row":165,"column":0},"action":"insert","lines":["",""],"id":24074},{"start":{"row":165,"column":0},"end":{"row":165,"column":4},"action":"insert","lines":["    "]}],[{"start":{"row":165,"column":4},"end":{"row":165,"column":5},"action":"insert","lines":["n"],"id":24075},{"start":{"row":165,"column":5},"end":{"row":165,"column":6},"action":"insert","lines":["a"]},{"start":{"row":165,"column":6},"end":{"row":165,"column":7},"action":"insert","lines":["m"]},{"start":{"row":165,"column":7},"end":{"row":165,"column":8},"action":"insert","lines":["e"]}],[{"start":{"row":165,"column":8},"end":{"row":165,"column":9},"action":"insert","lines":[" "],"id":24076},{"start":{"row":165,"column":9},"end":{"row":165,"column":10},"action":"insert","lines":["="]}],[{"start":{"row":165,"column":10},"end":{"row":165,"column":11},"action":"insert","lines":[" "],"id":24077},{"start":{"row":165,"column":11},"end":{"row":165,"column":12},"action":"insert","lines":["s"]},{"start":{"row":165,"column":12},"end":{"row":165,"column":13},"action":"insert","lines":["e"]},{"start":{"row":165,"column":13},"end":{"row":165,"column":14},"action":"insert","lines":["s"]},{"start":{"row":165,"column":14},"end":{"row":165,"column":15},"action":"insert","lines":["s"]},{"start":{"row":165,"column":15},"end":{"row":165,"column":16},"action":"insert","lines":["i"]},{"start":{"row":165,"column":16},"end":{"row":165,"column":17},"action":"insert","lines":["o"]},{"start":{"row":165,"column":17},"end":{"row":165,"column":18},"action":"insert","lines":["n"]}],[{"start":{"row":165,"column":18},"end":{"row":165,"column":20},"action":"insert","lines":["[]"],"id":24078}],[{"start":{"row":165,"column":19},"end":{"row":165,"column":21},"action":"insert","lines":["''"],"id":24079}],[{"start":{"row":165,"column":20},"end":{"row":165,"column":21},"action":"insert","lines":["n"],"id":24080},{"start":{"row":165,"column":21},"end":{"row":165,"column":22},"action":"insert","lines":["a"]},{"start":{"row":165,"column":22},"end":{"row":165,"column":23},"action":"insert","lines":["m"]},{"start":{"row":165,"column":23},"end":{"row":165,"column":24},"action":"insert","lines":["e"]}],[{"start":{"row":165,"column":26},"end":{"row":166,"column":0},"action":"insert","lines":["",""],"id":24081},{"start":{"row":166,"column":0},"end":{"row":166,"column":4},"action":"insert","lines":["    "]}],[{"start":{"row":166,"column":4},"end":{"row":166,"column":5},"action":"insert","lines":["m"],"id":24082},{"start":{"row":166,"column":5},"end":{"row":166,"column":6},"action":"insert","lines":["o"]},{"start":{"row":166,"column":6},"end":{"row":166,"column":7},"action":"insert","lines":["n"]},{"start":{"row":166,"column":7},"end":{"row":166,"column":8},"action":"insert","lines":["g"]},{"start":{"row":166,"column":8},"end":{"row":166,"column":9},"action":"insert","lines":["o"]}],[{"start":{"row":166,"column":9},"end":{"row":166,"column":10},"action":"insert","lines":["."],"id":24083},{"start":{"row":166,"column":10},"end":{"row":166,"column":11},"action":"insert","lines":["d"]},{"start":{"row":166,"column":11},"end":{"row":166,"column":12},"action":"insert","lines":["b"]}],[{"start":{"row":166,"column":12},"end":{"row":166,"column":13},"action":"insert","lines":["."],"id":24084},{"start":{"row":166,"column":13},"end":{"row":166,"column":14},"action":"insert","lines":["p"]},{"start":{"row":166,"column":14},"end":{"row":166,"column":15},"action":"insert","lines":["r"]},{"start":{"row":166,"column":15},"end":{"row":166,"column":16},"action":"insert","lines":["o"]},{"start":{"row":166,"column":16},"end":{"row":166,"column":17},"action":"insert","lines":["d"]},{"start":{"row":166,"column":17},"end":{"row":166,"column":18},"action":"insert","lines":["u"]}],[{"start":{"row":166,"column":18},"end":{"row":166,"column":19},"action":"insert","lines":["c"],"id":24085},{"start":{"row":166,"column":19},"end":{"row":166,"column":20},"action":"insert","lines":["t"]},{"start":{"row":166,"column":20},"end":{"row":166,"column":21},"action":"insert","lines":["s"]}],[{"start":{"row":166,"column":21},"end":{"row":166,"column":22},"action":"insert","lines":["."],"id":24086},{"start":{"row":166,"column":22},"end":{"row":166,"column":23},"action":"insert","lines":["r"]},{"start":{"row":166,"column":23},"end":{"row":166,"column":24},"action":"insert","lines":["e"]},{"start":{"row":166,"column":24},"end":{"row":166,"column":25},"action":"insert","lines":["m"]},{"start":{"row":166,"column":25},"end":{"row":166,"column":26},"action":"insert","lines":["o"]},{"start":{"row":166,"column":26},"end":{"row":166,"column":27},"action":"insert","lines":["v"]},{"start":{"row":166,"column":27},"end":{"row":166,"column":28},"action":"insert","lines":["e"]}],[{"start":{"row":166,"column":28},"end":{"row":166,"column":30},"action":"insert","lines":["()"],"id":24087}],[{"start":{"row":166,"column":29},"end":{"row":166,"column":31},"action":"insert","lines":["{}"],"id":24088}],[{"start":{"row":166,"column":30},"end":{"row":166,"column":50},"action":"insert","lines":["{\"_id\": ObjectId(id)"],"id":24089}],[{"start":{"row":166,"column":30},"end":{"row":166,"column":31},"action":"remove","lines":["{"],"id":24090}],[{"start":{"row":166,"column":50},"end":{"row":166,"column":51},"action":"insert","lines":[","],"id":24091}],[{"start":{"row":166,"column":51},"end":{"row":166,"column":53},"action":"insert","lines":["{}"],"id":24092}],[{"start":{"row":166,"column":52},"end":{"row":168,"column":4},"action":"insert","lines":["","        ","    "],"id":24093}],[{"start":{"row":167,"column":8},"end":{"row":167,"column":10},"action":"insert","lines":["''"],"id":24094}],[{"start":{"row":167,"column":9},"end":{"row":167,"column":10},"action":"insert","lines":["r"],"id":24095},{"start":{"row":167,"column":10},"end":{"row":167,"column":11},"action":"insert","lines":["e"]},{"start":{"row":167,"column":11},"end":{"row":167,"column":12},"action":"insert","lines":["v"]},{"start":{"row":167,"column":12},"end":{"row":167,"column":13},"action":"insert","lines":["i"]},{"start":{"row":167,"column":13},"end":{"row":167,"column":14},"action":"insert","lines":["e"]},{"start":{"row":167,"column":14},"end":{"row":167,"column":15},"action":"insert","lines":["w"]}],[{"start":{"row":167,"column":16},"end":{"row":167,"column":17},"action":"insert","lines":[":"],"id":24096},{"start":{"row":167,"column":17},"end":{"row":167,"column":18},"action":"insert","lines":["{"]}],[{"start":{"row":167,"column":18},"end":{"row":169,"column":9},"action":"insert","lines":["","            ","        }"],"id":24097}],[{"start":{"row":168,"column":12},"end":{"row":168,"column":14},"action":"insert","lines":["''"],"id":24098}],[{"start":{"row":168,"column":13},"end":{"row":168,"column":14},"action":"insert","lines":["n"],"id":24099},{"start":{"row":168,"column":14},"end":{"row":168,"column":15},"action":"insert","lines":["a"]},{"start":{"row":168,"column":15},"end":{"row":168,"column":16},"action":"insert","lines":["m"]},{"start":{"row":168,"column":16},"end":{"row":168,"column":17},"action":"insert","lines":["e"]}],[{"start":{"row":168,"column":18},"end":{"row":168,"column":19},"action":"insert","lines":[":"],"id":24100},{"start":{"row":168,"column":19},"end":{"row":168,"column":20},"action":"insert","lines":["n"]},{"start":{"row":168,"column":20},"end":{"row":168,"column":21},"action":"insert","lines":["a"]},{"start":{"row":168,"column":21},"end":{"row":168,"column":22},"action":"insert","lines":["m"]},{"start":{"row":168,"column":22},"end":{"row":168,"column":23},"action":"insert","lines":["e"]}],[{"start":{"row":167,"column":8},"end":{"row":167,"column":9},"action":"insert","lines":["{"],"id":24101}],[{"start":{"row":167,"column":8},"end":{"row":167,"column":9},"action":"insert","lines":[":"],"id":24102}],[{"start":{"row":167,"column":8},"end":{"row":167,"column":9},"action":"insert","lines":["'"],"id":24103},{"start":{"row":167,"column":9},"end":{"row":167,"column":10},"action":"insert","lines":["'"]}],[{"start":{"row":167,"column":9},"end":{"row":167,"column":10},"action":"insert","lines":["$"],"id":24104},{"start":{"row":167,"column":10},"end":{"row":167,"column":11},"action":"insert","lines":["p"]},{"start":{"row":167,"column":11},"end":{"row":167,"column":12},"action":"insert","lines":["u"]},{"start":{"row":167,"column":12},"end":{"row":167,"column":13},"action":"insert","lines":["l"]},{"start":{"row":167,"column":13},"end":{"row":167,"column":14},"action":"insert","lines":["l"]}],[{"start":{"row":166,"column":22},"end":{"row":166,"column":28},"action":"remove","lines":["remove"],"id":24105},{"start":{"row":166,"column":22},"end":{"row":166,"column":23},"action":"insert","lines":["u"]},{"start":{"row":166,"column":23},"end":{"row":166,"column":24},"action":"insert","lines":["p"]},{"start":{"row":166,"column":24},"end":{"row":166,"column":25},"action":"insert","lines":["d"]},{"start":{"row":166,"column":25},"end":{"row":166,"column":26},"action":"insert","lines":["a"]},{"start":{"row":166,"column":26},"end":{"row":166,"column":27},"action":"insert","lines":["t"]},{"start":{"row":166,"column":27},"end":{"row":166,"column":28},"action":"insert","lines":["e"]}],[{"start":{"row":169,"column":9},"end":{"row":169,"column":10},"action":"insert","lines":["\\"],"id":24106}],[{"start":{"row":169,"column":9},"end":{"row":169,"column":10},"action":"remove","lines":["\\"],"id":24107}],[{"start":{"row":169,"column":9},"end":{"row":170,"column":0},"action":"insert","lines":["",""],"id":24108},{"start":{"row":170,"column":0},"end":{"row":170,"column":8},"action":"insert","lines":["        "]},{"start":{"row":170,"column":8},"end":{"row":170,"column":9},"action":"insert","lines":["}"]}],[{"start":{"row":170,"column":4},"end":{"row":170,"column":8},"action":"remove","lines":["    "],"id":24109}],[{"start":{"row":169,"column":8},"end":{"row":169,"column":12},"action":"insert","lines":["    "],"id":24110}],[{"start":{"row":170,"column":4},"end":{"row":170,"column":8},"action":"insert","lines":["    "],"id":24111}],[{"start":{"row":172,"column":29},"end":{"row":172,"column":33},"action":"remove","lines":["user"],"id":24112},{"start":{"row":172,"column":29},"end":{"row":172,"column":30},"action":"insert","lines":["p"]},{"start":{"row":172,"column":30},"end":{"row":172,"column":31},"action":"insert","lines":["r"]},{"start":{"row":172,"column":31},"end":{"row":172,"column":32},"action":"insert","lines":["o"]},{"start":{"row":172,"column":32},"end":{"row":172,"column":33},"action":"insert","lines":["d"]},{"start":{"row":172,"column":33},"end":{"row":172,"column":34},"action":"insert","lines":["u"]},{"start":{"row":172,"column":34},"end":{"row":172,"column":35},"action":"insert","lines":["c"]},{"start":{"row":172,"column":35},"end":{"row":172,"column":36},"action":"insert","lines":["t"]}],[{"start":{"row":172,"column":29},"end":{"row":172,"column":36},"action":"remove","lines":["product"],"id":24113},{"start":{"row":172,"column":29},"end":{"row":172,"column":30},"action":"insert","lines":["r"]},{"start":{"row":172,"column":30},"end":{"row":172,"column":31},"action":"insert","lines":["e"]},{"start":{"row":172,"column":31},"end":{"row":172,"column":32},"action":"insert","lines":["v"]},{"start":{"row":172,"column":32},"end":{"row":172,"column":33},"action":"insert","lines":["i"]},{"start":{"row":172,"column":33},"end":{"row":172,"column":34},"action":"insert","lines":["e"]}],[{"start":{"row":172,"column":34},"end":{"row":172,"column":35},"action":"insert","lines":["w"],"id":24114}],[{"start":{"row":172,"column":36},"end":{"row":172,"column":37},"action":"insert","lines":[","],"id":24115}],[{"start":{"row":172,"column":37},"end":{"row":172,"column":38},"action":"insert","lines":[" "],"id":24116}],[{"start":{"row":172,"column":38},"end":{"row":172,"column":43},"action":"insert","lines":["id=id"],"id":24117}],[{"start":{"row":163,"column":44},"end":{"row":163,"column":45},"action":"insert","lines":["/"],"id":24121}],[{"start":{"row":163,"column":45},"end":{"row":163,"column":46},"action":"insert","lines":["p"],"id":24122},{"start":{"row":163,"column":46},"end":{"row":163,"column":47},"action":"insert","lines":["o"]},{"start":{"row":163,"column":47},"end":{"row":163,"column":48},"action":"insert","lines":["s"]},{"start":{"row":163,"column":48},"end":{"row":163,"column":49},"action":"insert","lines":["t"]}],[{"start":{"row":163,"column":48},"end":{"row":163,"column":49},"action":"remove","lines":["t"],"id":24123},{"start":{"row":163,"column":47},"end":{"row":163,"column":48},"action":"remove","lines":["s"]},{"start":{"row":163,"column":46},"end":{"row":163,"column":47},"action":"remove","lines":["o"]},{"start":{"row":163,"column":45},"end":{"row":163,"column":46},"action":"remove","lines":["p"]}],[{"start":{"row":163,"column":45},"end":{"row":163,"column":46},"action":"insert","lines":["<"],"id":24124},{"start":{"row":163,"column":46},"end":{"row":163,"column":47},"action":"insert","lines":[">"]}],[{"start":{"row":163,"column":46},"end":{"row":163,"column":47},"action":"insert","lines":["p"],"id":24125},{"start":{"row":163,"column":47},"end":{"row":163,"column":48},"action":"insert","lines":["o"]},{"start":{"row":163,"column":48},"end":{"row":163,"column":49},"action":"insert","lines":["s"]},{"start":{"row":163,"column":49},"end":{"row":163,"column":50},"action":"insert","lines":["t"]},{"start":{"row":163,"column":50},"end":{"row":163,"column":51},"action":"insert","lines":["_"]},{"start":{"row":163,"column":51},"end":{"row":163,"column":52},"action":"insert","lines":["c"]}],[{"start":{"row":163,"column":52},"end":{"row":163,"column":53},"action":"insert","lines":["o"],"id":24126},{"start":{"row":163,"column":53},"end":{"row":163,"column":54},"action":"insert","lines":["n"]},{"start":{"row":163,"column":54},"end":{"row":163,"column":55},"action":"insert","lines":["t"]},{"start":{"row":163,"column":55},"end":{"row":163,"column":56},"action":"insert","lines":["e"]},{"start":{"row":163,"column":56},"end":{"row":163,"column":57},"action":"insert","lines":["n"]},{"start":{"row":163,"column":57},"end":{"row":163,"column":58},"action":"insert","lines":["t"]}],[{"start":{"row":164,"column":21},"end":{"row":164,"column":22},"action":"insert","lines":[","],"id":24127}],[{"start":{"row":164,"column":22},"end":{"row":164,"column":23},"action":"insert","lines":[" "],"id":24128},{"start":{"row":164,"column":23},"end":{"row":164,"column":24},"action":"insert","lines":["p"]},{"start":{"row":164,"column":24},"end":{"row":164,"column":25},"action":"insert","lines":["o"]},{"start":{"row":164,"column":25},"end":{"row":164,"column":26},"action":"insert","lines":["s"]},{"start":{"row":164,"column":26},"end":{"row":164,"column":27},"action":"insert","lines":["t"]},{"start":{"row":164,"column":27},"end":{"row":164,"column":28},"action":"insert","lines":["_"]},{"start":{"row":164,"column":28},"end":{"row":164,"column":29},"action":"insert","lines":["c"]}],[{"start":{"row":164,"column":29},"end":{"row":164,"column":30},"action":"insert","lines":["o"],"id":24129},{"start":{"row":164,"column":30},"end":{"row":164,"column":31},"action":"insert","lines":["n"]},{"start":{"row":164,"column":31},"end":{"row":164,"column":32},"action":"insert","lines":["t"]},{"start":{"row":164,"column":32},"end":{"row":164,"column":33},"action":"insert","lines":["e"]}],[{"start":{"row":164,"column":23},"end":{"row":164,"column":33},"action":"remove","lines":["post_conte"],"id":24130},{"start":{"row":164,"column":23},"end":{"row":164,"column":35},"action":"insert","lines":["post_content"]}],[{"start":{"row":168,"column":16},"end":{"row":168,"column":17},"action":"remove","lines":["e"],"id":24131},{"start":{"row":168,"column":15},"end":{"row":168,"column":16},"action":"remove","lines":["m"]},{"start":{"row":168,"column":14},"end":{"row":168,"column":15},"action":"remove","lines":["a"]},{"start":{"row":168,"column":13},"end":{"row":168,"column":14},"action":"remove","lines":["n"]}],[{"start":{"row":168,"column":13},"end":{"row":168,"column":14},"action":"insert","lines":["p"],"id":24132},{"start":{"row":168,"column":14},"end":{"row":168,"column":15},"action":"insert","lines":["o"]},{"start":{"row":168,"column":15},"end":{"row":168,"column":16},"action":"insert","lines":["s"]},{"start":{"row":168,"column":16},"end":{"row":168,"column":17},"action":"insert","lines":["t"]}],[{"start":{"row":168,"column":22},"end":{"row":168,"column":23},"action":"remove","lines":["e"],"id":24133},{"start":{"row":168,"column":21},"end":{"row":168,"column":22},"action":"remove","lines":["m"]},{"start":{"row":168,"column":20},"end":{"row":168,"column":21},"action":"remove","lines":["a"]},{"start":{"row":168,"column":19},"end":{"row":168,"column":20},"action":"remove","lines":["n"]}],[{"start":{"row":168,"column":19},"end":{"row":168,"column":20},"action":"insert","lines":["p"],"id":24134},{"start":{"row":168,"column":20},"end":{"row":168,"column":21},"action":"insert","lines":["o"]},{"start":{"row":168,"column":21},"end":{"row":168,"column":22},"action":"insert","lines":["s"]},{"start":{"row":168,"column":22},"end":{"row":168,"column":23},"action":"insert","lines":["t"]},{"start":{"row":168,"column":23},"end":{"row":168,"column":24},"action":"insert","lines":["_"]}],[{"start":{"row":168,"column":24},"end":{"row":168,"column":25},"action":"insert","lines":["c"],"id":24135},{"start":{"row":168,"column":25},"end":{"row":168,"column":26},"action":"insert","lines":["o"]},{"start":{"row":168,"column":26},"end":{"row":168,"column":27},"action":"insert","lines":["n"]},{"start":{"row":168,"column":27},"end":{"row":168,"column":28},"action":"insert","lines":["t"]},{"start":{"row":168,"column":28},"end":{"row":168,"column":29},"action":"insert","lines":["e"]},{"start":{"row":168,"column":29},"end":{"row":168,"column":30},"action":"insert","lines":["n"]},{"start":{"row":168,"column":30},"end":{"row":168,"column":31},"action":"insert","lines":["t"]}],[{"start":{"row":158,"column":48},"end":{"row":158,"column":49},"action":"insert","lines":[","],"id":24136}],[{"start":{"row":158,"column":49},"end":{"row":158,"column":50},"action":"insert","lines":[" "],"id":24137},{"start":{"row":158,"column":50},"end":{"row":158,"column":51},"action":"insert","lines":["p"]},{"start":{"row":158,"column":51},"end":{"row":158,"column":52},"action":"insert","lines":["o"]},{"start":{"row":158,"column":52},"end":{"row":158,"column":53},"action":"insert","lines":["s"]},{"start":{"row":158,"column":53},"end":{"row":158,"column":54},"action":"insert","lines":["t"]}],[{"start":{"row":158,"column":53},"end":{"row":158,"column":54},"action":"remove","lines":["t"],"id":24138},{"start":{"row":158,"column":52},"end":{"row":158,"column":53},"action":"remove","lines":["s"]},{"start":{"row":158,"column":51},"end":{"row":158,"column":52},"action":"remove","lines":["o"]},{"start":{"row":158,"column":50},"end":{"row":158,"column":51},"action":"remove","lines":["p"]},{"start":{"row":158,"column":49},"end":{"row":158,"column":50},"action":"remove","lines":[" "]},{"start":{"row":158,"column":48},"end":{"row":158,"column":49},"action":"remove","lines":[","]}],[{"start":{"row":165,"column":4},"end":{"row":165,"column":26},"action":"remove","lines":["name = session['name']"],"id":24139},{"start":{"row":165,"column":4},"end":{"row":165,"column":5},"action":"insert","lines":["p"]},{"start":{"row":165,"column":5},"end":{"row":165,"column":6},"action":"insert","lines":["o"]},{"start":{"row":165,"column":6},"end":{"row":165,"column":7},"action":"insert","lines":["s"]},{"start":{"row":165,"column":7},"end":{"row":165,"column":8},"action":"insert","lines":["t"]}],[{"start":{"row":165,"column":4},"end":{"row":165,"column":8},"action":"remove","lines":["post"],"id":24140},{"start":{"row":165,"column":4},"end":{"row":165,"column":16},"action":"insert","lines":["post_content"]}],[{"start":{"row":165,"column":16},"end":{"row":165,"column":17},"action":"insert","lines":[" "],"id":24141},{"start":{"row":165,"column":17},"end":{"row":165,"column":18},"action":"insert","lines":["="]}],[{"start":{"row":165,"column":18},"end":{"row":165,"column":19},"action":"insert","lines":[" "],"id":24142}],[{"start":{"row":163,"column":58},"end":{"row":163,"column":59},"action":"insert","lines":["?"],"id":24143},{"start":{"row":163,"column":59},"end":{"row":163,"column":60},"action":"insert","lines":["="]}],[{"start":{"row":163,"column":59},"end":{"row":163,"column":60},"action":"remove","lines":["="],"id":24144}],[{"start":{"row":163,"column":45},"end":{"row":163,"column":46},"action":"remove","lines":["<"],"id":24146}],[{"start":{"row":163,"column":58},"end":{"row":163,"column":59},"action":"insert","lines":["<"],"id":24147}],[{"start":{"row":163,"column":58},"end":{"row":163,"column":59},"action":"insert","lines":["="],"id":24148}],[{"start":{"row":163,"column":60},"end":{"row":163,"column":61},"action":"insert","lines":["i"],"id":24149},{"start":{"row":163,"column":61},"end":{"row":163,"column":62},"action":"insert","lines":["d"]}],[{"start":{"row":165,"column":18},"end":{"row":165,"column":19},"action":"remove","lines":[" "],"id":24150},{"start":{"row":165,"column":17},"end":{"row":165,"column":18},"action":"remove","lines":["="]},{"start":{"row":165,"column":16},"end":{"row":165,"column":17},"action":"remove","lines":[" "]},{"start":{"row":165,"column":15},"end":{"row":165,"column":16},"action":"remove","lines":["t"]},{"start":{"row":165,"column":14},"end":{"row":165,"column":15},"action":"remove","lines":["n"]},{"start":{"row":165,"column":13},"end":{"row":165,"column":14},"action":"remove","lines":["e"]},{"start":{"row":165,"column":12},"end":{"row":165,"column":13},"action":"remove","lines":["t"]},{"start":{"row":165,"column":11},"end":{"row":165,"column":12},"action":"remove","lines":["n"]},{"start":{"row":165,"column":10},"end":{"row":165,"column":11},"action":"remove","lines":["o"]},{"start":{"row":165,"column":9},"end":{"row":165,"column":10},"action":"remove","lines":["c"]},{"start":{"row":165,"column":8},"end":{"row":165,"column":9},"action":"remove","lines":["_"]},{"start":{"row":165,"column":7},"end":{"row":165,"column":8},"action":"remove","lines":["t"]},{"start":{"row":165,"column":6},"end":{"row":165,"column":7},"action":"remove","lines":["s"]},{"start":{"row":165,"column":5},"end":{"row":165,"column":6},"action":"remove","lines":["o"]},{"start":{"row":165,"column":4},"end":{"row":165,"column":5},"action":"remove","lines":["p"]}],[{"start":{"row":165,"column":0},"end":{"row":165,"column":4},"action":"remove","lines":["    "],"id":24151},{"start":{"row":164,"column":37},"end":{"row":165,"column":0},"action":"remove","lines":["",""]}],[{"start":{"row":163,"column":61},"end":{"row":163,"column":62},"action":"remove","lines":["d"],"id":24152},{"start":{"row":163,"column":60},"end":{"row":163,"column":61},"action":"remove","lines":["i"]}],[{"start":{"row":163,"column":60},"end":{"row":163,"column":61},"action":"insert","lines":["p"],"id":24153},{"start":{"row":163,"column":61},"end":{"row":163,"column":62},"action":"insert","lines":["o"]},{"start":{"row":163,"column":62},"end":{"row":163,"column":63},"action":"insert","lines":["s"]},{"start":{"row":163,"column":63},"end":{"row":163,"column":64},"action":"insert","lines":["t"]}],[{"start":{"row":163,"column":60},"end":{"row":163,"column":64},"action":"remove","lines":["post"],"id":24154},{"start":{"row":163,"column":60},"end":{"row":163,"column":72},"action":"insert","lines":["post_content"]}],[{"start":{"row":164,"column":37},"end":{"row":165,"column":0},"action":"insert","lines":["",""],"id":24158},{"start":{"row":165,"column":0},"end":{"row":165,"column":4},"action":"insert","lines":["    "]},{"start":{"row":165,"column":4},"end":{"row":165,"column":5},"action":"insert","lines":["p"]},{"start":{"row":165,"column":5},"end":{"row":165,"column":6},"action":"insert","lines":["r"]},{"start":{"row":165,"column":6},"end":{"row":165,"column":7},"action":"insert","lines":["i"]},{"start":{"row":165,"column":7},"end":{"row":165,"column":8},"action":"insert","lines":["n"]},{"start":{"row":165,"column":8},"end":{"row":165,"column":9},"action":"insert","lines":["t"]}],[{"start":{"row":165,"column":9},"end":{"row":165,"column":11},"action":"insert","lines":["()"],"id":24159}],[{"start":{"row":165,"column":10},"end":{"row":165,"column":11},"action":"insert","lines":["p"],"id":24160},{"start":{"row":165,"column":11},"end":{"row":165,"column":12},"action":"insert","lines":["o"]},{"start":{"row":165,"column":12},"end":{"row":165,"column":13},"action":"insert","lines":["s"]},{"start":{"row":165,"column":13},"end":{"row":165,"column":14},"action":"insert","lines":["t"]}],[{"start":{"row":165,"column":10},"end":{"row":165,"column":14},"action":"remove","lines":["post"],"id":24161},{"start":{"row":165,"column":10},"end":{"row":165,"column":22},"action":"insert","lines":["post_content"]}],[{"start":{"row":165,"column":22},"end":{"row":165,"column":23},"action":"insert","lines":["'"],"id":24162}],[{"start":{"row":165,"column":10},"end":{"row":165,"column":11},"action":"insert","lines":["'"],"id":24163}],[{"start":{"row":165,"column":10},"end":{"row":165,"column":11},"action":"insert","lines":[","],"id":24164}],[{"start":{"row":165,"column":10},"end":{"row":165,"column":11},"action":"remove","lines":[","],"id":24165}],[{"start":{"row":165,"column":24},"end":{"row":165,"column":25},"action":"insert","lines":[","],"id":24166},{"start":{"row":165,"column":25},"end":{"row":165,"column":26},"action":"insert","lines":["p"]},{"start":{"row":165,"column":26},"end":{"row":165,"column":27},"action":"insert","lines":["o"]},{"start":{"row":165,"column":27},"end":{"row":165,"column":28},"action":"insert","lines":["s"]},{"start":{"row":165,"column":28},"end":{"row":165,"column":29},"action":"insert","lines":["t"]}],[{"start":{"row":165,"column":29},"end":{"row":165,"column":30},"action":"insert","lines":["-"],"id":24167},{"start":{"row":165,"column":30},"end":{"row":165,"column":31},"action":"insert","lines":["C"]},{"start":{"row":165,"column":31},"end":{"row":165,"column":32},"action":"insert","lines":["O"]},{"start":{"row":165,"column":32},"end":{"row":165,"column":33},"action":"insert","lines":["N"]},{"start":{"row":165,"column":33},"end":{"row":165,"column":34},"action":"insert","lines":["T"]},{"start":{"row":165,"column":34},"end":{"row":165,"column":35},"action":"insert","lines":["E"]},{"start":{"row":165,"column":35},"end":{"row":165,"column":36},"action":"insert","lines":["N"]},{"start":{"row":165,"column":36},"end":{"row":165,"column":37},"action":"insert","lines":["T"]}],[{"start":{"row":165,"column":36},"end":{"row":165,"column":37},"action":"remove","lines":["T"],"id":24168},{"start":{"row":165,"column":35},"end":{"row":165,"column":36},"action":"remove","lines":["N"]},{"start":{"row":165,"column":34},"end":{"row":165,"column":35},"action":"remove","lines":["E"]},{"start":{"row":165,"column":33},"end":{"row":165,"column":34},"action":"remove","lines":["T"]},{"start":{"row":165,"column":32},"end":{"row":165,"column":33},"action":"remove","lines":["N"]},{"start":{"row":165,"column":31},"end":{"row":165,"column":32},"action":"remove","lines":["O"]},{"start":{"row":165,"column":30},"end":{"row":165,"column":31},"action":"remove","lines":["C"]},{"start":{"row":165,"column":29},"end":{"row":165,"column":30},"action":"remove","lines":["-"]}],[{"start":{"row":165,"column":29},"end":{"row":165,"column":30},"action":"insert","lines":["_"],"id":24169}],[{"start":{"row":165,"column":25},"end":{"row":165,"column":30},"action":"remove","lines":["post_"],"id":24170},{"start":{"row":165,"column":25},"end":{"row":165,"column":37},"action":"insert","lines":["post_content"]}],[{"start":{"row":100,"column":27},"end":{"row":100,"column":52},"action":"remove","lines":[", methods=['GET', 'POST']"],"id":24171}],[{"start":{"row":101,"column":41},"end":{"row":101,"column":66},"action":"remove","lines":[", methods=['GET', 'POST']"],"id":24172}],[{"start":{"row":6,"column":0},"end":{"row":6,"column":13},"action":"remove","lines":["import bcrypt"],"id":24174},{"start":{"row":5,"column":35},"end":{"row":6,"column":0},"action":"remove","lines":["",""]}]]},"ace":{"folds":[],"scrolltop":120,"scrollleft":0,"selection":{"start":{"row":5,"column":35},"end":{"row":5,"column":35},"isBackwards":false},"options":{"guessTabSize":true,"useWrapMode":false,"wrapToView":true},"firstLineState":{"row":7,"state":"start","mode":"ace/mode/python"}},"timestamp":1568756586505}