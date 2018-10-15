from datetime import datetime
from mysite import db
from werkzeug.security import check_password_hash

#from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#mysite = Flask(__name__)
#mysite.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@127.0.0.1:3306/myflask1"
#mysite.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#mysite.debug = True
#db = SQLAlchemy(mysite)

class User(db.Model):
    __tablename__ = "user"
    # __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # 唯一
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(13), unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    uuid = db.Column(db.String(255), unique=True)

    # 关联外键
    # userlogs = db.relationship("Userlog", backref="user")
    # comments = db.relationship("Comment", backref="user")
    # moviecols = db.relationship("Moviecol", backref="user")

    def __repr__(self):
        return "<user %r>" % self.name

    def check_pwd(self, pwd):
        return check_password_hash(self.pwd, pwd)


'''if __name__ == "__main__":
    db.create_all()'''
