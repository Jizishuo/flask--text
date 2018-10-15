from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort, g

@admin.route("/")
#@admin_auth
def index():
    #return render_template("admin/index.html")
    return "<h1>admin</h1>"