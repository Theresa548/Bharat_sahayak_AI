from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

# ------------------ DATABASE ------------------
DATABASE_URL = "mysql+pymysql://root:Theresa%40123@localhost/bharat_sahaayak_ai"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ------------------ MODEL ------------------
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))
    preferred_language = Column(String(20), default="en")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ------------------ APP ------------------
app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ------------------ SCHEMAS ------------------
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ------------------ ROUTES ------------------

# Homepage - auth page
@app.get("/", response_class=HTMLResponse)
def auth_page():
    with open("frontend/auth.html", "r", encoding="utf-8") as f:
        return f.read()

# Signup
@app.post("/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Store plain password (no hashing)
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=data.password
    )
    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User registered successfully"}

# Login
@app.post("/login")
def login_user(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    db.close()
    return {"message": "Login successful", "user_id": user.user_id, "name": user.name}

# Dashboard page
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    file_path = os.path.join("frontend", "dashboard.html")
    if not os.path.exists(file_path):
        return HTMLResponse("<h2>Dashboard page not found. Create dashboard.html in frontend/</h2>", status_code=404)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Optional: separate login/signup pages (not strictly needed if using auth.html)
@app.get("/login-page", response_class=HTMLResponse)
def login_page():
    with open("frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/signup-page", response_class=HTMLResponse)
def signup_page():
    with open("frontend/signup.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/select-document", response_class=HTMLResponse)
def select_document():
    with open("frontend/select_document.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/form", response_class=HTMLResponse)
def apply_form():
    with open("frontend/form.html", encoding="utf-8") as f:
        return f.read()


