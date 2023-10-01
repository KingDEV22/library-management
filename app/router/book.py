from fastapi import APIRouter, status, Depends, HTTPException, Query, Header
import app.schema as schema
from app.oath import jwt_authenticate
from fastapi.encoders import jsonable_encoder
from typing import List
from app.schema import UserSchema
from app.db import Book, IssuedBook
from bson import ObjectId
from datetime import datetime
from app.permission import PermissionChecker
router = APIRouter()


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
)
async def add_books(
    requestBooks: List[schema.Book],
    current_user: UserSchema = Depends(PermissionChecker(required_roles=['admin']))
):
    # Extract ISBNs from the request books to check for existing books
    isbns = [book.isbn for book in requestBooks]
    # Find existing books with matching ISBNs
    existing_books = Book.find({"isbn": {"$in": isbns}})
    existing_isbns = set(book["isbn"] for book in existing_books)
    print(len(existing_isbns))
    if len(existing_isbns) == len(requestBooks):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Books already exist!!"
        )

    # Filter out books that already exist
    books_to_add = [book for book in requestBooks if book.isbn not in existing_isbns]
    result = Book.insert_many([jsonable_encoder(book) for book in books_to_add])
    if result.inserted_ids:
        return {
            "message": "Books added successfully",
            "added_books": len(result.inserted_ids),
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add books.",
        )


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
)
async def add_book(
    requestBook: schema.Book, current_user: UserSchema = Depends(PermissionChecker(required_roles=['admin']))
):
    book: schema.Book = Book.find_one({"isbn": requestBook.isbn})
    if book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Book already exist!!"
        )

    result = Book.insert_one(jsonable_encoder(requestBook))
    if result.inserted_id:
        return {"message": "Book added successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add book!!",
        )


@router.put(
    "/update",
    status_code=status.HTTP_201_CREATED,
)
async def update_book(
    requestBook: schema.Book,  current_user: UserSchema = Depends(PermissionChecker(required_roles=['admin']))
):
    book: schema.Book = Book.find_one({"isbn": requestBook.isbn})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found!!"
        )
    # Update the fields of the existing book with the new values
    book["title"] = requestBook.title
    book["author"] = requestBook.author
    book["published_year"] = requestBook.published_year
    book["quantity"] = requestBook.quantity

    # Perform the update
    result = Book.update_one({"_id": ObjectId(book["_id"])}, {"$set": book})
    if result.modified_count == 1:
        return {"message": "Book updated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book!!",
        )


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    requestBook: schema.Book,  current_user: UserSchema = Depends(PermissionChecker(required_roles=['admin'])),
):
    result = None
    if requestBook.isbn:
        result = Book.delete_one({"isbn": requestBook.isbn})
    elif requestBook.author:
        result = Book.delete_many({"author": requestBook.author})
    elif requestBook.title:
        result = Book.delete_many({"title": requestBook.title})

    if result.deleted_count < 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book!!",
        )


@router.get("/get/{isbn}", response_model=schema.Book)
async def get_book(isbn: str):
    book = Book.find_one({"isbn": isbn})
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@router.get("/all", response_model=List[schema.Book])
async def get_all_books(
    page: int = Query(1, ge=1), page_size: int = Query(5, ge=1, le=100)
):
    skip = (page - 1) * page_size
    books = Book.find().skip(skip).limit(page_size)
    return books


@router.get("/search", response_model=List[schema.Book])
async def search_book(
    query: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    skip = (page - 1) * page_size
    books = (
        Book.find(
            {
                "$or": [
                    {"title": query},
                    {"author": query},
                    {"isbn": query},
                    {"published_year": int(query)},
                ]
            }
        )
        .skip(skip)
        .limit(page_size)
    )
    return books


@router.get("/personalize", response_model=List[schema.Book])
async def recommend_books( current_user: UserSchema = Depends(PermissionChecker(required_roles=['user','admin']))):
    get_issue_history = IssuedBook.find({"user_id": current_user["email"]})
    user_interests = set()
    for record in get_issue_history:
        book = Book.find_one({"isbn": record["book_id"]})
        user_interests.add(book["author"])

    # Recommend books based on identified interests
    recommended_books = Book.find({"author": {"$in": list(user_interests)}}).limit(15)
    return recommended_books


@router.post("/borrow", response_model=schema.BookIssueResponse)
async def borrow_book(
    borrowRequest: schema.BookRequest,
    current_user: UserSchema = Depends(PermissionChecker(required_roles=['user','admin'])),
):
    # Check the limit of issued books for the user
    issued_books_count: int = IssuedBook.count_documents(
        {"user_id": current_user["email"]}
    )
    if issued_books_count == 3:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have reached your maximum issue limit!!!!",
        )
    book: schema.Book = Book.find_one({"isbn": borrowRequest.isbn})
    if not book or book["quantity"] < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sorry the book is not available at the time. Please come later.",
        )

    already_issued_book = IssuedBook.find_one(
        {
            "user_id": current_user["email"],
            "book_id": borrowRequest.isbn,
            "returned_book": False,
        }
    )
    if already_issued_book:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have already issued the book. Same book not allowed!!!",
        )

    # Decrement the book quantity
    quantity: int = book["quantity"] - 1
    book["quantity"] = quantity
    # Update the book's quantity
    Book.update_one({"isbn": borrowRequest.isbn}, {"$set": {"quantity": quantity}})
    # Create an entry in IssuedBook collection
    book_issue = {
        "user_id": current_user["email"],
        "book_id": borrowRequest.isbn,
        "borrow_date": datetime.utcnow(),
        "returned_book": False,
    }
    result = IssuedBook.insert_one(jsonable_encoder(book_issue))
    if result.inserted_id:
        return book_issue
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow book!!",
        )


@router.post("/return")
async def return_book(
    returnRequest: schema.BookRequest,
     current_user: UserSchema = Depends(PermissionChecker(required_roles=['user','admin'])),
):
    book: schema.Book = Book.find_one({"isbn": returnRequest.isbn})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sorry the book is not available. Enter a valid book isbn number!!!",
        )
    already_issued_book = IssuedBook.find_one(
        {
            "user_id": current_user["email"],
            "book_id": returnRequest.isbn,
            "returned_book": True,
        }
    )
    if already_issued_book:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have already returned the book. not allowed!!!",
        )
    result = IssuedBook.update_one(
        {"user_id": current_user["email"], "book_id": returnRequest.isbn},
        {"$set": {"return_date": datetime.utcnow(), "returned_book": True}},
    )
    if result.modified_count:
        # Decrement the book quantity
        quantity: int = book["quantity"] + 1
        book["quantity"] = quantity
        # Update the book's quantity
        Book.update_one({"isbn": returnRequest.isbn}, {"$set": {"quantity": quantity}})
        return {"message": "Returned book id: " + book["isbn"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to return book!!",
        )
