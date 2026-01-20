from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def check_borrowability(db, user_id: int, book_id: int) -> bool:
    """Return True if the book is available and the user is not borrowing another."""
    user = db.query(User).filter(User.id == user_id).first()
    book = db.query(Book).filter(Book.id == book_id).first()

    if not user or not book:
        return False

    print(user.borrowing, book.lent)
    return user.borrowing is None and book.lent is None

def borrow(db, user_id: int, book_id: int) -> bool:
    """Borrow a book: set book.lent = user_id and user.borrowing = book_id."""
    if not check_borrowability(db, user_id, book_id):
        print("Cannot borrow: either user is already borrowing or book is lent.")
        return False

    user = db.query(User).filter(User.id == user_id).first()
    book = db.query(Book).filter(Book.id == book_id).first()

    book.lent = user.id
    user.borrowing = book.id

    db.commit()
    print(f"User {user_id} borrowed book {book_id}.")
    return True


def return_book(db, user_id: int, book_id: int) -> bool:
    """Return a book: reset book.lent and user.borrowing to None."""
    user = db.query(User).filter(User.id == user_id).first()
    book = db.query(Book).filter(Book.id == book_id).first()

    if not user or not book:
        print("User or book not found.")
        return False

    if book.lent != user.id or user.borrowing != book.id:
        print("Mismatch: cannot return a book that is not borrowed by this user.")
        return False

    book.lent = None
    user.borrowing = None
    db.commit()
    print(f"User {user_id} returned book {book_id}.")
    return True


# ===== Example usage =====
if __name__ == "__main__":
    db = SessionLocal()
    action = None
    while action not in ('b', 'r'):
        action = input("Action: borrow or return? (b/r): ")
    # IDs to test
    uid = int(input('Enter user ID: '))
    bid = int(input('Enter book ID: '))

    print("Can borrow?", check_borrowability(db, uid, bid))

    if action == 'b':
        borrow(db, uid, bid)
    else:
        return_book(db, uid, bid)
    db.close()
