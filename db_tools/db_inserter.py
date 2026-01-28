import os, json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book, AdminLog
from datetime import datetime, timezone
from typing import Literal
PLACEHOLDER_COVER = Path("frontend/static/assets/placeholder_cover.png")

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

LOG_ACTIONS = {
    0: 'unr',
    1: 'add',
    2: 'del',
    3: 'bor',
    4: 'ret',
    5: 'cra',
    6: 'ada',
    7: 'adr',
    8: 'edi',
}
from db_tools.db_reader import print_db as read_db

DATABASE_URL = "sqlite:///./app.db"

SECRETS_PATH = Path("secrets.json")

def update_admin(
    email: str,
    subject: str,
    action: int,
    db) -> bool:
    subject = subject.strip().lower()
    if not subject:
        return False

    if not SECRETS_PATH.exists():
        raise FileNotFoundError("secrets.json not found")

    with SECRETS_PATH.open("r", encoding="utf-8") as f:
        secrets = json.load(f)

    admins = set(e.lower() for e in secrets.get("admin_emails", []))

    if email not in admins:
        return False

    if action == 0:
        if subject in admins:
            return False
        admins.add(subject)
        log_action(db, user_email=email, subject=subject, action=6)

    elif action == 1:
        if subject not in admins:
            return False
        if len(admins) <= 2:
            raise RuntimeError("Refusing to remove last admin")
        admins.remove(subject)
        log_action(db, user_email=email, subject=subject, action=7)
    else:
        return False

    secrets["admin_emails"] = sorted(admins)

    tmp_path = SECRETS_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(secrets, f, indent=2)

    tmp_path.replace(SECRETS_PATH)
    return True

def add_entry(db, entry, user_table=True, author=None, cover=None, category='Unmarked', section=None):
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
        log_action(db, entry, 5)
    else:
        new_entry = Book(title=entry, author=author, cover=cover, lent=None, category=category, section=section)

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
            if cover_path.exists() and cover_path != PLACEHOLDER_COVER:
                try:
                    cover_path.unlink()
                    print(f"Deleted cover file: {cover_path}")
                except Exception as e:
                    print(f"Failed to delete cover file: {cover_path} ({e})")

    db.delete(obj)
    db.commit()
    print(f"\nEntry removed successfully from {table_name} with ID: {entry_id}")

def edit_entry(db, id, title=None, author=None, cover=None, category=None, section=None):
    obj = db.query(Book).filter(Book.id == id).first()
    if not obj:
        print(f"\nEntry not found in Book with ID: {id}")
        return

    if cover and obj.cover != cover:
        old_cover_path = Path("frontend") / obj.cover
        if old_cover_path.exists() and old_cover_path != PLACEHOLDER_COVER:
            try:
                old_cover_path.unlink()
            except Exception as e:
                print(f"Failed to delete old cover: {e}")

    obj.title = title if title is not None else obj.title
    obj.author = author if author is not None else obj.author
    obj.cover = cover if cover is not None else obj.cover
    obj.category = category if category not in (None, "Unmarked") else obj.category
    obj.section = section if section is not None else obj.section

    db.commit()
    print(f"\nEntry edited successfully in Book with ID: {id}")


def log_action(db, user_email: str | None, action: int = 0, subject=None, book=None):
    if action not in LOG_ACTIONS or not LOG_ACTIONS[action]:
        print(f"\n\033[31mLogging action <{action}> invalid, defaulting to 0.\033[0m")
        action = 0

    if book:
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
    elif subject:
        now_utc = datetime.now(timezone.utc)
        log = AdminLog(
            user_email=user_email,
            subject=subject,
            action=LOG_ACTIONS[action],
            timestamp=now_utc
        )

        db.add(log)
        db.commit()

        print(
            f"\nLogging action <{LOG_ACTIONS[action]}> by <{user_email}> towards <{subject}> "
            f"at <{now_utc.isoformat()}> logged."
        )
    else:
        now_utc = datetime.now(timezone.utc)
        log = AdminLog(
            user_email=user_email,
            action=LOG_ACTIONS[action],
            timestamp=now_utc
        )

        db.add(log)
        db.commit()

        print(
            f"\nLogging action <{LOG_ACTIONS[action]}> by <{user_email}> "
            f"at <{now_utc.isoformat()}> logged."
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
