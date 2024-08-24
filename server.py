import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error

app = Flask(__name__)

minioClient = Minio(
    os.environ.get("S3_ENDPOINT"),
    access_key=os.environ.get("S3_ACCESS_KEY"),
    secret_key=os.environ.get("S3_SECRET_KEY"),
    secure=False
)

bucket_name = 'audio'
if not minioClient.bucket_exists(bucket_name):
    try:
        minioClient.make_bucket(bucket_name)
    except S3Error as err:
        print(str(err))

@app.route('/')
def home():
    posts = [
        {'audio_s3_path': 'test', 'date': 'This is the first post.'},
        {'audio_s3_path': 'test', 'date': 'This is the second post.'},
    ]
    return render_template('home.html', posts=posts)

@app.route('/audio/<filename>')
def stream_audio(filename):
    try:
        data = minioClient.get_object(bucket_name, filename)
        return Response(data, mimetype='audio/mpeg')
    except S3Error as err:
        return str(err)

if __name__ == "__main__":
    app.run(debug=True)