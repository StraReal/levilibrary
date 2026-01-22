from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
    lent = Column(Integer, nullable=True)  # ID of the user who borrowed this book, or None
