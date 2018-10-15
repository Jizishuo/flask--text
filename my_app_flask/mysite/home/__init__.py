from flask import Blueprint

home = Blueprint("home", __name__)

import mysite.home.views