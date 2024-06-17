# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import render_template, request, redirect, url_for, flash, json, session
from jinja2  import TemplateNotFound
from datetime import datetime
import random

# App modules
from app import app, dbConn, cursor
# from app.models import Profiles

# App main route + generic routing
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginsumbit')
def loginsumbit():
    email = request.form['email']
    password = request.form['password']
    cursor.execute("SELECT * FROM Userprofile WHERE email = %s AND password = %s", (email, password))
    result = cursor.fetchall()
    cursor.execute("SELECT * FROM Userprofile WHERE email = %s", email)
    result_findaccount = cursor.fetchall()
    error = False
    if not result_findaccount:
        error = True
        flash('Your account is not existed!')

    if not result:
        error = True
        flash('The entered password is incorrect!')
    
    if result:
        flash('Login Success!')
        render_template('index.html')

    if error:
        return render_template('login.html', email=email, password=password)
      

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registersumbit', methods=['POST'])
def registersumbit():
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    session['first_name'] = firstname
    session['last_name'] = lastname
    session['email'] = email
    session['password'] = password

    sql = "INSERT INTO Userprofile (first_name, last_name, email, password) values(%s, %s, %s, %s)"
    print(cursor.mogrify(sql,(firstname, lastname, email, password)))
    cursor.execute(sql, (firstname, lastname, email, password))
    flash('New user added successfully')
    return render_template('login.html')



@app.route('/profile')
def profile():
    sql = ''' 
    SELECT 
    CASE
        WHEN age < 16 THEN '<16'
        WHEN age BETWEEN 16 AND 25 THEN '16~25'
        WHEN age BETWEEN 26 AND 40 THEN '25~40'
        ELSE '>40'
      END AS label,
      COUNT(*) AS value
    FROM
      Userprofile
    GROUP BY
      CASE
        WHEN age < 16 THEN '<16'
        WHEN age BETWEEN 16 AND 25 THEN '16~25'
        WHEN age BETWEEN 26 AND 40 THEN '25~40'
        ELSE '>40'
      END '''
    cursor.execute(sql)
    print(cursor.mogrify(sql))
    ageinfo = cursor.fetchall()
    chart_data = json.dumps(ageinfo)

    return render_template('profile.html', chart_data=chart_data)

@app.route('/requestSubmit', methods=['POST'])
def requestsubmit():
    # get the info from post data
    date = datetime.now()
    item = request.form['item']
    addr = request.form['address']
    budg = request.form['budget']
    rewd = request.form['reward']
    phone = request.form['phone']
    time = request.form['time']
    error = False
    
    if not item or item=="":
        error = True
        flash('Item name is required')

    if not addr or addr=="":
        error = True
        flash('Store Address is required')
    
    if not budg or budg=="":
        error = True
        flash('Item budget is required')

    if not rewd or rewd=="":
        error = True
        flash('Reward is required')

    if not phone or phone=="":
        error = True
        flash('Phone number is required')

    if not time or time=="":
        error = True
        flash('Delivery Time is required')


    if error:
        # return to the form page
        return render_template('index.html', item=item, addr=addr, budg=budg, rewd=rewd, phone=phone, time=time)
    else:
        sql = "INSERT INTO Request (RequestTime, RequestContent, Address, Budget, Reward, PhoneNumber, DeliveryTime) values(%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (date, item, addr, float(budg), float(rewd), phone, time))
        return render_template('req-success.html')






@app.route('/myrequest')
def myrequest():
    return render_template('myrequest.html')


@app.route('/data')
def data():
    return render_template('data.html')


@app.route('/dataRequest')
def dataRequest():
    # retrieve a list of supplier IDs from the database and pass then to the page
    sql = "select Address from Requests"
    cursor.execute(sql)
    req = cursor.fetchall()
    return render_template('reqdata.html', requests=req)


@app.route('/requestGraph', methods=['POST'])
def requestGraph():
    # retrieve the supplier ID from the form post data
    addr = request.form.get('addr')

    # get product names and total in-stock values for the products supplied by the selected supplier
    if addr:
        sql = "select Address as Merchant, count(*) as Total_Orders from Requests where Address = %s GROUP BY Address"
        cursor.execute(sql, (addr))
        orders = cursor.fetchall()
        chartData = json.dumps(orders)

    # pass the data to the graph page
    return render_template('reqGraph.html', orders=chartData)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/accept')
def searchproducts():
    return render_template('accept.html')

@app.route("/acceptSubmit",methods=['GET'])
def acceptSubmit():
    so = request.args.get('Searchorders')
    if so:
        sql = "select * from Request where RequestContent = %s"
        cursor.execute(sql,(so))
        orders = cursor.fetchall()
        return render_template('searchaccept.html',orders=orders)
    else:
        return render_template("accept.html")

@app.route("/acceptance", methods=['POST'])
def accept():
    raid = random.randint(1000, 9999)  
    acceTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    rid = request.form.get('rid')
    email = request.form.get('email')
    if raid:
        sql = "INSERT INTO Request_acceptance (raid, AcceptanceTime, Request_rid, Userprofile_email) VALUES (%s,%s,%s,%s)"
        print(cursor.mogrify(sql,(int(raid),acceTime,int(rid),email)))
        cursor.execute(sql,(int(raid),acceTime,int(rid), email))
        acceptances = cursor.fetchall()
        return render_template('acceptance.html',acceptances = acceptances)
    else:
        return render_template('searchaccept.html')
