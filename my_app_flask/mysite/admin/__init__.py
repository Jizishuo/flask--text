from flask import Blueprint

admin = Blueprint("admin", __name__)

import mysite.admin.views