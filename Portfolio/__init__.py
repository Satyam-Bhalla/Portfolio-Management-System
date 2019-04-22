from flask import Flask,render_template, request, url_for, session, redirect
from datetime import datetime
import sqlite3
import base64

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'

conn = sqlite3.connect("data.db")
c = conn.cursor()

def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS users (id integer primary key autoincrement, name text, email text, mobile text, password text)")
	c.execute("CREATE TABLE IF NOT EXISTS details (id integer primary key autoincrement, f_id integer, git text, image text, about text, foreign key(f_id) references users(id))")
	c.execute("CREATE TABLE IF NOT EXISTS timeline(id integer primary key autoincrement, f_id integer, words text, image text, dateColumn datetime, auth text, foreign key(f_id) references users(id))")

create_table()
conn.commit()
conn.close()


@app.route('/',methods=['POST','GET'])
def index():
	if request.method == 'POST':
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
	return render_template('index.html')

@app.route('/dash',methods=['POST','GET'])
def dash():
	if session['username']:
		photo = ""
		name =""
		email =""
		git = ""
		mob = ""
		conn = sqlite3.connect("data.db")
		c = conn.cursor()
		c.execute("SELECT * FROM users WHERE email=?",(session['username'],))
		new_id = c.fetchone()
		c.execute("SELECT * FROM details WHERE f_id=?",(new_id[0],))
		data = c.fetchone()
		if data:
			name = new_id[1]
			email = new_id[2]
			git = data[1]
			mob = new_id[3]
			photo = data[3]
		if request.method == "POST":
			img = request.files['image']
			a = img.read()
			picc = base64.b64encode(a)
			pic = picc.decode("utf-8")
			conn = sqlite3.connect("data.db")
			c = conn.cursor()
			c.execute("SELECT id FROM users WHERE email=?",(session['username'],))
			i = c.fetchone()
			c.execute("INSERT INTO details(f_id, git, image, about) VALUES(?,?,?,?)",(i[0],request.form['git'],pic,request.form['about']))
			conn.commit()
			return redirect(dash)
		return render_template('dashboard.html',photo=photo,name=name, git=git, mob=mob,email=email)
	return redirect(url_for('index'))

@app.route('/timeline/', methods=['POST','GET'])
def timel():
	if session['username']:
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
	return redirect(url_for('index'))

@app.route('/delete')
def delete():
	if session['username']:
		conn = sqlite3.connect("data.db")
		c = conn.cursor()
		c.execute("DELETE FROM users WHERE email=?",(session['username'],))
		conn.commit()
		conn.close()
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/logout')
def log():
	if session['username']:
		session['username'] = None
		return redirect(url_for('index'))
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)