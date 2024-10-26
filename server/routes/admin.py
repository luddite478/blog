import os
from flask import Flask, Response, render_template, request, jsonify, Blueprint, redirect, url_for
from minio import Minio
from minio.error import S3Error
import logging
from dotenv import load_dotenv
from scripts.posts import get_posts
from scripts.stream import is_stream_live

logging.getLogger('pymongo').setLevel(logging.WARNING)
load_dotenv()
STREAM_PULL_PUBLIC_ADDRESS = os.environ.get('STREAM_PULL_PUBLIC_ADDRESS')

admin = Blueprint('admin', __name__)

@admin.route('/')
def admin_page():
    posts = get_posts()
    
    # Sort posts by date in descending order before processing
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    response_posts = []
    for post in posts:
        try:
            post_data = {
                "id": str(post['_id']) if '_id' in post else '',
                "date": post['date'].strftime('%B %d, %Y') if 'date' in post else '',
                "blocks": post['blocks'] if 'blocks' in post else [],
                "title": post['title'] if 'title' in post else ''
            }

            response_posts.append(post_data)
        except ValueError as e:
            print(f"Error processing post: {e}")
            return jsonify({"error": "Error processing post"}), 500
        
    rendered_template = render_template(
        'admin.html', 
        posts=response_posts, 
        stream_pull_url=STREAM_PULL_PUBLIC_ADDRESS,
        is_stream_live=is_stream_live()
    )
        
    return rendered_template

@admin.route('/posts/<post_id>')
def redirect_to_post(post_id):
    return redirect(url_for('home.home_page', post_id=post_id))