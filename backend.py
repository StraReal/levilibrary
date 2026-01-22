from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from requests_oauthlib import OAuth2Session
import time
import os, uuid

import db_tools.db_reader as dbr
import db_tools.db_inserter as dbi

from database import engine, SessionLocal
from models import Base, User, Book

Base.metadata.create_all(bind=engine)

# ---------- OAuth2 config ----------
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SECRETS_PATH = BASE_DIR / "secrets.json"

TEMPLATE = {
    "CLIENT_ID": "your-google-client-id.apps.googleusercontent.com",
    "CLIENT_SECRET": "your-google-client-secret",
    "REDIRECT_URI": "http://localhost:8000/auth/callback"
}

if not SECRETS_PATH.exists():
    # Create a template to guide the user
    with open(SECRETS_PATH, "w", encoding="utf-8") as f:
        json.dump(TEMPLATE, f, indent=4)

    raise FileNotFoundError(
        f"\nMissing secrets.json\n"
        f"A template file has been created at:\n"
        f"  {SECRETS_PATH}\n\n"
        f"Fill it with your real credentials and restart the application.\n"
        f"Do NOT commit this file to Git."
    )

with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["CLIENT_ID"]
CLIENT_SECRET = secrets["CLIENT_SECRET"]
REDIRECT_URI = secrets["REDIRECT_URI"]


SESSION_TTL = 3600
oauth2_sessions = {}  # temp state storage
sessions = {}  # session_id -> email

app = FastAPI()
frontend = Jinja2Templates(directory="frontend")

from fastapi.staticfiles import StaticFiles

# Mount the static folder
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

ALLOWED_DOMAIN = "levi.edu.it"
def is_allowed_email(email: str) -> bool:
    return email.lower().endswith(f"@{ALLOWED_DOMAIN}")

def get_session_email(session_id: str):
    if not session_id:
        return None

    session = sessions.get(session_id)

    if not session:
        return None

    # Expired?
    if time.time() - session["created"] > SESSION_TTL:
        sessions.pop(session_id, None)
        return None

    return session["email"]

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, session_id: str = Cookie(None)):
    email = get_session_email(session_id)

    if not email:
        # No valid session → redirect to login page
        print('Redirecting to /login,', session_id)
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

    print(state, google)
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
        dbr.print_db(db, True,"\n=== WITH new entry ===")
        db.close()

        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "email": email,
            "created": time.time()
        }
        response = RedirectResponse(url="/")
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=SESSION_TTL,
            httponly=True,
            secure=False,  # enable when HTTPS
            samesite="lax"
        )

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
    email = get_session_email(session_id)

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
