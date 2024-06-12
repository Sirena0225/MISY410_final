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

# Import routing to render the pages
from app import views
