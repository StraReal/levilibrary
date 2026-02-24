import sys

from sqlalchemy import create_engine
from models import Base, Book, User, AdminLog

dbs = {
    0: Book,
    1: User,
    2: AdminLog,
}
try:
    database = int(input('Which database to delete? (0: Books, 1: Users, 2: AdminLogs)'))
except ValueError:
    sys.exit('Invalid input')

if database in dbs:
    database = dbs[database]
else:
    sys.exit('Invalid input')

execute = input('Are you sure? This will wipe the entire selected database. Write "CONFIRMDELETE" to confirm.')

if execute != 'CONFIRMDELETE':
    sys.exit()

engine = create_engine("sqlite:///../app.db", echo=False)

Base.metadata.bind = engine

Base.metadata.drop_all(bind=engine, tables=[database.__table__])
Base.metadata.create_all(bind=engine)