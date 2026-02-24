import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, Column, text
from sqlalchemy.orm import sessionmaker
from models import Base, User, Book, AdminLog

BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)  # creates missing tables, not columns

def add_missing_columns(table_cls):
    inspector = inspect(engine)
    table_name = table_cls.__tablename__
    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]

    with engine.begin() as conn:
        for col in table_cls.__table__.columns:
            if col.name not in existing_columns:
                if col.type.python_type == int:
                    col_type = "INTEGER"
                elif col.type.python_type == float:
                    col_type = "REAL"
                elif col.type.python_type == str:
                    col_type = "TEXT"
                elif col.type.python_type == bool:
                    col_type = "INTEGER"
                else:
                    col_type = "TEXT"

                # Make the column nullable for SQLite; we’ll populate it later
                nullable = ""  # remove NOT NULL here
                default = f" DEFAULT {col.default.arg}" if col.default is not None else ""
                sql = f'ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type} {nullable}{default}'.strip()
                print(f"Adding column: {sql}")
                conn.execute(text(sql))

def migrate_authors():
    with engine.begin() as conn:
        inspector = inspect(engine)
        table_name = Book.__tablename__
        columns = [c['name'] for c in inspector.get_columns(table_name)]

        # Add authorn and authors if missing
        if "authorn" not in columns:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN authorn TEXT"))
        if "authors" not in columns:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN authors TEXT"))

        # Populate authorn/authors from old author column
        books = conn.execute(text(f"SELECT id, author FROM {table_name}")).fetchall()
        for book_id, author_full in books:
            if author_full:
                parts = author_full.split()
                authorn = parts[0]
                authors = " ".join(parts[1:]) if len(parts) > 1 else ""
                conn.execute(
                    text(f"UPDATE {table_name} SET authorn = :authorn, authors = :authors WHERE id = :id"),
                    {"authorn": authorn, "authors": authors, "id": book_id}
                )

        if "author" in columns:
            print("WARNING: SQLite cannot drop the 'author' column automatically. Drop manually or recreate the table.")

def print_db(db, table: int = 0, message: str = ''):
    if message:
        print(message)

    if table==0:
        table = User
        empty_msg = "No users in the database."
        header = "id | email | borrowing"
    elif table==1:
        table = Book
        empty_msg = "No books in the database."
        header = "id | title | author | category | section | cover | lent"
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
            print(f"{e.id} | {e.title} | {e.authorn} {e.authors} | {e.category} | {e.section} | {e.cover} | {e.lent}")
        elif table==AdminLog:
            print(f"{e.id} | {e.user_email} | {e.action} | {e.book_id} | {e.book_title} | {e.subject} | {e.timestamp}")

def main():
    db = SessionLocal()
    for table_cls in [User, Book, AdminLog]:
        add_missing_columns(table_cls)

    # Migrate old author column
    migrate_authors()

    print_db(db, 0, message="\n=== USERS DB ===")
    print_db(db, 1, message="\n=== BOOKS DB ===")
    print_db(db, 2, message="\n=== ADMINS DB ===")
    db.close()

if __name__ == "__main__":
    main()
