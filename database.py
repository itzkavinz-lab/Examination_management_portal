import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR/ "instance"
DATABASE_PATH = INSTANCE_DIR/ "examination.db"

def get_db_connection():
    INSTANCE_DIR.mkdir(exist_ok =True)
    connection = sqlite3.connect(DATABSE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection