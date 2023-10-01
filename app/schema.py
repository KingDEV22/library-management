from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserSchema(BaseModel):
    name: str
    email: str
    role: list[str] | None = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class UserInDB(UserSchema):
    password: str


class Login(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str


class Book(BaseModel):
    isbn: str = ""
    title: str = ""
    author: str = ""
    published_year: int = 0
    quantity: int = 0

class BookRequest(BaseModel):
    isbn: str = ""

class IssuedBook(BaseModel):
    user_id: str = ""
    book_id: str = ""
    borrow_date: datetime | None = None
    return_date: datetime | None = None
    returned_book: bool = False

class BookIssueResponse(BaseModel):
    user_id: str = ""
    book_id: str = ""
    borrow_date: datetime | None = None


# class UserResponse(BaseModel):
#     status: str
#     user: UserResponseSchema
