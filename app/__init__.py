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


# Import routing to render the pages
from app import views
