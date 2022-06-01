from dotenv import load_dotenv
import pymongo
import os

load_dotenv()
DB_HOST = os.getenv('MONGO_HOST')
DB_NAME = os.getenv('DB_NAME')

mongoClient = pymongo.MongoClient(DB_HOST)
db = mongoClient[DB_NAME]