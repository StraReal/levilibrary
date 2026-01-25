import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book, AdminLog
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

LOG_ACTIONS = {
    1: 'add',
    2: 'del',
    3: 'bor',
    4: 'ret'
}
from db_tools.db_reader import print_db as read_db

DATABASE_URL = "sqlite:///./app.db"

def add_entry(db, entry, user_table=True, author=None, cover=None):
    entry=entry.strip()
    if not entry: return
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
        new_entry = Book(title=entry, author=author, cover=cover, lent=None)

    db.add(new_entry)
    db.commit()
    print(f"\nEntry added successfully to {table_name}: {entry}")

from pathlib import Path

def remove_entry(db, entry_id, user_table=True):
    if user_table:
        table = User
        table_name = "User"
        obj = db.query(table).filter(User.id == entry_id).first()
    else:
        table = Book
        table_name = "Book"
        obj = db.query(table).filter(Book.id == entry_id).first()

    if not obj:
        print(f"\nEntry not found in {table_name} with ID: {entry_id}")
        return

    if user_table:
        if obj.borrowing:
            book = db.query(Book).filter(Book.id == int(obj.borrowing)).first()
            if book:
                book.lent = None
    else:
        if obj.lent:
            user = db.query(User).filter(User.id == int(obj.lent)).first()
            if user:
                user.borrowing = None

        if obj.cover:
            cover_path = Path("frontend") / obj.cover
            if cover_path.exists():
                try:
                    cover_path.unlink()
                    print(f"Deleted cover file: {cover_path}")
                except Exception as e:
                    print(f"Failed to delete cover file: {cover_path} ({e})")

    db.delete(obj)
    db.commit()
    print(f"\nEntry removed successfully from {table_name} with ID: {entry_id}")

def log_action(db, user_email: str | None, action: int, book=None):
    if action not in LOG_ACTIONS or not LOG_ACTIONS[action]:
        print(f"\n\033[31mLogging action <{action}> invalid.\033[0m")
        return

    now_utc = datetime.now(timezone.utc)

    log = AdminLog(
        user_email=user_email,
        action=LOG_ACTIONS[action],
        book_id=getattr(book, "id", None),
        book_title=getattr(book, "title", None),
        timestamp=now_utc
    )

    db.add(log)
    db.commit()

    print(
        f"\nLogging action <{LOG_ACTIONS[action]}> by <{user_email}> "
        f"on book <{getattr(book, 'title', None)}> "
        f"(id: <{getattr(book, 'id', None)}>) at <{now_utc.isoformat()}> logged."
    )


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
    author = None
    if not user_db:
        author = input("Enter author: ")
    add_entry(db, entry, user_table=user_db, author=author, cover=None)
    read_db(db, user_db,"\n=== AFTER adding ===")
    db.close()

if __name__ == "__main__":
    main()
