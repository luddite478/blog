from pymongo import MongoClient
import os
from bson.objectid import ObjectId

def get_all_posts():
    MONGO_URI = os.environ.get('MONGO_URI')
    client = MongoClient(MONGO_URI)

    db = client['blog']

    posts = list(db['posts'].find({}))
    client.close()

    return posts

def delete_posts_by_ids(ids):
    MONGO_URI = os.environ.get('MONGO_URI')
    client = MongoClient(MONGO_URI)

    db = client['blog']

    object_ids = [ObjectId(id) for id in ids]
    db['posts'].delete_many({'_id': {'$in': object_ids}})
    client.close()
