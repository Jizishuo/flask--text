from . import home
from flask import render_template, redirect, url_for, flash, session, request, abort, g

@home.route("/")
def index():
    #return render_template("admin/index.html")
    return "<h1>home</h1>"