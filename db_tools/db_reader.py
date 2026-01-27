import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book, AdminLog

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

def print_db(db, table: int = 0, message: str = ''):
    """
    Print all entries in the database.
    If user_table=True, prints all users.
    If user_table=False, prints all books.
    """
    if message:
        print(message)

    if table==0:
        table = User
        empty_msg = "No users in the database."
        header = "id | email | borrowing"
    elif table==1:
        table = Book
        empty_msg = "No books in the database."
        header = "id | title | author | cover | lent"
    elif table==2:
        table = AdminLog
        empty_msg = "No logs in the database."
        header = "id | email | action | book_id | book_title | subject | timestamp"
    else:
        print("Invalid table")
        return

    entries = db.query(table).all()
    if not entries:
        print(empty_msg)
        return

    print(header)
    for e in entries:
        if table==User:
            print(f"{e.id} | {e.email} | {e.borrowing}")
        elif table==Book:
            print(f"{e.id} | {e.title} | {e.author} | {e.cover} |{e.lent}")
        elif table==AdminLog:
            print(f"{e.id} | {e.user_email} | {e.action} | {e.book_id} |{e.book_title} | {e.subject} | {e.timestamp}")
        else:
            print("Invalid table")

def main():
    db = SessionLocal()
    print_db(db, 0, message="\n=== USERS DB ===")
    print_db(db, 1, message="\n=== BOOKS DB ===")
    print_db(db, 2, message="\n=== ADMINS DB ===")
    db.close()

if __name__ == "__main__":
    main()
