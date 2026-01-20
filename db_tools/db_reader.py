import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Email

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

def print_db(db, message: str = ''):
    """Print all emails in the database."""
    if message:
        print(message)
    emails = db.query(Email).all()
    if not emails:
        print("No emails in the database.")
        return
    for e in emails:
        print(f"id={e.id} | email={e.email}")

def main():
    db = SessionLocal()
    print_db(db, "\n=== DATABASE ===")
    db.close()

if __name__ == "__main__":
    main()
