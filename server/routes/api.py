import os
import random
from flask import Flask, request, jsonify
from minio import Minio
import logging
from minio.error import S3Error
from dotenv import load_dotenv
from flask import Blueprint, render_template
from scripts.get_posts import get_posts
from scripts.delete_posts import delete_posts_by_ids
from datetime import datetime, timedelta
from pymongo import MongoClient


api = Blueprint('api', __name__)

minioClient = Minio(
    os.environ.get("MINIO_INTERNAL_ADDRESS"),
    access_key=os.environ.get("MINIO_ACCESS_KEY"),
    secret_key=os.environ.get("MINIO_SECRET_KEY"),
    secure=False
)

logging.getLogger('pymongo').setLevel(logging.WARNING)

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'flac', 'aac', 'ogg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

try:
    MONGO_URI = os.environ.get('MONGO_URI')
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client['blog']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

def upload_file_to_minio(file, bucket):
    MINIO_PROTOCOL = 'http'
    try:
        minioClient.put_object(
            bucket,
            file.filename,
            file.stream,
            length=-1,  # Automatically calculate the length
            part_size=10*1024*1024  # 10 MB part size
        )
        file_url = f"{MINIO_PROTOCOL}://{os.environ.get('MINIO_PUBLIC_ADDRESS')}/{bucket}/{file.filename}"
        return file_url
    except Exception as e:
        print(f"Error uploading file to MinIO: {e}")
        raise

def validate_audio_file(audio_block):
    file_extension = audio_block['filename'].filename.rsplit('.', 1)[1].lower()
    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        return None


@api.route('/create-post', methods=['POST'])
def create_post():
    try:
        if not request.form:
            return jsonify({"error": "Request must contain form data"}), 400

        form_data = request.form.to_dict()
        print('Form Data:', form_data)
        
        files_data = {key: file.filename for key, file in request.files.items()}
        print('Files:', files_data)

        post_data = {
            "date": datetime.now()
        }

        if 'title' in form_data:
            post_data['title'] = form_data['title']
        else:
            post_data['title'] = ''

        blocks = []

        if 'words' in form_data:
            blocks.append({
                'type': 'words',
                'text': form_data['words']
            })

        for _, f in request.files.items():
            file_extension = f.filename.rsplit('.', 1)[1].lower()
            if file_extension in ALLOWED_AUDIO_EXTENSIONS:
                blocks.append({
                    "type": "audio",
                    "s3_path": upload_file_to_minio(f, 'audio'),
                    "name": f.filename,
                    "extension": file_extension
                })
            elif file_extension in ALLOWED_VIDEO_EXTENSIONS:
                blocks.append({
                    "type": "video",
                    "s3_path": upload_file_to_minio(f, 'video'),
                    "name": f.filename,
                    "extension": file_extension
                })

        post_data['blocks'] = blocks

        result = db.posts.insert_one(post_data)
        return jsonify({"message": "Post created", "post_id": str(result.inserted_id)}), 201
    
    except Exception as e:
        print(f"Internal server error: {e}")
        return jsonify({"error": "Error creating post"}), 500

@api.route('/delete-posts', methods=['DELETE'])
def delete_posts():
    try:
        if not request.json or 'ids' not in request.json:
            return jsonify({"error": "Request must contain JSON data with 'ids'"}), 400

        ids = request.json['ids']
        delete_posts_by_ids(ids)
        return jsonify({"message": "Posts deleted"}), 200
    
    except Exception as e:
        print(f"Internal server error: {e}")
        return jsonify({"error": "Error deleting posts"}), 500