from flask import Flask,render_template, request, url_for, session

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'

@app.route('/',methods=['POST','GET'])
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)