from flask import Flask
import pymongo
import os

DB_HOST = os.environ['MONGO_HOST']

mongoClient = pymongo.MongoClient(DB_HOST)

db = mongoClient.lvl

collection_locations = db.locations
collection_racks = db.racks
collection_lockers = db.lockers
collection_items = db.items
collection_payments = db.payments