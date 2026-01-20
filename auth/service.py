from sqlalchemy.orm import Session 
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.models import User as UserModel 
from auth.schemas import User as UserSchema, UserCreate
from auth.database import get_db
import bcrypt

SECRET_KEY = "mysecretkey"  # In production, use environment variable!
EXPIRE_MINUTES = 60 * 24 
ALGORITHM = "HS256"

# Password hashing context
# Use bcrypt directly to avoid passlib compatibility issues
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

# Check if there is existing user with the same username or email 
async def existing_user(db: Session, username: str, email: str):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user: 
        return db_user 
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if db_user:
        return db_user
    return None

# Create jwt token
async def create_access_token(id: int, username: str):
    encode = {"sub": username, "id": id}
    expires = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Get current user from token 
async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        
        if username is None or id is None: 
            raise credentials_exception
            
        db_user = db.query(UserModel).filter(UserModel.id == id).first()
        
        if db_user is None:
            raise credentials_exception
            
        return db_user
        
    except JWTError:
        raise credentials_exception

# Create user 
async def create_user(db: Session, user: UserCreate):
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authenticate user (verify username and password)
async def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user by verifying username and password.
    Returns the user if authentication succeeds, None otherwise.
    """
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user