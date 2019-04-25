from flask import Flask,render_template, request, url_for, session, redirect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime
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
				e = request.form['lemail']
				c.execute("SELECT * FROM users WHERE email=?",(e,))
				check = c.fetchone()
				conn.commit()
				conn.close()
				if check:
					if check[4] == request.form['lpass']:
						session['username'] = str(e)
						return redirect(url_for('dash'))
					return render_template('index.html',msg='wrong')
				return render_template('index.html',msg='wrong')
			elif request.form['test'] == 'signup':
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				names = request.form['name']
				e = request.form['semail']
				mobile = request.form['mobile']
				spass = request.form['spass']
				c.execute("SELECT * FROM users WHERE email=?",(e,))
				data = c.fetchone()
				if data:
					msg = 'warning'
					return render_template('index.html', msg=msg)
				else:
					c.execute("INSERT INTO users(name, email, mobile, password) VALUES(?,?,?,?)",(names, e, mobile, spass))
				conn.commit()
				conn.close()
			return render_template('index.html', msg='success')
		except:
			return render_template('hidden.html')
	return render_template('index.html')

@app.route('/dash',methods=['POST','GET'])
def dash():
	if session['username']:
		try:
			k = 5
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
				z = data[6]
			else:
				z = 0
			if request.method == "POST":
				pic = ""
				z = 0
				if 'pri' in request.form:
					z = 1
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
					c.execute("UPDATE details SET git=?,image=?,about=?, link=?",(request.form['git'],pic,request.form['about'],z))
				else:
					c.execute("INSERT INTO details(f_id, git, image, about,token, link) VALUES(?,?,?,?,?,?)",(i[0],request.form['git'],pic,request.form['about'],token,z))
				conn.commit()
				return redirect(url_for('dash'))
			return render_template('dashboard.html',ab=ab,k=k,z=z,url=url,photo=photo,name=name, git=git, mob=mob,email=email)
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
		git = data[2]
		mob = new_id[3]
		photo = data[3]
		z = data[6]
		if z == 0:
			return render_template('dashboard.html',z=z,url=url,photo=photo,name=name, git=git, mob=mob,email=email)
		return render_template('hidden.html')
	except:
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
				details.append(h)
				doc.append(i)
		return render_template('s.html',doc=doc,details=details,url=url)

@app.route('/timeline/', methods=['POST','GET'])
def timel():
	if session['username']:
		try:
			conn = sqlite3.connect("data.db")
			c = conn.cursor()
			c.execute("SELECT * FROM timeline ORDER BY id DESC ")
			posts = c.fetchall()
			conn.close()
			if request.method == 'POST':
				time = datetime.now().strftime("%B %d, %Y %I:%M%p")
				img = request.files['chooseFile']
				a = img.read()
				picc = base64.b64encode(a)
				pic = picc.decode("utf-8")
				conn = sqlite3.connect("data.db")
				c = conn.cursor()
				c.execute("SELECT * FROM users WHERE email=?",(session['username'],))
				i = c.fetchone()
				c.execute("INSERT INTO timeline(f_id, words, image, dateColumn,auth) VALUES(?,?,?,?,?)",(i[0],request.form['data'],pic,time,i[1]))
				conn.commit()
				conn.close()
				return redirect(url_for('timel'))
			return render_template('timeline.html',posts=posts)
		except:
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