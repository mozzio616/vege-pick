from flask import Flask
import pymongo
import os

DB_HOST = os.environ['MONGO_HOST']
mongoClient = pymongo.MongoClient(DB_HOST)
db = mongoClient.lvl