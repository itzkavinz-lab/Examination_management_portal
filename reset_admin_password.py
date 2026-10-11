import sqlite3
import getpass
from werkzeug.security import generate_password_hash

DB_PATH ="instance/examination.db"
USERNAME = "24f3003047"
new_password = getpass.getpass("Enter a new Admin password: ")
confirm_password = getpass.getpass("Confirm the new PAssword: ")
if(len(new_password)<12):
    raise SystemExit("Use a password with at least 12 characters. ")

if new_password !=confirm_password:
    raise SystemExit("Password do not match. ") 

with sqlite3.connect(DB_PATH) as conn:
    user =conn.execute("SELECT id from users WHERE username = ? AND role = ?",
        (USERNAME, "admin")).fetchone()
    if not user:
         raise SystemExit("Admin Account not found. ")
    password_hash = generate_password_hash(new_password)
            
    conn.execute( 
        "UPDATE users SET password_hash = ? WHERE id =?",
        (password_hash,user[0])
    )
    print("Admin password updated sucessfully ")
            
    