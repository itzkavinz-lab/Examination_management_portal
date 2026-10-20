from flask import render_template ,Flask,request,redirect,url_for,session,flash
import os
from werkzeug.security import check_password_hash,generate_password_hash
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
        with get_db_connection()as conn:
            total_students = conn.execute(
                "SELECT COUNT(*) FROM students"
            ).fetchone()[0]
            total_examiners = conn.execute(
                "SELECT COUNT(*) FROM examiners"
            ).fetchone()[0]
            total_courses = conn.execute(
                "SELECT COUNT(*) FROM courses"
            ).fetchone()[0]
            total_examinations = conn.execute(
                "SELECT COUNT(*) FROM examinations"
            ).fetchone()[0]
            
            return render_template(
                "admin_dashboard.html",total_students=total_students, total_examiners=total_examiners,total_courses=total_courses,total_examinations=total_examinations)
            



@app.route("/admin/examiners", methods =["GET","POST"])
def manage_examiners():
    if session.get("role")!="admin":
        return redirect(url_for("login"))
    
    error = None
    success = None
    if request.method == "POST" or request.method=="GET":
        
        examiner_id = request.form.get("examiner_id","").strip()
        name =request.form.get("name","").strip()
        username =request.form.get("username","").strip()
        email = request.form.get("email","").strip()
        password =request.form.get("password","")
        department = request.form.get("department","").strip()
        phone = request.form.get("phone","").strip()
        
        if not all([examiner_id,name,username,password,email]):
            error = "Please fill in all required fields."
        else:
            password_hash = generate_password_hash(password)
            try:
                with get_db_connection() as conn:
                    cursor = conn.execute(
                        """
                        INSERT INTO users( username,email,password_hash,role)
                        VALUES (?,?,?,?)
                        """,(username,email,password_hash,"examiner"))
                    user_id = cursor.lastrowid
                    conn.execute("""
                                 INSERT INTO examiners(user_id,examiner_id,name,department,phone)
                                VALUES(?,?,?,?,?)
                                """,(user_id,examiner_id,name,department or None, phone or None))
                    success = "Examiner registered sucessfully"
            except sqlite3.IntegrityError:
                error = (
                    "Registration fqailed. The userame , email, or "
                    "examiner ID may already exis. "
                )
        with get_db_connection() as conn:
            examiners = conn.execute(
                    """SELECT e.id,e.examiner_id,e.name,e.department,e.phone,e.status,u.username,u.email
                    FROM examiners AS e
                    JOIN users As u on e.user_id = u.id
                    ORDER BY e.id DESC
                    """).fetchall()
        if success:
            flash(success, "success")
        else:
            flash(error, "danger")
            
    return render_template(
                "admin_examiners.html",
                examiners = examiners,
                error = error,
                success =success
    )      
            
        
@app.route("/admin/examiners/<int:examiner_id>/status", methods=["POST"])
def update_examiner_status(examiner_id):
    if session.get("role")!="admin":
        return redirect(url_for("login"))
    
    new_status = request.form.get("status","")
    allowed_status={"approved","inactive"}
    if new_status not in allowed_status:
        flash("invalid examiner satus.","danger")
        return redirect(url_for("manage_examiners"))
    
    with get_db_connection() as conn:
        examiner = conn.execute(
            "SELECT id,status FROM examiners WHERE id = ?", (examiner_id,)
        ).fetchone()
        
        if examiner is None:
            flash("Examiner is not found","danger")
        elif examiner["status"] == new_status:
            flash("Examiner already has this status", "danger")
        else:
            conn.execute(
                "UPDATE examiners SET status=? WHERE id=?",
                (new_status,examiner_id)
            )
            flash(
                f"Examiner status changed to {new_status}.","success"
            )
    return redirect(url_for("manage_examiners"))
@app.route("/logout",methods =["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))
  
@app.route("/test-layout")
def test_layout():
    return render_template("base.html")
         

if __name__== "__main__":
    app.run(debug = True)