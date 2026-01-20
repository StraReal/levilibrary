from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from requests_oauthlib import OAuth2Session
import os, uuid

import db_tools.db_reader as dbr
import db_tools.db_inserter as dbi

from database import engine, SessionLocal
from models import Base, User, Book

Base.metadata.create_all(bind=engine)

ALLOWED_DOMAIN = "levi.edu.it"
def is_allowed_email(email: str) -> bool:
    return email.lower().endswith(f"@{ALLOWED_DOMAIN}")

# ---------- OAuth2 config ----------
CLIENT_ID = "782649023-kbhsqahf4nao93cqh5d66bajd6v6jqaa.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8000/auth/callback"
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = ["https://www.googleapis.com/auth/userinfo.email", "openid"]

oauth2_sessions = {}  # temp state storage
sessions = {}  # session_id -> email

app = FastAPI()
frontend = Jinja2Templates(directory="frontend")

from fastapi.staticfiles import StaticFiles

# Mount the static folder
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, session_id: str = Cookie(None)):
    email = sessions.get(session_id)

    if not email:
        # No valid session → redirect to login page
        return RedirectResponse(url="/login")

    # Logged in → render homepage with user info
    return frontend.TemplateResponse(
        "home.html",
        {"request": request, "logged_in": True, "email": email}
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Render the login page with the Google login button.
    """
    return frontend.TemplateResponse("login.html", {"request": request})


@app.get("/login/redirect")
def login_redirect():
    """
    Redirect to Google OAuth page.
    """
    google = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = google.authorization_url(
        AUTHORIZATION_BASE_URL, access_type="offline"
    )

    # Save the session state
    oauth2_sessions[state] = google

    # Redirect user to Google's OAuth page
    return RedirectResponse(authorization_url)


@app.get("/auth/callback")
def callback(response: Response, request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    google = oauth2_sessions.pop(state)

    # Fetch token
    token = google.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, code=code)

    # Fetch user info
    resp = google.get("https://www.googleapis.com/oauth2/v2/userinfo")
    user_info = resp.json()
    email = user_info["email"]

    if is_allowed_email(email) or True:
        # Add user to DB
        db = SessionLocal()
        dbi.add_entry(db, email)
        dbr.print_db(db, "\n=== WITH new entry ===")
        db.close()

        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = email
        response = RedirectResponse(url="/")
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    else:
        return RedirectResponse(url="/loginrejected")


@app.get("/loginrejected", response_class=HTMLResponse)
def login_rejected(request: Request):
    return frontend.TemplateResponse(
        "loginrejected.html", {"request": request}
    )


@app.get("/logout")
def logout(response: Response, session_id: str = Cookie(None)):
    if session_id in sessions:
        sessions.pop(session_id)
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response


@app.get("/borrow")
def borrow_book(request: Request, book_id: int, session_id: str = Cookie(None)):
    email = sessions.get(session_id)
    if not email:
        return RedirectResponse(url="/login")

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    book = db.query(Book).filter(Book.id == str(book_id)).first()

    if not user or not book:
        db.close()
        return {"success": False, "message": "User or book not found"}

    if user.borrowing is not None:
        db.close()
        return {"success": False, "message": "You are already borrowing a book"}

    if book.lent is not None:
        db.close()
        return {"success": False, "message": "Book is already lent"}

    # Borrow the book
    user.borrowing = str(book.id)
    book.lent = str(user.id)
    db.commit()
    db.close()

    return RedirectResponse(url="/")  # or return JSON if using AJAX
