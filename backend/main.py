from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# ------------------ DATABASE ------------------
DATABASE_URL = "mysql+pymysql://root:Theresa@123@localhost/bharat_sahaayak_ai"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# ------------------ PASSWORD ------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

# ------------------ MODEL ------------------
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))
    preferred_language = Column(String(20))

# ------------------ APP ------------------
app = FastAPI()

# ------------------ SCHEMA ------------------
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ------------------ ROUTES ------------------
@app.post("/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        preferred_language="en"
    )
    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User registered successfully"}

#Login Page
@app.post("/login")
def login_user(data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user.user_id}

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/login-page", response_class=HTMLResponse)
def login_page():
    with open("frontend/login.html") as f:
        return f.read()
    
#Signup Page
@app.get("/signup-page", response_class=HTMLResponse)
def signup_page():
    with open("frontend/signup.html") as f:
        return f.read()

#Auth file
@app.get("/", response_class=HTMLResponse)
def auth_page():
    with open("frontend/auth.html") as f:
        return f.read()
