from flask import Flask, render_template, render_template_string, request, redirect
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Create a databse connection in a MySQL server
def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

# Execute querys like CREATE TABLE, ALTER TABLE, INSERT INTO _ VALUES, ....
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

# Read SELECT querys
def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

# User password and Database to make the connection (local machine, change for your local server)
pw = "LocalHost#123"
db = "shop"

# User logged
session = {}

@app.route("/")
def root():
    return "Hello World"

# User page with SQL Injection
@app.route("/<user>")
def hello_world(user):
    query = "SELECT username FROM users WHERE username='"+ user +"';"
    connection = create_db_connection("localhost", "root", pw, db)
    if(read_query(connection, query)):
        return render_template('index.html', user=user)
    else:
        return "User not found."

# Load the products page
@app.route("/products", methods=['GET', 'POST'])
def products():
    if session and session['username']:
        
        templates = []
        query = "SELECT * FROM products;"
        connection = create_db_connection("localhost", "root", pw, db)

        for product in read_query(connection, query):
            templates.append(product)
        
        return render_template('products.html', user=session['username'], products=templates)
    
    return redirect('/login')

# Search by category results with SQL Injection
@app.route("/products/category")
def search():
    if session and session['username']:
        param = request.args.get('search')
        if(param):

            templates = []
            query = "SELECT id,name FROM products WHERE category='" + param + "';"
            connection = create_db_connection("localhost", "root", pw, db)
            products = read_query(connection, query)
            
            if(products):
            
                temp=""

                for product in read_query(connection, query):
                    templates.append(product)
                    temp += """
                                    <p class="product">Id: """+str(product[0])+"""<br>Name: """+product[1]+"""</p>
                    """

                temp1 = """
                    <html>
                        <head>
                            <title>Products</title>
                        </head>
                        <body>
                                <h1>Products from the """ + param + """ category:</h1>
                                <div class="products">"""
                temp2 = """
                                </div>
                        </body>
                    </html>
                """
                return render_template_string(temp1+temp+temp2)
            else:
                return "Product not found."
        
    return redirect('/login')

# Login page with SQL Injection
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        query = "SELECT username, password FROM users WHERE username='"+ request.form['username'] + "' AND password='" + request.form['password'] + "';"
        connection = create_db_connection("localhost", "root", pw, db)
        if(read_query(connection, query)):
            session['username'] = request.form['username']
            return redirect('/products')
        else: 
            return "Erro ao logar"
    else:
        return render_template('login.html')

if __name__=="__main__":
    app.run()