import os
import sys
import click
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

WIN = sys.platform.startswith('win')
if WIN: #如果是windows系统，使用三个斜线
	prefix = 'sqlite:///'
else: #否则使用四个斜线
	prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(
	app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev' # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前加载配置

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户ID作为参数
	user = User.query.get(int(user_id)) # 用ID作为User模型的主键，查询对应的用户
	return user # 返回用户对象


login_manager.log_view = 'login'
# login_manager.login_message = 'Your custom message'

@app.cli.command() #注册为命令
@click.option('--drop', is_flag=True, help='Greate after drop.')
# 设置选项
def initdb(drop):
	"""初始化数据库Initialize the database."""
	if drop: #判断是否输入了选项
		db.drop_all()
	db.create_all()
	click.echo('初始化数据库完毕！') #输出提示信息

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

@app.cli.command()
@click.option('--username', prompt=True, help='请输入用户名。')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='请输入密码。')
def admin(username, password):
	"""创建用户"""
	db.create_all()

	user = User.query.first()
	if user is not None:
		click.echo('更新用户信息...')
		user.username = username
		user.set_password(password) # 设置密码
	else:
		click.echo('创建用户...')
		user = User(username=username, name='Admin')
		user.set_password(password) # 设置密码
		db.session.add(user)

	db.session.commit() # 提交数据库会话
	click.echo('Done.')			

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True) # 主键
	name = db.Column(db.String(20)) # 名字
	username = db.Column(db.String(20)) # 用户名
	password_hash = db.Column(db.String(128)) # 密码散列值

	def set_password(self, password): # 用来设置密码的方法：接受密码作为参数
		self.password_hash = generate_password_hash(password) # 将生成的密码保持到对应字段
	def validate_password(self, password): # 用于验证密码的方法，接受密码作为参数
		return check_password_hash(self.password_hash, password) # 返回布尔值

class Company(db.Model): #表名将会是company
	id = db.Column(db.Integer, primary_key=True) # 主键
	title = db.Column(db.String(60)) # 上市公司名称
	code = db.Column(db.String(6)) # 股票代码

@app.context_processor # 函数名可以随意修改
def inject_user():
	user = User.query.first()
	return dict(user=user) # 需要返回字典，等同于return{'user':user}

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象做为参数
	return render_template('404.html'), 404 # 返回模板和状态码

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST': # 判断是否是POST请求
		if not current_user.is_authenticated: # 如果当前用户未认证
			return redirect(url_for('index')) # 重定向到主页
		# 获取表单数据
		title = request.form['title'] # 传入表单对应输入字段的name值
		code = request.form['code']
		# 验证数据
		if not title or not code or len(code) > 6 or len(title)> 60:
			flash('输入的内容格式不符') # 显示错误信息
			return redirect(url_for('index')) # 重定向回主页
		# 保存表单数据到数据库
		company = Company(title=title, code=code) # 创建记录
		db.session.add(company) # 添加到数据库会话
		db.session.commit() # 提交数据库会话
		flash('新增完成！') # 显示成功创建的提示
		return redirect(url_for('index')) # 重定向回主页

	companys = Company.query.all() #读取所有上市公司记录
	return render_template('index.html', companys=companys)

@app.route('/company/edit/<int:company_id>', methods=['GET', 'POST'])
@login_required # 登录保护
def edit(company_id):
	company = Company.query.get_or_404(company_id)

	if request.method == 'POST': # 处理编辑表单的提交请求
		title = request.form['title']
		code = request.form['code']

		if not title or not code or len(code) > 6 or len(title) > 60:
			flash('输入的内容格式不符！')
			return redirect(url_for('edit', company_id = company_id))
# 重定向回对应的编辑页面
		company.title = title # 更新股票名称
		company.code = code # 更新股票代码
		db.session.commit() # 提交数据库会话
		flash('编辑完成！')
		return redirect(url_for('index')) # 重定向回主页

	return render_template('edit.html', company=company) # 传入被编辑的电影记录

@app.route('/company/delete/<int:company_id>', methods=['POST']) # 限定只接受POST请求
@login_required # 登录保护
def delete(company_id):
	company = Company.query.get_or_404(company_id) # 获取股票信息
	db.session.delete(company) # 删除对应的记录
	db.session.commit() # 提交数据库会话
	flash('删除完成！')
	return redirect(url_for('index')) # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		if not username or not password:
			flash('输入的信息无效！')
			return redirect(url_for('login'))

		user = User.query.first()
		# 验证用户名和密码是否一致
		
		if username == user.username and user.validate_password(password):
			login_user(user) # 登入用户
			flash('登录成功！')
			return redirect(url_for('index')) # 重定向到主页

		flash('身份验证没有通过！') # 如果验证失败，显示错误消息
		return redirect(url_for('login'))

	return render_template('login.html')

@app.route('/logout')
@login_required # 用于视图保护，后面会详细介绍
def logout():
	logout_user() # 登出用户
	flash('当前已退出登录！')
	return redirect(url_for('index')) # 重定向回首页

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	if request.method == 'POST':
		name = request.form['name']

		if not name or len(name) > 20:
			flash('输入的用户名无效！')
			return redirect(url_for('settings'))

		current_user.name = name
		# current_user 会返回当前登录用户的数据库记录对象
		# 等同于下面的用法
		# user = User.query.first()
		# user.name = name
		db.session.commit()
		flash('设置完成！')
		return redirect(url_for('index'))

	return render_template('settings.html')