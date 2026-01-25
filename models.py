from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    borrowing = Column(Integer, nullable=True)  # ID of the book user is borrowing, or None

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    cover = Column(String, nullable=False)
    lent = Column(Integer, nullable=True)

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=True)
    action = Column(String, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    book_title = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())