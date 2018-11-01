
from . import api
from home import models



@api.route("/index")
def index():
    return "index"
