from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import pyshorteners

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "ACMkaapnaurlshortener"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_url = db.Column(db.String(256), nullable=False)
    short_url = db.Column(db.String(25), nullable=False)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)


db.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()

        if not user:
            return redirect("register")

        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))
        else:
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        org_url = request.form.get("urlholder")
        short_url = pyshorteners.Shortener().tinyurl.short(org_url)

        url = Url(org_url=org_url, short_url=short_url)

        db.session.add(url)
        db.session.commit()

        return render_template("home.html", short_url=short_url)

    urls = Url.query.all()

    return render_template("home.html", urls=urls)


if __name__ == "__main__":
    app.run()
