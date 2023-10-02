# Overview

This is a library management app with FastAPI. 
The features of this app:
- Register/Login a user with JWT auth and role based access.
- Add, Update and Delete books.
- Borrow and Return books.
- Search and View books in the database with pagination.
- Recommend books based on issued books history.


## Set up the app
- Make sure to have docker install in the system
- Clone the repo and ``cd`` into it
- Run ```docker-compose up``` to start the server
- Run ```docker-compose down``` to stop the server


## API Docs

```/api/auth/register``` *POST* : to register user

Sample Body:

```
{
  "name": "King Biswas",
  "email": "king@gmail.com",
  "role": ["user"],
  "password": "test123"
}
```

Response code : *201* for success, *422* for Validation Error 

```/api/auth/login``` *POST* : to login user

Sample form-data:

```
username:king@gmail.com
password:test123
```

Response code : *200* for success, *422* for Validation Error 

```/api/book/admin/add``` *POST* : to add list of books with admin role

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Sample Body:

```
[
  {
    "isbn": "9780132350884",
    "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
    "author": "Robert C. Martin",
    "published_year": 2008,
    "quantity": 10
  },
  {
    "isbn": "9781449331818",
    "title": "Eloquent JavaScript: A Modern Introduction to Programming",
    "author": "Marijn Haverbeke",
    "published_year": 2011,
    "quantity": 5
  },
  {
    "isbn": "9781593279509",
    "title": "Python Crash Course",
    "author": "Eric Matthes",
    "published_year": 2019,
    "quantity": 15
  },
  {
    "isbn": "9780135471944",
    "title": "The Pragmatic Programmer: Your Journey to Mastery",
    "author": "David Thomas, Andrew Hunt",
    "published_year": 2019,
    "quantity": 8
  },
  {
    "isbn": "9780134494166",
    "title": "Introduction to the Theory of Computation",
    "author": "Michael Sipser",
    "published_year": 2012,
    "quantity": 20
  }]
```

Response code : *201* for success, *422* for Validation Error 

```/api/book/admin/create``` *POST* : to add a new book with admin role

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Sample Body:

```
{
    "isbn": "978-3-16-148410-2334512",
    "title": "Example",
    "author": "John1 Doe1",
    "published_year": 2021,
    "quantity": 10
}
```

Response code : *201* for success, *422* for Validation Error 

```/api/book/admin/update``` *PUT* : to update a book with admin role

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Sample Body:

```
{
    "isbn": "978-3-16-148410-2334512",
    "title": "Example",
    "author": "John1 Doe1",
    "published_year": 2021,
    "quantity": 10
}
```

Response code : *201* for success, *422* for Validation Error 


```/api/book/admin/delete``` *DELETE* : to delete a book with admin role

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Sample Body:  
```
{
    "isbn": "978-3-16-148410-23023"
}
```

Response code : *204* for success, *422* for Validation Error 

```/api/book/user/all``` *GET* : to fetch all books

Sample Params

```
page:2  (min: 1)
page_size:7 (max: 100)
```

Response code : *200* for success, *422* for Validation Error 

Sample output: 
```
[
  {
    "isbn": "string",
    "title": "string",
    "author": "string",
    "published_year": 0,
    "quantity": 0
  }
]
```


```/api/book/user/search``` *GET* : to search based on query

Sample Params

```
query:"enter title or author or isbn"
page:2  (min: 1)
page_size:7 (max: 100)
```

Response code : *200* for success, *422* for Validation Error 

Sample output: 
```
[
  {
    "isbn": "string",
    "title": "string",
    "author": "string",
    "published_year": 0,
    "quantity": 0
  }
]
```

```/api/book/user/personalize``` *GET* : get personalised books recommendation based on borrowed book history

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Response code : *200* for success, *422* for Validation Error 

Sample output: 
```
[
  {
    "isbn": "string",
    "title": "string",
    "author": "string",
    "published_year": 0,
    "quantity": 0
  }
]
```

```/api/book/user/borrow``` *POST* : to borrow books

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Sample Body : 
```
{
  "isbn": "string"
}
```

Response code : *201* for success, *422* for Validation Error 

Sample Output: 
```
{
  "user_id": "string",
  "book_id": "string",
  "borrow_date": "2023-10-02T06:55:29.503Z"
}
```

```/api/book/user/return``` *POST* : to return issued books

Sample Header: ```Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW5nQGdtYWlsLmNvbSIsImV4cCI6MTY5NjIzNjI0OX0.wbgp2icCIHv6MEZ7yDe2kkpFvEUolHmZfMcbthEOLBU```

Sample Body : 
```
{
  "isbn": "string"
}
```

Response code : *200* for success, *422* for Validation Error
