from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from minio import Minio
from minio.error import S3Error
import random

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['blog']

# MinIO setup
MINIO_PROTOCOL = 'http'
MINIO_PUBLIC_ADDRESSS = os.environ.get('MINIO_PUBLIC_ADDRESS')
MINIO_INTERNAL_ADDRESS = os.environ.get('MINIO_INTERNAL_ADDRESS')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
minio_client = Minio(
    MINIO_INTERNAL_ADDRESS,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

#   {
#     _id: ObjectId('6713813469b4f70ecfc684e1'),
#     date: ISODate('2024-10-19T09:51:28.160Z'),
#     title: '',
#     blocks: [
#       { id: '76a7a5', type: 'words', text: '' },
#       {
#         type: 'audio',
#         files: [
#           {
#             extension: 'wav',
#             s3_path: 'http://localhost:30200/audio/26b487.wav'
#           },
#           {
#             extension: 'mp3',
#             s3_path: 'http://localhost:30200/audio/26b487.mp3'
#           }
#         ],
#         file_id: '26b487',
#         name: 'test.wav'
#       }
#     ]
#   }
# ]

# if 'posts' not in db.list_collection_names():
#     db.create_collection('posts')
    
def init_dev_db():
    try:
        audio_objects = list(minio_client.list_objects('audio', recursive=True))
        posts = []
        for audio_object in audio_objects:
            audio_path = f"{MINIO_PROTOCOL}://{MINIO_PUBLIC_ADDRESSS}/audio/{audio_object.object_name}"
            post = {
                "date": datetime.now() - timedelta(days=random.randint(1, 30)),  # Randomize the date for each post
                "title": "",
                "blocks":  [{
                    'type': 'audio',
                    's3_path': audio_path,
                    'name': audio_object.object_name.split('.')[0],
                    'extension': audio_object.object_name.split('.')[1]
                }],   
            }
            posts.append(post)

        if posts:
            result = db.posts.insert_many(posts)
            print(f"Inserted {len(posts)} posts with IDs: {result.inserted_ids}")
        else:
            print("No songs found in the 'songs' bucket. No posts were inserted.")
    except S3Error as e:
        print(f"Error accessing 'songs' bucket: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    init_dev_db()

