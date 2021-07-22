# _*_ coding: utf-8 _*_
import click

from watchlist import app, db
from watchlist.models import User, Company


@app.cli.command() # 注册为命令
@click.option('--drop', is_flag=True, help='创建后删除。')
# 设置选项
def initdb(drop):
	"""初始化数据库。"""
	if drop: # 判断是否输入了选项
		db.drop_all()
	db.create_all()
	click.echo('初始化数据库。') # 输入提示信息


@app.cli.command()
def forge():
	"""生成虚拟数据。"""
	db.create_all()
	# 全局的两个变量移动到这个函数内
	name = '琢磨'
	companys = [
		{'title': '一心堂', 'code': '002727'},
		{'title': '中顺洁柔', 'code': '002511'},
	]

	user = User(name=name)
	db.session.add(user)
	for i in companys:
		company = Company(title=i[title], code=i['code'])
		db.session.add(company)

	db.session.commit()
	click.echo('导入完毕。')


@app.cli.command()
@click.option('--username', prompt=True, help='请输入用户名。')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='请输入用户密码。')
def admin(username, password):
	"""创建用户。"""
	db.create_all()

	user = User.query.first()
	if user is not None:
		click.echo('更新用户信息。')
		user.username = username
		user.set_password(password) # 设置密码
	else:
		click.echo('创建用户。')
		userfd = User(username=username, name='琢磨')
		user.set_password(password) # 设置密码
		db.session.add(user)

	db.session.commit() # 提交数据库会话
	click.echo('用户创建更新完毕。')