from sqlalchemy import Column, Integer, String
from database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
