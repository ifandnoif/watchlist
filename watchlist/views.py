# _*_ coding: utf-8 _*_
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Company


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST': # 判断是否是POST请求
		if not current_user.is_authenticated: # 如果当用户未认证
			return redirect(url_for('index')) # 重定向到主页
		# 获取表单数据
		title = request.form['title'] # 传入表单对应输入的name值
		code = request.form['code'] # 重定向到主页
		# 验证数据
		if not title or not code or len(code) > 6 or len(title) > 60:
			flash('输入的信息无效。') # 显示错误信息
			return redirect(url_for('index')) # 重定向主页

		company = Company(title=title, code=code) # 创建记录
		db.session.add(company) # 添加数据库会话
		db.session.commit() # 提交数据库会话
		flash('上市公司新增完成。') # 显示成功创建的提示
		return redirect(url_for('index')) # 重定向回主页

	companys = Company.query.all() # 读取所有上市公司记录
	return render_template('index.html', companys=companys)


@app.route('/company/edit/<int:company_id>', methods=['GET', 'POST'])
@login_required # 登陆保护
def edit(company_id):
	company = Company.query.get_or_404(company_id)

	if request.method == 'POST': # 处理编辑表单的提交请求
		title = request.form['title']
		code = request.form['code']

		if not title or not code or len(code) > 6 or len(title) > 60:
			flash('输入的信息无效。')
			return redirect(url_for('edit', company_id = company_id))
	# 重定向回对应的编辑页面
		company.title = title # 更新股票名称
		company.code = code # 更新股票代码
		db.session.commit() # 提交数据库会话
		flash('上市公司编辑完成。')
		return redirect(url_for('index')) # 重定向回主页

	return render_template('edit.html', company=company) # 传入被编辑的上市公司记录


@app.route('/company/delete/<int:company_id>', methods=['POST']) # 限定只接受POST请求
@login_required # 登录保护
def delete(company_id):
	company = Company.query.get_or_404(company_id) # 获取股票信息
	db.session.delete(company) # 删除对应的记录
	db.session.commit() # 提交数据库会话
	flash('上市公司已删除。')
	return redirect(url_for('index')) # 重定向回主页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	if request.method == 'POST':
		name = request.form['name']

		if not name or len(name) > 20:
			flash('输入的信息无效')
			return redirect(url_for('settings'))

		user = User.query.first()
		user.name = name
		db.session.commit()
		flash('设置完毕。')
		return redirect(url_for('index'))

	return render_template('settings.html')


@app.route('/login',methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		if not username or not password:
			flash('输入的信息无效。')
			return redirect(url_for('login'))

		user = User.query.first()

		if username == user.username and user.validate_password(password):
			login_user(user)
			flash('登陆成功。')
			return redirect(url_for('index')) # 重定向到主页

		flash('输入的登录信息有误。') # 如果验证失败，显示错误消息
		return redirect(url_for('login'))

	return render_template('login.html')


@app.route('/logout')
@login_required # 用于视图保护
def logout():
	logout_user() # 退出登录
	flash('已退出登录。')
	return redirect(url_for('index')) # 重定向回首页