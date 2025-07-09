from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employees'

mysql = MySQL(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login required', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    cur.close()
    return render_template('index.html', employees=employees)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        position = request.form['position']
        office = request.form['office']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employees (id,name,position,office) VALUES (%s, %s, %s, %s)",
                    (id,name,position,office))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        position = request.form['position']
        office = request.form['office']
        cur.execute("UPDATE employees SET name=%s, position=%s, office=%s WHERE id=%s",
                    (name, department, email, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    else:
        cur.execute("SELECT * FROM employees WHERE id = %s", (id,))
        employee = cur.fetchone()
        cur.close()
        return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM employees WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
