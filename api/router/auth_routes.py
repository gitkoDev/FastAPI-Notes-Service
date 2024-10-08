from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from typing import Annotated
from datetime import timedelta

from api.repository.auth_repository import AuthRepository
from api.schemas.user_schemas import CreateUserInput, Token
from helpers.helpers import NotFoundError


router = APIRouter(
    prefix="/auth",
    tags=["Authorization"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserInput) -> dict:
    try:
        user_id = await AuthRepository.create_user(data)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name already exists",
        )
    return {"id": user_id}


@router.post("/token", response_model=Token)
async def get_access_token(
    data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict:
    user = await AuthRepository.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )
    token = AuthRepository.create_access_token(
        user.name, user.id, timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}
