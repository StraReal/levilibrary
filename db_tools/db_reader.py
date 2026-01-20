import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

def print_db(db, user_table: bool = True, message: str = ''):
    """
    Print all entries in the database.
    If user_table=True, prints all users.
    If user_table=False, prints all books.
    """
    if message:
        print(message)

    if user_table:
        table = User
        empty_msg = "No users in the database."
        header = "id | email | borrowing"
    else:
        table = Book
        empty_msg = "No books in the database."
        header = "id | title | lent"

    entries = db.query(table).all()
    if not entries:
        print(empty_msg)
        return

    print(header)
    for e in entries:
        if user_table:
            print(f"{e.id} | {e.email} | {e.borrowing}")
        else:
            print(f"{e.id} | {e.title} | {e.lent}")

def main():
    db = SessionLocal()
    print_db(db, True, message="\n=== USERS DB ===")
    print_db(db, False, message="\n=== BOOKS DB ===")
    db.close()

if __name__ == "__main__":
    main()
