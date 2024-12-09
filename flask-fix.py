from flask import Flask, jsonify, request, render_template, redirect, url_for
import subprocess
import sqlite3
import os
import logging
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/home/kali/Desktop/upload"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/")
def main_page():
    return "REST API"

@app.route("/user/<string:name>")
def search_user(name):
    con = sqlite3.connect("test.db")
    cur = con.cursor()
    cur.execute("select * from test where username = ?", (name,))
    data = str(cur.fetchall())
    con.close()
    logging.basicConfig(filename="restapi.log", filemode='w', level=logging.DEBUG)
    logging.debug(data)
    return jsonify(data=data), 200

@app.route("/welcome/<string:name>")
def welcome(name):
    data = f"Welcome {name}"
    return jsonify(data=data), 200

@app.route("/hello")
def hello_ssti():
    if request.args.get('name'):
        name = request.args.get('name')
        template = f'''<div>
        <h1>Hello</h1>
        {name}
</div>'''
        logging.basicConfig(filename="restapi.log", filemode='w', level=logging.DEBUG)
        logging.debug(str(template))
        return render_template_string(template)

@app.route("/get_users")
def get_users():
    try:
        hostname = request.args.get('hostname')
        command = ["dig", hostname]
        data = subprocess.check_output(command)
        return data
    except Exception as e:
        return str(e), 400

@app.route("/read_file")
def read_file():
    filename = request.args.get('filename')
    safe_filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    try:
        with open(safe_filename, "r") as file:
            data = file.read()
        logging.basicConfig(filename="restapi.log", filemode='w', level=logging.DEBUG)
        logging.debug(str(data))
        return jsonify(data=data), 200
    except FileNotFoundError:
        return jsonify(data="File not found"), 404

@app.route("/deserialization/")
def deserialization():
    return jsonify(data="Insecure deserialization is disabled"), 200

@app.route("/get_admin_mail/<string:control>")
def get_admin_mail(control):
    if control == "admin":
        data = "admin@cybersecurity.intra"
        logging.basicConfig(filename="restapi.log", filemode='w', level=logging.DEBUG)
        logging.debug(data)
        return jsonify(data=data), 200
    else:
        return jsonify(data="Control didn't set admin"), 200

@app.route("/run_file")
def run_file():
    try:
        filename = request.args.get("filename")
        safe_filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(safe_filename):
            command = ["/bin/bash", safe_filename]
            data = subprocess.check_output(command)
            return jsonify(data=data), 200
        else:
            return jsonify(data="File not found"), 404
    except Exception as e:
        return jsonify(data=str(e)), 400

@app.route("/create_file", methods=["POST"])
def create_file():
    try:
        filename = request.form.get("filename")
        text = request.form.get("text")
        safe_filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        with open(safe_filename, "w") as file:
            file.write(text)
        return jsonify(data="File created"), 200
    except Exception as e:
        return jsonify(data=str(e)), 400

@app.route('/login', methods=["GET"])
def login():
    username = request.args.get("username")
    passwd = request.args.get("password")
    if re.match(r"^[a-zA-Z0-9_]+$", username) and re.match(r"^[a-zA-Z0-9_]+$", passwd):
        if "anil" in username and "cyber" in passwd:
            return jsonify(data="Login successful"), 200
        else:
            return jsonify(data="Login unsuccessful"), 403
    else:
        return jsonify(data="Invalid username or password format"), 400

@app.route('/upload', methods=['GET', 'POST'])
def uploadfile():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify(data="File uploaded successfully"), 200
        else:
            return jsonify(data="Invalid file type"), 400
    else:
        return '''
<html>
   <body>
      <form method="POST" enctype="multipart/form-data">
         <input type="file" name="file" />
         <input type="submit"/>
      </form>
   </body>
</html>'''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081)
