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
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginsumbit', methods=['POST'])
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
        session['email'] = email
        login = True
        flash('Login Success!')
        return render_template('index.html', login=login)

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
    return render_template('profile2.html')


@app.route('/userportrait')
def userportrait():
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


    sqll = '''SELECT gender as label, COUNT(*) AS value
            FROM Userprofile
            WHERE gender IS NOT NULL
            GROUP BY gender;'''
    cursor.execute(sqll)
    print(cursor.mogrify(sqll))
    genderinfo = cursor.fetchall()
    gender_data = json.dumps(genderinfo)


    return render_template('userportrait.html', chart_data=chart_data, gender_data = gender_data)

@app.route('/changepassword', methods=['POST'])
def changepassword():
    newpassword = request.form['newpassword']
    email = session.get('email')
    oldpassword = session.get('password')
    if newpassword == oldpassword:
        flash('The password is same as the preview one!')
    if newpassword != oldpassword:
        sql = 'UPDATE Userprofile SET password=%s WHERE email=%s'
        print(cursor.mogrify(sql, (newpassword, email)))
        cursor.execute(sql, (newpassword, email))
        flash('New password updated successfully')
    if not newpassword or newpassword =='':
        return render_template('profile2.html')
    
    return render_template('profile2.html')


@app.route('/completeinfo', methods=['POST'])
def completeinfo():
    email = session.get('email')
    address = request.form['address']
    age = request.form['age']
    city = request.form['city']
    country = request.form['country']
    gender = request.form['gender']
    error = False
    if not email or email == '':
        error = True
        flash('Email is required')
    if not address or address == '':
        error = True
        flash('Address is required')
    if not age or age == '':
        error = True
        flash('Age is required')
    if not city or city == '':
        error = True
        flash('City is required')
    if not country or country == '':
        error = True
        flash('Country is required')
    if not gender:
        error = True
        flash('Gender is required')
    if error:
        return render_template('profile2.html', email=email, address=address, age=age, city=city, country=country, gender=gender)

    sql = "UPDATE Userprofile SET address=%s, age=%s, city=%s, country=%s, gender= %s WHERE email=%s"
    print(cursor.mogrify(sql, (address, age, city, country, gender, email)))
    cursor.execute(sql, (address, age, city, country, gender, email))
    flash('Your info is added successfully')
    return render_template('profile2.html', email=email, address=address, age=age, city=city, country=country, gender= gender)


@app.route('/requestSubmit', methods=['POST'])
def requestsubmit():
    # get the info from post data
    date = datetime.now()
    rid = request.form['rid']
    item = request.form['item']
    addr = request.form['address']
    budg = request.form['budget']
    rewd = request.form['reward']
    email = request.form['email']
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

    if not email or email=="":
        error = True
        flash('Email is required')

    if not time or time=="":
        error = True
        flash('Delivery Time is required')


    if error:
        # return to the form page
        return render_template('index.html', item=item, addr=addr, budg=budg, rewd=rewd, email=email, time=time)
    else:
        if not rid or rid=="":
            sql = "INSERT INTO Request (RequestTime, RequestContent, Address, Budget, Reward, Email, DeliveryTime) values(%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (date, item, addr, float(budg), float(rewd), email, time))
            return render_template('req-success.html')
        else: 
            sql = "UPDATE Request SET RequestContent = %s, Address = %s, Budget = %s, Reward = %s, Email = %s, DeliveryTime = %s WHERE rid = %s"
            cursor.execute(sql, (item, addr, float(budg), float(rewd), email, time, int(rid)))
            return render_template('req-success.html')


@app.route('/myrequest')
def myrequest():
    email = session['email']

    if email:
        sql = "select * from Request where email = %s"
        cursor.execute( sql, (session['email']))
        requests = cursor.fetchall()

    return render_template('myrequest.html', requests=requests)


@app.route("/reqDelete", methods=['POST'])
def reqdelete():
    rid = request.form.get('rid')
    if rid:
        sql = "DELETE FROM Request WHERE rid = %s"
        cursor.execute(sql,(int(rid)))
        sql = "select * from Request WHERE email = %s"
        cursor.execute( sql, (session['email']))
        requests = cursor.fetchall()
        return render_template('myrequest.html', requests=requests)



@app.route('/data')
def data():
    return render_template('data.html')


@app.route('/dataRequest')
def dataRequest():
    # retrieve a list of supplier IDs from the database and pass then to the page
    sql = "select DISTINCT Address from Request"
    cursor.execute(sql)
    req = cursor.fetchall()
    return render_template('reqdata.html', requests=req)


@app.route('/requestGraph', methods=['POST'])
def requestGraph():
    # retrieve the supplier ID from the form post data
    addr = request.form.get('addr')

    # get product names and total in-stock values for the products supplied by the selected supplier
    if addr:
        sql = "select RequestContent as label, count(*) as value from Request where Address = %s GROUP BY RequestContent"
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
    raid = random.randint(1, 9999)  
    acceTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    rid = request.form.get('rid')
    email = request.form.get('email')
    if raid:
        sql = "INSERT INTO Request_acceptance (raid, AcceptanceTime, Request_rid, Userprofile_email) VALUES (%s,%s,%s,%s)"
        print(cursor.mogrify(sql,(int(raid),acceTime,int(rid),email)))
        cursor.execute(sql,(int(raid),acceTime,int(rid), email))

        sql = "select * from Request_acceptance where raid=%s"
        cursor.execute(sql, raid)
        acceptances = cursor.fetchall()
        return render_template('acceptance.html',acceptan = acceptances)
    else:
        return render_template('searchaccept.html')

@app.route("/graphsearch",methods=['GET'])
def graphsearch():
    return render_template('graphsearch.html')


@app.route('/graph',methods=['POST'])
def graph():
    month = request.form.get("month")
    if month:
        sql2="select MONTH(AcceptanceTime) AS label,COUNT(*) AS value FROM Request_acceptance where MONTH(AcceptanceTime) = %s GROUP BY MONTH(AcceptanceTime)"
        cursor.execute(sql2,month)
        product2=cursor.fetchall()
        chart_data2=json.dumps(product2)
        return render_template('graph.html', acceptances=chart_data2)
    else:
        return render_template('graphsearch.html')

@app.route("/Acceptance",methods=['GET'])
def Acceptance():
    sql1="select * from Request_acceptance"
    cursor.execute(sql1)
    product1= cursor.fetchall()
    return render_template('myaccept.html',Acceptances=product1)

@app.route("/acceDelete", methods=['POST'])
def accedelete():
    raid = request.form.get('raid')
    if raid:
        sql = "DELETE FROM Request_acceptance WHERE raid = %s"
        cursor.execute(sql,(int(raid)))

        sql = "select * from Request_acceptance"
        cursor.execute(sql)
        accedelete = cursor.fetchall()
        return render_template('myaccept.html', Acceptances=accedelete)


