# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Import core packages
import os
import pymysql

# Import Flask 
from flask import Flask

# Inject Flask magic
app = Flask(__name__)

app.secret_key = '12345678asdfghjk'

dbConn = pymysql.connect(
    host='116.62.160.40',
    user='misy410group05',
    password='@m8Wa9jHYORG3hoD7',
    database='misy4110group05',
    autocommit=True,
    port=3306,   
    cursorclass=pymysql.cursors.DictCursor
)

cursor = dbConn.cursor()

# Import routing to render the pages
from app import views
