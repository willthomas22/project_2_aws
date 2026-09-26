import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/var/www/FlaskApp/FlaskApp/uploads'

def get_db_connection():
    conn = sqlite3.connect('/var/www/FlaskApp/FlaskApp/users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    address = request.form['address']

    conn = get_db_connection()
    conn.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                 (username, password, firstname, lastname, email, address))
    conn.commit()
    conn.close()
    return redirect(url_for('profile', username=username))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid credentials. Try again."
    return render_template('login.html')

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    word_count = None
    filename = None

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())

    return render_template('profile.html', user=user, word_count=word_count, filename=filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
