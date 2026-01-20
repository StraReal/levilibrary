import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book

# Change working directory to parent of this script's folder
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

from db_tools.db_reader import print_db as read_db

DATABASE_URL = "sqlite:///./app.db"

def add_entry(db, entry, user_table=True):
    """
    Add an entry to the database.
    If user_table=True, adds to Users table.
    Otherwise, adds to Book table.
    Optionally, you can specify borrowing_id:
      - If adding a user, borrowing_id is the book they borrow
      - If adding a book, borrowing_id is the user who borrowed it
    """
    if user_table:
        table = User
        table_name = "User"
        column = "email"
    else:
        table = Book
        table_name = "Book"
        column = "title"

    exists = db.query(table).filter(getattr(table, column) == entry).first()
    if exists:
        print(f"\nEntry already exists in {table_name}: {entry}")
        return

    if user_table:
        new_entry = User(email=entry, borrowing=None)
    else:
        new_entry = Book(title=entry, lent=None)

    db.add(new_entry)
    db.commit()
    print(f"\nEntry added successfully to {table_name}: {entry}")

def main():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    user_db = None
    while user_db not in ('U', 'B'):
        user_db = input("\nUsers (U) or Books (B) Database?: ")
    if user_db == 'U':
        user_db = True
    else:
        user_db = False

    read_db(db, user_db,"\n=== BEFORE adding ===")
    entry = input("Enter item: ")
    add_entry(db, entry, user_table=user_db)
    read_db(db, user_db,"\n=== AFTER adding ===")
    db.close()

if __name__ == "__main__":
    main()
