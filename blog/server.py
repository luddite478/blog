import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

PORT=os.environ.get("BLOG_CONTAINER_PORT")

def strip_http(url):
    return url.replace("http://", "").replace("https://", "")

app = Flask(__name__)
minioClient = Minio(
    strip_http(os.environ.get("MINIO_ENDPOINT")),
    access_key=os.environ.get("MINIO_ROOT_USER"),
    secret_key=os.environ.get("MINIO_ROOT_PASSWORD"),
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
    posts = []
    for obj in minioClient.list_objects(bucket_name, recursive=True):
        filename = obj.object_name
        # Adjusting to handle filename format "[yy-mm-dd-hh-mm-ss].mp3"
        try:
            date_time_str = filename.strip("[]").split('.')[0]
            yy, mm, dd, hh, minute, ss = date_time_str.split('-')
            date = f"20{yy}-{mm}-{dd} {hh}:{minute}:{ss}"
            posts.append({'audio_s3_path': filename, 'date': date})
        except ValueError:
            logging.error(f"Filename {filename} does not match expected format.")
    return render_template('index.html', posts=posts)

@app.route('/audio/<filename>')
def stream_audio(filename):
    try:
        data = minioClient.get_object(bucket_name, filename)
        return Response(data, mimetype='audio/mpeg')
    except S3Error as err:
        return str(err)

if __name__ == "__main__":
    logging.info(f"Starting Flask server on port {PORT}")
    app.run(debug=True, host="0.0.0.0", port=PORT)