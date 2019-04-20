from flask import Flask,render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'

db = SQLAlchemy(app)

class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(80))
	password = db.Column(db.String(50))
	email = db.Column(db.String(100))
	image = db.Column(db.String)

@app.route('/',methods=['POST','GET'])
def index():
	return render_template('index.html')

@app.route('/dash',methods=['POST','GET'])
def dash():
	return render_template('dashboard.html')

if __name__ == '__main__':
	app.run(debug=True)