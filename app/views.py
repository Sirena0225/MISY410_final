# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import render_template, request, redirect, url_for, flash
from jinja2  import TemplateNotFound
from datetime import datetime

# App modules
from app import app, dbConn, cursor
# from app.models import Profiles

# App main route + generic routing
@app.route('/')
def index():
    return render_template('index.html')

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


@app.route('/about')
def about():
    return render_template('about.html')
