from flask import Flask,render_template, request, url_for, session, redirect, jsonify
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime
import requests
import sqlite3
import base64
import re

app = Flask(__name__)

s = URLSafeTimedSerializer('Thisisasecret!')

app.config['SECRET_KEY'] = 'secret'

conn = sqlite3.connect("data.db")
c = conn.cursor()

def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS users (id integer primary key autoincrement, name text, email text, mobile text, password text)")
	c.execute("CREATE TABLE IF NOT EXISTS details (id integer primary key autoincrement, f_id integer, git text, image text, about text,token text, link integer, foreign key(f_id) references users(id))")
	c.execute("CREATE TABLE IF NOT EXISTS timeline(id integer primary key autoincrement, f_id integer, words text, image text, dateColumn datetime, auth text, foreign key(f_id) references users(id))")
	c.execute("CREATE TABLE IF NOT EXISTS profile (id integer primary key autoincrement, f_id integer, foreign key(f_id) references users(id))")

create_table()
conn.commit()
conn.close()


@app.route('/',methods=['POST','GET'])
def index():
	if request.method == 'POST':
		try:
			if request.form['test'] == 'login':
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				email = request.form['lemail']
				c.execute("SELECT * FROM users WHERE email=?",(email,))
				user = c.fetchone()
				conn.commit()
				conn.close()
				if user:
					if user[4] == request.form['lpass']:
						session['username'] = str(email)
						return redirect(url_for('dash'))
					return render_template('index.html',msg='wrong')
				return render_template('index.html',msg='wrong')
			elif request.form['test'] == 'signup':
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				names = request.form['name']
				email = request.form['semail']
				mobile = request.form['mobile']
				spass = request.form['spass']
				c.execute("SELECT * FROM users WHERE email=?",(email,))
				data = c.fetchone()
				if data:
					msg = 'warning'
					return render_template('index.html', msg=msg)
				else:
					c.execute("INSERT INTO users(name, email, mobile, password) VALUES(?,?,?,?)",(names, email, mobile, spass))
				conn.commit()
				conn.close()
			return render_template('index.html', msg='success')
		except Exception as e:
			return str(e)
			return render_template('hidden.html')
	return render_template('index.html')

@app.route('/dash',methods=['POST','GET'])
def dash():
	if session['username']:
		try:
			test = 5
			token = s.dumps(session['username'])
			url = request.url_root + 'prof/'+ token
			photo = ""
			git = ""
			ab = ""
			conn = sqlite3.connect("data.db")
			c = conn.cursor()
			c.execute("SELECT * FROM users WHERE email=?",(session['username'],))
			new_id = c.fetchone()
			name = new_id[1]
			email = new_id[2]
			mob = new_id[3]
			c.execute("SELECT * FROM details WHERE f_id=?",(new_id[0],))
			data = c.fetchone()
			if data:
				git = data[2]
				ab = data[4]
				photo = data[3]
				privateBool = data[6]
			else:
				privateBool = 0
			if request.method == "POST":
				pic = ""
				privateBool = 0
				if 'pri' in request.form:
					privateBool = 1
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				c.execute("SELECT * FROM users WHERE email=?",(session['username'],))
				new_id = c.fetchone()
				c.execute("SELECT * FROM details WHERE f_id=?",(new_id[0],))
				data = c.fetchone()
				if data:
					pic = data[3]
				if request.files['image']:
					img = request.files['image']
					a = img.read()
					picc = base64.b64encode(a)
					pic = picc.decode("utf-8")
				c.execute("SELECT id FROM users WHERE email=?",(session['username'],))
				i = c.fetchone()
				if data:
					c.execute("UPDATE details SET git=?,image=?,about=?, link=?",(request.form['git'],pic,request.form['about'],privateBool))
				else:
					c.execute("INSERT INTO details(f_id, git, image, about,token, link) VALUES(?,?,?,?,?,?)",(i[0],request.form['git'],pic,request.form['about'],token,privateBool))
				conn.commit()
				return redirect(url_for('dash'))
			return render_template('dashboard.html',ab=ab,test=test,privateBool=privateBool,url=url,photo=photo,name=name, git=git, mob=mob,email=email)
		except Exception as e:
			return str(e)
			return render_template('hidden.html')
	return redirect(url_for('index'))

@app.route('/prof/<link>')
def profile(link):
	try:
		url = request.url_root + link
		l = s.loads(link)
		conn = sqlite3.connect("data.db")
		c = conn.cursor()
		c.execute("SELECT * FROM users WHERE email=?",(l,))
		new_id = c.fetchone()
		c.execute("SELECT * FROM details WHERE f_id=?",(new_id[0],))
		data = c.fetchone()
		name = new_id[1]
		email = new_id[2]
		mob = new_id[3]
		git = ""
		photo =""
		ab = ""
		privateBool = 0
		if data:
			git = data[2]
			photo = data[3]
			ab = data[4]
			privateBool = data[6]
		if privateBool == 0:
			return render_template('dashboard.html',ab=ab,privateBool=privateBool,url=url,photo=photo,name=name, git=git, mob=mob,email=email)
		return render_template('hidden.html')
	except Exception as e:
		return str(e)
		return render_template('hidden.html')

@app.route('/search',methods=['POST'])
def search():
	if request.method == 'POST':
		n = request.form['n']
		a = re.compile(str(request.form['n']), re.IGNORECASE)
		doc = []
		details = []
		url = request.url_root + 'prof/'
		conn = sqlite3.connect("data.db")
		c = conn.cursor()
		c.execute("SELECT * FROM users")
		z = c.fetchall()
		for i in z:
			b = a.findall(i[1])
			for j in b:
				c.execute("SELECT * FROM details WHERE f_id=?",(i[0],))
				h = c.fetchone()
				if i not in doc:
					doc.append(i)
					details.append(h)
		return render_template('s.html',doc=doc,details=details,url=url)

@app.route('/timeline/', methods=['POST','GET'])
def timel():
	if session['username']:
		try:
			response = requests.get("http://127.0.0.1:8000/")
			r = response.json()
			posts = r['timeline']
			if request.method == 'POST':
				user_email = session['username']
				img = request.files['chooseFile']
				if img:
					file = img.read()
					b64 = base64.b64encode(file)
					picc = b64.decode('utf-8')
					if picc[0] == '/':
						pic = picc[1:]
					else:
						pic = picc
				else:
					pic = "0"
				text = '.'
				if request.form['data']:
					text = request.form['data']
				response = requests.post(f"http://127.0.0.1:8000/{user_email}/img&{pic}/{text}")
				return redirect(url_for('timel'))
			return render_template('timeline.html',posts=posts)
		except Exception as e:
			return str(e)
			return render_template('hidden.html')
	return redirect(url_for('index'))

@app.route('/delete')
def delete():
	if session['username']:
		try:
			conn = sqlite3.connect("data.db")
			c = conn.cursor()
			c.execute("DELETE FROM users WHERE email=?",(session['username'],))
			conn.commit()
			conn.close()
			session['username'] = None
			return redirect(url_for('index'))
		except:
			return render_template('hidden.html')
	return redirect(url_for('index'))

@app.route('/logout')
def log():
	if session['username']:
		session['username'] = None
		return redirect(url_for('index'))
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)