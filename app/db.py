from pymongo import mongo_client
import pymongo
import logging

from app.config import settings

def connect_db():
    client = mongo_client.MongoClient(settings.DB_URL, serverSelectionTimeoutMS=5000)
    try:
        conn = client.server_info()
        logging.info(f'Connected to MongoDB {conn.get("version")}')
    except Exception:
        logging.error("Unable to connect to the MongoDB server.")
    return client


# fucntion to close connection with mongodb
def close_connection(client):
    if not client:
        client.close()
        logging.info("Connection closed!!")


client = connect_db()
# connect to specific database
db = client[settings.MONGODB_DATABASE]

# creating instance of the respective collection
User = db[settings.USER_COLLECTION]
Book = db[settings.BOOK_COLLECTION]
IssuedBook = db[settings.ISSUE_COLLECTION]

User.create_index([("email", pymongo.ASCENDING)], unique=True)
