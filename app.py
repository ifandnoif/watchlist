import os
import sys
import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN: #如果是windows系统，使用三个斜线
	prefix = 'sqlite:///'
else: #否则使用四个斜线
	prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(
	app.root_path, 'data.db')
app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
# 在扩展类实例化前加载配置

db = SQLAlchemy(app)

@app.cli.command() #注册为命令
@click.option('--drop', is_flag=True, help='Greate after drop.')
# 设置选项
def initdb(drop):
	"""初始化数据库Initialize the database."""
	if drop: #判断是否输入了选项
		db.drop_all()
	db.create_all()
	click.echo('Initialized database.') #输出提示信息

@app.cli.command()
def forge():
	"""生成虚拟数据Generate fake data."""
	db.create_all
	# 全局的两个变量移动到这个函数内
	name = '琢磨'
	companys = [
		{'title': '中顺洁柔', 'code': '002511'},
		{'title': '绿伞化学', 'code': '430666'},
		{'title': '茶花股份', 'code': '603615'},
		{'title': '天际股份', 'code': '002759'},
		{'title': '上海家化', 'code': '600315'},
		{'title': '晨光文具', 'code': '603899'},
		{'title': '恒通股份', 'code': '603223'},
		{'title': '安车检测', 'code': '300572'},
		{'title': '多伦科技', 'code': '603528'},
		{'title': '南华仪器', 'code': '300417'},
		{'title': '秦川物联', 'code': '688528'},
		{'title': '紫晶存储', 'code': '688086'},
		{'title': '一心堂', 'code': '002727'},
	]	
	user = User(name=name)
	db.session.add(user)
	for i in companys:
		company = Company(title=i['title'], code=i['code'])
		db.session.add(company)

	db.session.commit()
	click.echo('Done')

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True) #主键
	name = db.Column(db.String(20)) #名字

class Company(db.Model): #表名将会是company
	id = db.Column(db.Integer, primary_key=True) #主键
	title = db.Column(db.String(60)) #上市公司名称
	code = db.Column(db.String(6)) #股票代码

@app.context_processor #函数名可以随意修改
def inject_user():
	user = User.query.first()
	return dict(user=user) # 需要返回字典，等同于return{'user':user}

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象做为参数
	return render_template('404.html'), 404 # 返回模板和状态码

@app.route('/')
def index():
	companys = Company.query.all() #读取所有上市公司记录
	return render_template('index.html', companys=companys)

