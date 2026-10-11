from flask import render_template ,Flask,request,redirect,url_for,session
import os
from werkzeug.security import check_password_hash
from database import get_db_connection

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "SET the flask_Secret_keh environment before running the app"
    )

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        with get_db_connection() as conn:
            user = conn.execute(
    """
    SELECT id,username,password_hash,role
    FROM users
    WHERE username= ?
    """,
        (username,)).fetchone()
        if user and check_password_hash(user["password_hash"],password):
            if(user["role"]=="admin"):
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                return redirect(url_for("admin_dashboard"))
            error = "This login is only for admin"
        else:
            error = "Invalid username or password"
    return render_template("login.html",error=error)
     
@app.route("/admin")
def admin_dashboard():
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return render_template("admin_dashboard.html")
    
@app.route("/logout",methods =["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))
  
@app.route("/test-layout")
def test_layout():
    return render_template("base.html")
         

if __name__== "__main__":
    app.run(debug = True)