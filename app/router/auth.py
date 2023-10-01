from datetime import datetime, timedelta
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from app.db import User
from app.userSerializer import userEntity, userResponseEntity
import app.schema as schema
from app.oath import create_access_token, verify_password, get_hashed_password
from app.config import settings
from typing import Annotated

router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(requestUser: schema.UserInDB):
    # Check if user already exist
    user = User.find_one({"email": requestUser.email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exist!!"
        )
    #  Hash the password
    requestUser.password = get_hashed_password(requestUser.password)
    requestUser.created_at = datetime.utcnow()
    requestUser.updated_at = requestUser.created_at
    User.insert_one(jsonable_encoder(requestUser))
    return {"status": "success"}


@router.post("/login", response_model=schema.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Check if the user exist
    db_user = User.find_one({"email": form_data.username})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )
    user = userEntity(db_user)
    # Check if the password is valid
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    # Send both access
    return {"access_token": access_token, "token_type": "bearer"}