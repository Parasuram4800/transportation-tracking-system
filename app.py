from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            product TEXT,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM shipments")
    data = c.fetchall()

    conn.close()

    return render_template('index.html', shipments=data)

@app.route('/add', methods=['POST'])
def add():
    customer = request.form['customer']
    product = request.form['product']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO shipments (customer, product, status) VALUES (?, ?, ?)",
        (customer, product, status)
    )

    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)