from flask import Flask, render_template
app = Flask(__name__)

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

@app.route('/')
def index():
	return render_template('index.html', name=name, companys=companys)