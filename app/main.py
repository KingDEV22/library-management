from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.router import auth,book_admin,book_user
from app.logger.log_middleware import LogMiddleware


app = FastAPI()
app.add_middleware(LogMiddleware)

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(book_admin.router, tags=['Auth'], prefix='/api/book/admin')
app.include_router(book_user.router, tags=['Auth'], prefix='/api/book/user')


@app.get("/api/status")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}