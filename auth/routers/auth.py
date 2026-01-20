from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.schemas import UserCreate, User as UserSchema, LoginRequest
from auth.database import get_db
from auth.models import User as UserModel
from auth.service import (
    create_user,
    existing_user,
    create_access_token,
    authenticate_user,
    get_current_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    db_user = await existing_user(db, user.username, user.email)

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    return await create_user(db, user)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    user = await authenticate_user(
        db,
        credentials.username,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = await create_access_token(user.id, user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }



@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Get currently logged-in user
    """
    return current_user


@router.get("/protected")
async def protected_route(current_user: UserModel = Depends(get_current_user)):
    """
    Example protected endpoint
    """
    return {
        "message": f"Hello {current_user.username}! This is a protected route.",
        "user_id": current_user.id,
        "email": current_user.email
    }
