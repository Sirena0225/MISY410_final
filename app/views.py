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

    return render_template('profile2.html', chart_data=chart_data)

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
    if error:
        return render_template('profile.html', email=email, address=address,age=age,city=city,country=country)
    


    sql = "UPDATE Userprofile SET address=%s, age=%s, city=%s, country=%s WHERE email=%s"
    print(cursor.mogrify(sql, (address, age, city, country, email)))
    cursor.execute(sql, (address, age, city, country, email))
    flash('Your info is added successfully')
    
    return render_template('profile2.html')


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
    email = '123@qq.com'# session.get('email')

    if email:
        sql = "select * from Request where email = %s"
        cursor.execute( sql, (email))
        requests = cursor.fetchall()

    return render_template('myrequest.html', requests=requests)

@app.route('/searchOrders', methods=['GET'])
def SearchOrders():
    # get sid send in the get request
    rid = request.form['rid']

    # retrieve the product records from the database for the given sid
    if rid:
        sql = "select * from Request where rid = %s"
        cursor.execute( sql, (int(rid)))
        requests = cursor.fetchall()

    # send the product table back
    return render_template('myrequest.html', requests=requests)



@app.route('/data')
def data():
    return render_template('data.html')


@app.route('/dataRequest')
def dataRequest():
    # retrieve a list of supplier IDs from the database and pass then to the page
    sql = "select Address from Request"
    cursor.execute(sql)
    req = cursor.fetchall()
    return render_template('reqdata.html', requests=req)


@app.route('/requestGraph', methods=['POST'])
def requestGraph():
    # retrieve the supplier ID from the form post data
    addr = request.form.get('addr')

    # get product names and total in-stock values for the products supplied by the selected supplier
    if addr:
        sql = "select Address as Merchant, count(*) as Total_Orders from Request where Address = %s GROUP BY RequestContent"
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

@app.route('/payer')
def payer():
    return render_template('payer-1.html')

@app.route('/payersubmit', methods=['POST'])
def payersubmit():
        rid = request.form.get('Request-ID')
        pid = request.form.get('Payment-ID')
        PaymentMethodpayer = request.form.get('Pay-Method')
        amountpayer = request.form.get('Amount')
        sql = "INSERT INTO Payment (rid,pid,PaymentMethodpayer,amountpayer) values(%s, %s, %s, %s)"
        print(cursor.mogrify(sql,(rid,pid,PaymentMethodpayer,amountpayer)))
        cursor.execute(sql, (rid,pid,PaymentMethodpayer,amountpayer))
        flash('New payer added successfully')
        return render_template('waiting.html',rid=rid,pid=pid,PaymentMethodpayer=PaymentMethodpayer,amountpayer=amountpayer)

@app.route('/payee')
def payee():
    return render_template('payee-1.html')

@app.route('/payeesubmit', methods=['POST'])
def payeesubmit():
        raid = request.form.get('Acceptance-ID')
        pid = request.form.get('Payment-ID')
        PaymentMethodpayee = request.form.get('Pay-Method')
        amountpayee = float(request.form.get('Amount'))
        PaidTime = datetime.now()

        # GET THE AMOUNT FROM DB USING PID
        sql = "select amountpayer from Payment where pid = %s"
        cursor.execute(sql,(pid))
        row = cursor.fetchone()
        if row:
            amountpayer = float(row['amountpayer'])
        print(cursor.mogrify(sql,(pid)))

                
        # COMPARE THE TWO AMOUNTS
        # IF AMOUTPAYEE < BUYER SPECIFIED AMOUNT, NOTIFY THE BUYER TO UPDATE THE AMOUNT
        if amountpayee < amountpayer:
            
                
            sql = "UPDATE Payment SET raid=%s, PaymentMethodpayee=%s, amountpayee=%s ,PaidTime= %s WHERE pid=%s"
            print(cursor.mogrify(sql,(raid,PaymentMethodpayee,amountpayee,PaidTime, pid)))
            cursor.execute(sql, (raid,PaymentMethodpayee,amountpayee,PaidTime, pid))
            flash('New payer added successfully')
            return render_template('pay-success.html')
        # # ELSE THEN UPDATE
        # sql = "UPDATE Payment SET raid=%s, PaymentMethodpayee=%s, amountpayee=%s WHERE pid=%s"
        # print(cursor.mogrify(sql,(raid,PaymentMethodpayee,amountpayee,pid)))
        # cursor.execute(sql, (raid,PaymentMethodpayee,amountpayee,pid))
        # flash('New payer added successfully')
        else:
            return render_template('payee-2.html',raid=raid,pid=pid,PaymentMethodpayee=PaymentMethodpayee,amountpayee=amountpayee)

# @app.route('/waiting')
# def waiting():
#     pid = request.form.get('Payment-ID')
#     return render_template('waiting.html',pid=pid)

# @app.route('/paysubmit', methods=['POST'])
# def paysubmit():
#         amountpayee = request.form.get('amountpayee')
#         amountpayer = request.form.get('amountpayer')
#         pid = request.form.get('pid')
#         PaidTime = datetime.now()
       
#         if amountpayee and amountpayer:
#             sql = "select * from Payment where pid=%s "

#             cursor.execute(sql,(amountpayee, amountpayer))
#             payment = cursor.fetchone()

#             if payment:
#                 session['amountpayee'] = session['amountpayer']
#                 sql = "INSERT INTO Payment (pid,amountpayee, amountpayer, Paidtime) values(%s, %s, %s, %s)"
#                 flash("Successful!")

#                 return render_template('pay-success.html')
                
#             else:
#                 flash("Amount is incorrect. Please modify.")
#                 return render_template('payee-2.html')

            
@app.route('/modify')
def modify():
    return render_template('payee-2.html')

@app.route('/modifysubmit', methods=['POST'])
def modifysubmit():

    pid = request.form.get('Payment-ID')

    amountpayee = request.form.get('Amount')
    

    sql = "UPDATE Payment SET amountpayee = %s  WHERE pid = %s;"
    print(cursor.mogrify(sql,(amountpayee,  pid)))
    cursor.execute(sql, (amountpayee, pid))
    flash('Modify successfully')
    
    return render_template('confirm.html',pid=pid,amountpayee=amountpayee)

@app.route('/confirm')
def confirm():
    pid = request.form.get('Payment-ID')
    return render_template('confirm.html',pid=pid)

@app.route('/confirmsubmit', methods=['POST'])
def confirmsubmit():
    pid = request.form.get('Payment-ID')
    sql = "select amountpayer from Payment where pid = %s"
    cursor.execute(sql,(pid))
    row = cursor.fetchone()
    if row:
        amountpayee = float(row['amountpayee'])
        print(cursor.mogrify(sql,(pid)))
    PaidTime = datetime.now()

    if 'submit' in request.form:
            return submit(pid, amountpayee)
    elif 'cancel' in request.form:
            return cancel(pid)
    
    def submit(pid, amountpayee_m):    
         db = connect_db()
         cursor = db.cursor()
         cursor.execute("INSERT INTO Payment (pid,amountpayee_m) values(%s, %s)")
         db.commit()
         db.close()
         flash('Payment submitted successfully!')
         return render_template('pay-success.html')

    def cancel(pid):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE * FROM Payment  WHERE pid = pid")
        db.commit()
        db.close()
        flash('Payment Cancel successfully!')
        return render_template('confirm.html')

    


