from datetime import datetime
from app import db
from werkzeug.security import check_password_hash


#会员
class User(db.Model):
    __tablename__ = "user"
    #__table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)#唯一
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(11), unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    uuid = db.Column(db.String(255), unique=True)

    #关联外键
    userlogs = db.relationship("Userlog", backref="user")
    comments = db.relationship("Comment", backref="user")
    moviecols = db.relationship("Moviecol", backref="user")

    def __repr__(self):
        return "<user %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)



#会员登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)
    #属于哪一个会员
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<userlog %r>" % self.id

#标签
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    moives = db.relationship('Movie', backref='tag') #电影外键

    def __repr__(self):
        return "<Tag %r>" % self.name

#电影
class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)#标号
    title = db.Column(db.String(255), unique=True)#标题
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)#简介
    logo = db.Column(db.String(255), unique=True)#封面
    star = db.Column(db.SmallInteger)#星级
    playnum = db.Column(db.BigInteger)#播放数量
    commentnum = db.Column(db.BigInteger)#评论数量
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))#电影标签
    area = db.Column(db.String(255))#地区
    release_time = db.Column(db.Date)#上映时间
    length = db.Column(db.String(100))#电影时长
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)#电影添加时间

    comments = db.relationship("Comment", backref="movie")#评论外键
    moviecols = db.relationship("Moviecol", backref="movie")

    def __repr__(self):
        return '<movie %r>' % self.title

#预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer, primary_key=True)#标号
    title = db.Column(db.String(255), unique=True)  # 标题
    logo = db.Column(db.String(255), unique=True)  # 封面
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 预告添加时间

    def __repr__(self):
        return '<preview %r>' % self.title

#评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)#标号
    content = db.Column(db.Text)  # 内容
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))#所属电影
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))#所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Comment %r>' % self.id

#电影收藏
class Moviecol(db.Model):
    __tablename__ = "moviecol"
    id = db.Column(db.Integer, primary_key=True)#标号
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))#所属电影
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))#所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Moviecol %r>' % self.id


#权限
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)#标号
    name = db.Column(db.String(100), unique=True)#标题
    url = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 添加时间

    def __repr__(self):
        return '<Auth %r>' % self.name

#角色
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)#标号
    name = db.Column(db.String(100), unique=True)#标题
    auths = db.Column(db.String(600))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    admins = db.relationship("Admin", backref="role")

    def __repr__(self):
        return '<Role %r>' % self.name


#管理员
class Admin(db.Model):
    __tablename__= "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)#唯一
    pwd = db.Column(db.String(100))
    is_super = db.Column(db.SmallInteger)#是否是超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    adminlogs = db.relationship("Adminlog", backref="admin")
    oplogs = db.relationship("Oplog", backref="admin")

    def __repr__(self):
        return "<Admin %r>" % self.name

    def check_pwd(self, pwd):
        return check_password_hash(self.pwd, pwd)

#管理员登录日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer, primary_key=True)
    #属于哪一个管理员
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<adminlog %r>" % self.id


#操作日志
class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer, primary_key=True)
    #属于哪一个管理员
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    ip = db.Column(db.String(100))
    reason = db.Column(db.String(600))#操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<oplog %r>" % self.id


'''if __name__ =="__main__":
    #db.create_all()
    role = Role(
        name="超级管理员",
        auths=""
    )
    db.session.add(role)
    db.session.commit()
    from werkzeug.security import generate_password_hash
    admin = Admin(
        name="jzs",
        pwd=generate_password_hash("19950920"),
        is_super=0,
        role_id=1
    )
    db.session.add(admin)
    db.session.commit()'''