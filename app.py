from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
	return '欢迎访问此清单！'