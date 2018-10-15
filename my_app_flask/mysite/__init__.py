from flask import Flask, render_template
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#自建的
from mysite.home import home as home_blueprint
from mysite.admin import admin as admin_blueprint

mysite = Flask(__name__)
mysite.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@127.0.0.1:3306/movie"
mysite.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

mysite.debug = True
db = SQLAlchemy(mysite)



mysite.register_blueprint(home_blueprint)
mysite.register_blueprint(admin_blueprint, url_prefix="/admin")