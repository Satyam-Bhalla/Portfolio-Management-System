from flask import Flask, render_template, request
import base64

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
	if request.method == 'POST':
		a = request.files['chooseFile']
		b = a.read()
		img = base64.b64encode(b)
		image = img.decode('utf-8')
		return f"<img src='data:image/png;base64,{image}'>"
	return '''<form action='' method='POST' enctype='multipart/form-data'>
	           <input type='file' name='chooseFile'>
	           <input type='submit'>'''

if __name__ == '__main__':
	app.run()