from fastapi import APIRouter, status, Depends, HTTPException
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from typing import List
import logging
from app.schema import UserSchema
from app.db import Book
import app.schema as schema
from app.permission import PermissionChecker

# Set up a logger with basic configuration
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
)
async def add_books(
    requestBooks: List[schema.Book],
    current_user: UserSchema = Depends(PermissionChecker(required_roles=["admin"])),
):
    # Extract ISBNs from the request books to check for existing books
    isbns = [book.isbn for book in requestBooks]

    # Find existing books with matching ISBNs
    existing_books = Book.find({"isbn": {"$in": isbns}})

    # Set isbn to filter out existing books
    existing_isbns = set(book["isbn"] for book in existing_books)
    if len(existing_isbns) == len(requestBooks):
        logging.error("All books present!!!")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="All Books already exist!!"
        )

    # Filter out books that already exist
    books_to_add = [book for book in requestBooks if book.isbn not in existing_isbns]

    # insert books in bulk
    result = Book.insert_many([jsonable_encoder(book) for book in books_to_add])
    if result.inserted_ids:
        logging.info(str(len(books_to_add)) + " Books added successfully.")
        return {
            "message": "Books added successfully",
            "added_books": len(result.inserted_ids),
        }
    else:
        logging.error("Failed to add books!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add books!!",
        )


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    requestBook: schema.Book,
    current_user: UserSchema = Depends(PermissionChecker(required_roles=["admin"])),
):
    # check if book already exists
    book: schema.Book = Book.find_one({"isbn": requestBook.isbn})
    if book:
        logging.error("Book already exist!!!")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Book already exist!!"
        )
    
    # insert the book
    result = Book.insert_one(jsonable_encoder(requestBook))
    if result.inserted_id:
        logging.info("Book added: " + requestBook.isbn)
        return {"message": "Book added successfully"}
    else:
        logging.error("Failed to add book!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add book!!",
        )


@router.put(
    "/update",
    status_code=status.HTTP_201_CREATED,
)
async def update_book(
    requestBook: schema.Book,
    current_user: UserSchema = Depends(PermissionChecker(required_roles=["admin"])),
):
    # check if the book is present
    book: schema.Book = Book.find_one({"isbn": requestBook.isbn})
    if not book:
        logging.error("Book not found!!!")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found!!"
        )
    
    # Update the fields of the existing book with the new values
    book["title"] = requestBook.title
    book["author"] = requestBook.author
    book["published_year"] = requestBook.published_year
    book["quantity"] = requestBook.quantity

    # Update the book in the db
    result = Book.update_one({"_id": ObjectId(book["_id"])}, {"$set": book})
    if result.modified_count == 1:
        logging.info("Book updated: " + requestBook.isbn)
        return {"message": "Book updated successfully"}
    else:
        logging.error("Failed to update book!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book!!",
        )


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    requestBook: schema.Book,
    current_user: UserSchema = Depends(PermissionChecker(required_roles=["admin"])),
):
    result = None
    # delete based on isbn
    if requestBook.isbn:
        result = Book.delete_one({"isbn": requestBook.isbn})

    # delete based on author
    elif requestBook.author:
        result = Book.delete_many({"author": requestBook.author})
        
    # delete based on title
    elif requestBook.title:
        result = Book.delete_many({"title": requestBook.title})

    if result.deleted_count < 1:
        logging.error("Failed to delete book!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book!!",
        )
    else:
        logging.info("Book deleted..")
        return {"message": "Book updated successfully"}
