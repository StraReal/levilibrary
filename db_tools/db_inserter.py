import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Email

# Change working directory to parent of this script's folder
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

from db_tools.db_reader import print_db as read_db

DATABASE_URL = "sqlite:///./app.db"

def add_email(db, entry):
    """Add an email to the database if it doesn't already exist."""
    exists = db.query(Email).filter(Email.email == entry).first()
    if exists:
        print(f"\nEmail already exists: {entry}")
    else:
        new_email = Email(email=entry)
        db.add(new_email)
        db.commit()
        print(f"\nEmail added successfully: {entry}")

def main():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    read_db(db, "\n=== BEFORE adding ===")
    email_to_add = input("Enter item: ")
    add_email(db, email_to_add)
    read_db(db, "\n=== AFTER adding ===")
    db.close()

if __name__ == "__main__":
    main()
