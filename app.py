from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import secrets
import hmac
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)

IDENTITY_SECRET = os.getenv("IDENTITY_SECRET")
app.secret_key = os.getenv("FLASK_SECRET_KEY")

def generate_identity_token(email):
    return hmac.new(
        IDENTITY_SECRET.encode(),
        email.encode(),
        "sha256"
    ).hexdigest()

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

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT username, password FROM dsw WHERE username = %s",
            (username,)
        )

        dsw_user = cursor.fetchone()
        cursor.close()
        connection.close()

        if dsw_user and check_password_hash(dsw_user["password"], password):
            session["admin"] = dsw_user["username"]
            return redirect(url_for("dsw_dashboard"))
        else:
            return render_template(
                "dsw_portal.html",
                error="Invalid username or password"
            )

    return render_template("dsw_portal.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT username FROM dsw WHERE email = %s", (email,))

        dsw_user = cursor.fetchone()

        if dsw_user:
            token = secrets.token_urlsafe(32)
            expiry = datetime.now() + timedelta(minutes=15)

            cursor.execute(
                """
                UPDATE dsw
                SET reset_token = %s, reset_token_expiry = %s
                WHERE email = %s
                """,
                (token, expiry, email)
            )

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for("reset_password", token=token))
        cursor.close()
        connection.close()

        return render_template(
            "forgot_password.html",
            error="No DSW account found with that email."
        )
    return render_template("forgot_password.html")    

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT username
        FROM dsw
        WHERE reset_token = %s
        AND reset_token_expiry > %s
        """,
        (token, datetime.now())
    )

    dsw_user = cursor.fetchone()

    if not dsw_user:
        cursor.close()
        connection.close()

        return render_template(
            "forgot_password.html",
            error="This password reset link is invalid or has expired."
        )

    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            cursor.close()
            connection.close()

            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )

        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            """
            UPDATE dsw
            SET password = %s,
                reset_token = NULL,
                reset_token_expiry = NULL
            WHERE username = %s
            """,
            (hashed_password, dsw_user["username"])
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("admin_login"))

    cursor.close()
    connection.close()

    return render_template("reset_password.html")

@app.route("/dsw-dashboard")
def dsw_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """SELECT complaint_id, category, description, status, created_at
        FROM complaints
        ORDER BY created_at DESC
        LIMIT 5
        """
    )

    complaints = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("dsw_dashboard.html", complaints=complaints)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        print("EMAIL RECEIVED:", repr(email))

        if not email.endswith("@student.ruet.ac.bd"):
            return render_template(
                "verify.html",
                error="Please use a valid RUET student email address."
            )

        identity_token = generate_identity_token(email)

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, nickname, pin_hash
            FROM anonymous_students
            WHERE identity_token = %s
            """,
            (identity_token,)
        )

        student = cursor.fetchone()

        cursor.close()
        connection.close()

        if student:
            print("RETURNING STUDENT:", student["nickname"])

            session["pending_student_id"] = student["id"]
            session["pending_nickname"] = student["nickname"]

            return redirect(url_for("student_login"))

        print("NEW STUDENT")

        session["identity_token"] = identity_token

        return redirect(url_for("create_identity"))

    return render_template("verify.html")

@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    student_id = session.get("pending_student_id")

    if not student_id:
        return redirect(url_for("verify"))

    if request.method == "POST":
        pin = request.form["pin"].strip()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, nickname, pin_hash
            FROM anonymous_students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        cursor.close()
        connection.close()

        if not student or not check_password_hash(
            student["pin_hash"], pin
        ):
            return render_template(
                "student_login.html",
                error="Incorrect PIN."
            )

        session.pop("pending_student_id", None)
        session.pop("pending_nickname", None)

        session["student_id"] = student["id"]
        session["student_nickname"] = student["nickname"]

        return redirect(url_for("complaint_form"))

    return render_template("student_login.html")

@app.route("/forgot-pin", methods=["GET", "POST"])
def forgot_pin():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        nickname = request.form["nickname"].strip()
        new_pin = request.form["new_pin"].strip()
        confirm_pin = request.form["confirm_pin"].strip()

        if not email.endswith("@student.ruet.ac.bd"):
            return render_template(
                "forgot_pin.html",
                error="Please use a valid RUET student email address."
            )

        if new_pin != confirm_pin:
            return render_template(
                "forgot_pin.html",
                error="PINs do not match."
            )

        identity_token = generate_identity_token(email)

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, nickname
            FROM anonymous_students
            WHERE identity_token = %s
            """,
            (identity_token,)
        )

        student = cursor.fetchone()

        if not student or student["nickname"] != nickname:
            cursor.close()
            connection.close()

            return render_template(
                "forgot_pin.html",
                error="The email and nickname do not match any UniSync identity."
            )

        new_pin_hash = generate_password_hash(new_pin)

        cursor.execute(
            """
            UPDATE anonymous_students
            SET pin_hash = %s
            WHERE id = %s
            """,
            (new_pin_hash, student["id"])
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("student_login"))

    return render_template("forgot_pin.html")

@app.route("/create-identity", methods=["GET", "POST"])
def create_identity():
    identity_token = session.get("identity_token")

    if not identity_token:
        return redirect(url_for("verify"))

    if request.method == "POST":
        nickname = request.form["nickname"].strip()
        pin = request.form["pin"].strip()

        if not nickname or not pin:
            return render_template(
                "create_identity.html",
                error="Please enter a nickname and PIN."
            )

        pin_hash = generate_password_hash(pin)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO anonymous_students
            (identity_token, nickname, pin_hash)
            VALUES (%s, %s, %s)
            """,
            (identity_token, nickname, pin_hash)
        )

        connection.commit()

        student_id = cursor.lastrowid

        cursor.close()
        connection.close()

        session.pop("identity_token", None)
        session["student_id"] = student_id
        session["student_nickname"] = nickname

        return redirect(url_for("complaint_form"))

    return render_template("create_identity.html")

@app.route("/complaint-form")
def complaint_form():
    return render_template("complaint_form.html")


@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():

    anonymous_id = session.get("student_id")

    if not anonymous_id:
        return redirect(url_for("verify"))

    category = request.form["category"]
    description = request.form["description"]

    complaint_id = "US-" + secrets.token_hex(4).upper()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO complaints
        (complaint_id, anonymous_id, category, description)
        VALUES (%s, %s, %s, %s)
        """,
        (complaint_id, anonymous_id, category, description)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return render_template(
        "complaint_success.html",
        complaint_id=complaint_id
    )

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

@app.route("/dsw-complaint/<complaint_id>")
def view_complaint(complaint_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT complaint_id, category, description, status, created_at
        FROM complaints
        WHERE complaint_id = %s
        """,
        (complaint_id,)
    )

    complaint = cursor.fetchone()

    cursor.close()
    connection.close()

    if not complaint:
        return "Complaint not found", 404

    return render_template(
        "dsw_complaint.html",
        complaint=complaint
    )

@app.route("/dsw-complaints")
def dsw_complaints():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT complaint_id, category, description, status, created_at
        FROM complaints
        ORDER BY created_at DESC
        """
    )

    complaints = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "all_complaints.html",
        complaints=complaints
    )

@app.route("/update-complaint-status/<complaint_id>", methods=["POST"])
def update_complaint_status(complaint_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    status = request.form["status"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE complaints
        SET status = %s
        WHERE complaint_id = %s
        """,
        (status, complaint_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        url_for("view_complaint", complaint_id=complaint_id)
    )

if __name__ == "__main__":
    app.run(debug=True)