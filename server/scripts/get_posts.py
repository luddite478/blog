from pymongo import MongoClient
import os

def get_posts():
    MONGO_URI = os.environ.get('MONGO_URI')
    client = MongoClient(MONGO_URI)

    db = client['blog']

    posts = list(db['posts'].find({}))
    client.close()

    return posts

if __name__ == "__main__":
    get_posts()
