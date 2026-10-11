import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR/ "instance"
DATABASE_PATH = INSTANCE_DIR/ "examination.db"

def get_db_connection():
    INSTANCE_DIR.mkdir(exist_ok =True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db():
    INSTANCE_DIR.mkdir(exist_ok=True)
    with get_db_connection() as conn:
        conn.executescript("""
                           CREATE TABLE IF NOT EXISTS users(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               username TEXT NOT NULL UNIQUE,
                               email TEXT NOT NULL UNIQUE,
                               password_hash TEXT NOT NULL,
                                role TEXT NOT NULL
                                check(role IN ('admin','examiner','student')),
                                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                           );
                           CREATE TABLE IF NOT EXISTS students (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               user_id INTEGER NOT NULL UNIQUE,
                               student_id TEXT NOT NULL UNIQUE,
                               name TEXT NOT NULL,
                               phone TEXT,
                               department TEXT,
                               FOREIGN KEY(user_id) REFERENCES users(id)
                               
                           );
                           
                           CREATE TABLE IF NOT EXISTS examiners(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL UNIQUE,
                               examiner_id TEXT NOT NULL UNIQUE,
                               name TEXT  NOT NULL,
                               department TEXT,
                               phone TEXT,
                               status TEXT NOT NULL DEFAULT "pending"
                                CHECK (status in ('pending','approved','inactive')),
                                FOREIGN KEY (user_id) REFERENCES users(id)
                           );
                           CREATE TABLE IF NOT EXISTS courses(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               course_code TEXT NOT NULL UNIQUE,
                               course_name TEXT NOT NULL,
                               description TEXT,
                               status TEXT NOT NULL DEFAULT 'active'
                                CHECK (status IN('active','inactive'))
                           );
                           CREATE TABLE IF NOT EXISTS examinations(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                            course_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            examination_type TEXT NOT NULL
                                CHECK( examination_type IN(
                                   'viva','practical','project_demo','assessment'
                                )),
                                duration_mins INTEGER NOT NULL CHECK(duration_mins > 0 ),
                                max_marks REAL NOT NULL CHECK (max_marks > 0),
                                slot_creation_start TEXT NOT NULL , 
                                slot_creation_end TEXT NOT NULL,
                                booking_start TEXT NOT NULL,
                                booking_end TEXT NOT NULL,
                                status TEXT NOT NULL default 'draft'
                                    check(status in ('draft','open','closed','completed')),
                                    FOREIGN KEY( course_id) REFERENCES courses(id)
                               
                           );
                           CREATE TABLE IF NOT EXISTS slots(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               examination_id INTEGER NOT NULL,
                               examiner_id INTEGER NOT NULL,
                               date TEXT NOT NULL,
                               start_time TEXT NOT NULL,
                               end_time TEXT NOT NULL,
                               capacity INTEGER NOT NULL CHECK(capacity > 0),
                               available_seats INTEGER NOT NULL CHECK (
                                   available_seats > 0 AND available_seats < capacity
                               ),
                               status TEXT NOT NULL DEFAULT 'available' CHECK(status IN(
                                   'available', 'full', 'cancelled' , 'completed'
                               )),
                               FOREIGN KEY(examination_id) REFERENCES examinations(id),
                               FOREIGN KEY(examiner_id) REFERENCES  examiners(id),
                               CHECK(start_time < end_time)
                            
                           );
                           CREATE TABLE IF NOT EXISTS bookings(
                               id  INTEGER PRIMARY KEY AUTOINCREMENT,
                               student_id INTEGER NOT NULL,
                               examination_id INTEGER NOT NULL,
                               slot_id INTEGER NOT NULL,
                               booking_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                               status TEXT NOT NULL DEFAULT 'booked'
                                    CHECK( status IN ( 'booked', 'cancelled','completed')),
                                    FOREIGN KEY (student_id) REFERENCES students(id),
                                    FOREIGN KEY (examination_id) REFERENCES examinations(id),
                                    FOREIGN KEY (slot_id) REFERENCES slots(id),
                                    UNIQUE(student_id,examination_id)
                               
                           );
                           CREATE TABLE IF NOT EXISTS rubrics(
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                examination_id INTEGER NOT NULL,
                                criterion_name TEXT NOT NULL,
                                max_marks REAL NOT NULL CHECK( max_marks > 0),
                                weightage REAL NOT NULL DEFAULT 0
                                    CHECK(weightage >= 0 AND weightage <=100),
                                    description TEXT,
                                    FOREIGN KEY (examination_id) REFERENCES examinations(id)
                           );
                           
                           CREATE TABLE IF NOT EXISTS evaluations (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               booking_id INTEGER NOT NULL UNIQUE,
                               total_marks REAL NOT NULL DEFAULT 0 CHECK(total_marks >= 0),
                               remarks TEXT,
                               status TEXT NOT NULL DEFAULT 'draft'
                                    CHECK(status IN ('draft','submitted','published')),
                                    submitted_At TEXT,
                                    FOREIGN KEY (booking_id) REFERENCES bookings(id)
                           );
                           CREATE TABLE IF NOT EXISTS evaluation_items (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               evaluation_id INTEGER NOT NULL,
                               rubric_id INTEGER NOT NULL,
                               marks REAL NOT NULL CHECK (marks >= 0),
                               FOREIGN KEY (evaluation_id) REFERENCES evaluations(id),
                               FOREIGN KEY (rubric_id) REFERENCES rubrics(id),
                               UNIQUE (evaluation_id,rubric_id)
                           );
                           
                           CREATE INDEX IF NOT EXISTS idx_examination_course ON examinations(course_id);
                           CREATE INDEX IF NOT EXISTS idx_slots_examination on slots(examination_id);
                           CREATE INDEX IF NOT EXISTS idx_slots_examiner on slots(examiner_id);
                           CREATE INDEX IF NOT EXISTS idx_bookings_student ON bookings(student_id);
                           CREATE INDEX IF NOT EXISTS idx_bookings_slot ON bookings(slot_id);
                           
                           
                           
                           
                          """ )
        print("DATABASE INITIATED SUCESSFULLY")
        print(f"Database Location: {DATABASE_PATH}")
        
if __name__ =="__main__":
    init_db()