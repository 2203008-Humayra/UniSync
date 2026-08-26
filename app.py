from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "unisync-secret-key"

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="unisync"
    )

    return connection

@app.route("/")
def home():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM announcements ORDER BY created_at DESC"
    )

    announcements = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "home.html",
        announcements=announcements
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["admin"] = username
            return redirect(url_for("dsw_dashboard"))

        else:
            return render_template(
                "dsw_portal.html",
                error="Invalid username or password"
    )

    return render_template("dsw_portal.html")

@app.route("/dsw-dashboard")
def dsw_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    return render_template("dsw_dashboard.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/verify")
def verify():
    return render_template("verify.html")

@app.route("/complaint-form")
def complaint_form():
    return render_template("complaint_form.html")


@app.route("/complaint-success")
def complaint_success():
    return render_template("complaint_success.html")

@app.route("/track")
def track():
    return render_template("track.html")

@app.route("/add-announcement", methods=["POST"])
def add_announcement():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    announcement = request.form["announcement"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO announcements (message) VALUES (%s)",
        (announcement,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("dsw_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)