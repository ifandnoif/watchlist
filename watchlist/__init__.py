# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN: #如果是windows系统，使用三个斜线
	prefix = 'sqlite:///'
else: #否则使用四个斜线
	prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户ID作为参数
	from watchlist.models import User 
	user = User.query.get(int(user_id)) # 用ID作为User模型的主键，查询对应的用户
	return user # 返回用户对象


login_manager.login_view = 'login'
# login_manager.login_message = 'Your custon message'


@app.context_processor # 函数名可以随意修改
def inject_user():
	from watchlist.models import User
	user = User.query.first() 
	return dict(user=user) # 需要返回字典，等同于return{'user':user}


from watchlist import views, errors, commands