from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "delivery_tracking_secret_key"


def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            address TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if search:
        c.execute("""
            SELECT * FROM shipments 
            WHERE customer LIKE ? OR product LIKE ? OR status LIKE ?
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT * FROM shipments")

    shipments = c.fetchall()

    c.execute("SELECT COUNT(*) FROM shipments")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM shipments WHERE status='Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM shipments WHERE status='In Transit'")
    transit = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM shipments WHERE status='Delivered'")
    delivered = c.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        shipments=shipments,
        search=search,
        total=total,
        pending=pending,
        transit=transit,
        delivered=delivered
    )


@app.route("/add", methods=["GET", "POST"])
def add_shipment():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        customer = request.form["customer"]
        product = request.form["product"]
        address = request.form["address"]
        status = request.form["status"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("""
            INSERT INTO shipments (customer, product, address, status)
            VALUES (?, ?, ?, ?)
        """, (customer, product, address, status))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_shipment.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_shipment(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        customer = request.form["customer"]
        product = request.form["product"]
        address = request.form["address"]
        status = request.form["status"]

        c.execute("""
            UPDATE shipments
            SET customer=?, product=?, address=?, status=?
            WHERE id=?
        """, (customer, product, address, status, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    c.execute("SELECT * FROM shipments WHERE id=?", (id,))
    shipment = c.fetchone()

    conn.close()

    return render_template("edit_shipment.html", shipment=shipment)


@app.route("/delete/<int:id>")
def delete_shipment(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM shipments WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)