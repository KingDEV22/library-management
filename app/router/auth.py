from datetime import datetime, timedelta
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import logging

from app.db import User
import app.schema as schema
from app.oath import create_access_token, verify_password, get_hashed_password
from app.config import settings


# Set up a logger with basic configuration
logging.basicConfig(level=logging.INFO)


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(requestUser: schema.UserInDB):
    # Check if user already exist
    user = User.find_one({"email": requestUser.email})
    if user:
        logging.error("User already present!!!")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email: " + requestUser.email + " already exist!!",
        )
    
    # Hash the password
    requestUser.password = get_hashed_password(requestUser.password)
    logging.info("Passowrd hashed.")

    requestUser.created_at = datetime.utcnow()
    requestUser.updated_at = requestUser.created_at

    # insert user in the db
    result = User.insert_one(jsonable_encoder(requestUser))
    if result.inserted_id:
        logging.info("User created..")
        return {"status": "success"}
    else:
        logging.error("Falied to created user!!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user: " + requestUser.email,
        )


@router.post("/login", response_model=schema.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Check if the user exist
    db_user = User.find_one({"email": form_data.username})
    if not db_user:
        logging.error("User not found!!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email!!!",
        )
    
    # Check if the password is valid
    if not verify_password(form_data.password, db_user["password"]):
        logging.error("User passowrd not correct!!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Password!!!",
        )
    
    logging.info(msg="Password and email verified...")

    # Create access token
    access_token = create_access_token(
        data={"sub": db_user["email"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN),
    )
    
    if access_token:
        # send token
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        logging.error("Failed to generate token!!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate token for user: " + form_data.username,
        )
