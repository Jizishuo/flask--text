"""
外卖项目入口
"""

from home import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#创建app
app = create_app('develop')


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)



if __name__ == "__main__":
    #app.run()
    manager.run()


#python manage.py runserver
#python manage.py db init
#python manage.py db migrate -m 'init table'
#python manage.py db upgrade