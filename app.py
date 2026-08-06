from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/admin-login")
def admin_login():
    return render_template("dsw_portal.html")

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

if __name__ == "__main__":
    app.run(debug=True)