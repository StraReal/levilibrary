from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from db_tools import db_inserter as dbi, db_reader as dbr
from database import engine, SessionLocal
from models import Base, Email

Base.metadata.create_all(bind=engine)

app = FastAPI()
frontend = Jinja2Templates(directory="frontend")


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    return frontend.TemplateResponse(
        "index.html", {"request": request}
    )


@app.post("/submit")
def submit_email(email: str = Form(...)):
    db = SessionLocal()

    dbi.add_email(db, email)
    dbr.print_db(db, "\n=== WITH new entry ===")

    db.close()
    return RedirectResponse("/", status_code=303)
