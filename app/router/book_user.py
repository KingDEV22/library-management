from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from typing import List
import logging
from datetime import datetime

import app.schema as schema
from app.db import Book, IssuedBook
from app.permission import PermissionChecker

router = APIRouter()

# Set up a logger with basic configuration
logging.basicConfig(level=logging.INFO)


@router.get("/all", response_model=List[schema.Book])
async def get_all_books(
    page: int = Query(1, ge=1), page_size: int = Query(5, ge=1, le=100)
):
    # set the current page
    skip = (page - 1) * page_size

    # fetch based on page number and page size
    books = Book.find().skip(skip).limit(page_size)

    if not books:
        logging.error("No books found in the db!!!!")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No books present!!!!",
        )
    else:
        logging.info("Books found..")
        return books


@router.get("/search", response_model=List[schema.Book])
async def search_book(
    query: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    # set the current page
    skip = (page - 1) * page_size

    # find books based on search query
    books = (
        Book.find(
            {
                "$or": [
                    {"title": query},
                    {"author": query},
                    {"isbn": query}
                ]
            }
        )
        .skip(skip)
        .limit(page_size)
    )
    if not books:
        logging.error("No books found in the db!!!!")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No books present!!!!",
        )
    else:
        logging.info("Books found..")
        return books


@router.get("/personalize", response_model=List[schema.Book])
async def recommend_books(
    current_user: schema.UserSchema = Depends(
        PermissionChecker(required_roles=["user", "admin"])
    )
):
    # get user issued booked history
    get_issue_history = IssuedBook.find({"user_id": current_user["email"]})
    user_interests = set()

    # add unique authors name for recommendations
    for record in get_issue_history:
        book = Book.find_one({"isbn": record["book_id"]})
        user_interests.add(book["author"])

    # search books based on identified interests
    recommended_books = Book.find({"author": {"$in": list(user_interests)}}).limit(15)
    logging.info("Recommending books based on  interests..")
    return recommended_books


@router.post("/borrow", response_model=schema.BookIssueResponse, status_code=status.HTTP_201_CREATED)
async def borrow_book(
    borrowRequest: schema.BookRequest,
    current_user: schema.UserSchema = Depends(
        PermissionChecker(required_roles=["user", "admin"])
    ),
):
    # Check the limit of issued books for the user
    issued_books_count: int = IssuedBook.count_documents(
        {"user_id": current_user["email"]}
    )
    if issued_books_count == 3:
        logging.error("Reached borrowed books limit 3. !!!")
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have reached your maximum issue limit !!!!",
        )

    # check for the availabiltiy of books in the db
    book: schema.Book = Book.find_one({"isbn": borrowRequest.isbn})
    if not book or book["quantity"] < 1:
        logging.error("Book is not available")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sorry the book is not available at the time. Please come later.",
        )

    # check if the book is already issued
    already_issued_book = IssuedBook.find_one(
        {
            "user_id": current_user["email"],
            "book_id": borrowRequest.isbn,
            "returned_book": False,
        }
    )
    if already_issued_book:
        logging.error("Already Issued Date: " + already_issued_book["borrow_date"])
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have already issued the book."
            + "Issued Date: "
            + already_issued_book["borrow_date"]
            + " Same book not allowed!!!",
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
        logging.info("Book issued..")
        return book_issue
    else:
        logging.error("Failed to issue book..")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow book!!",
        )


@router.post("/return")
async def return_book(
    returnRequest: schema.BookRequest,
    current_user: schema.UserSchema = Depends(
        PermissionChecker(required_roles=["user", "admin"])
    ),
):
    # check if the book exist in db
    book: schema.Book = Book.find_one({"isbn": returnRequest.isbn})
    if not book:
        logging.error("Book is not present")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sorry the book is not available. Enter a valid book isbn number!!!",
        )
    # check if the book is not returned already
    already_issued_book = IssuedBook.find_one(
        {
            "user_id": current_user["email"],
            "book_id": returnRequest.isbn,
            "returned_book": True,
        }
    )
    if already_issued_book:
        logging.error("already returned the book")
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You have already returned the book."+ "Returned Date: " + already_issued_book['return_date'] +"not allowed!!!",
        )
    
    # update the return date
    result = IssuedBook.update_one(
        {"user_id": current_user["email"], "book_id": returnRequest.isbn},
        {"$set": {"return_date": datetime.utcnow(), "returned_book": True}},
    )
    if result.modified_count:
        logging.info("Book return successfully!!")
        
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
