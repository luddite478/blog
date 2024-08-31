import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask import Blueprint, render_template
from scripts.get_posts import get_posts

home = Blueprint('home', __name__)

load_dotenv()

logging.basicConfig(level=logging.ERROR)

@home.route('/')
def home_page():
    posts = get_posts()
    print(posts)
    processed_posts = []
    for post in posts:
        try:
            post_data = {
                "date": post['date'] if 'date' in post else '',
                "audio_paths": [path for path in post['audio']['path']] if 'audio' in post and 'path' in post['audio'] else [],
                "name": post['audio']['name'] if 'audio' in post and 'name' in post['audio'] else '',
                "words": post['words'] if 'words' in post else '',
                "title": post['title'] if 'title' in post else ''
            }
            processed_posts.append(post_data)
        except ValueError as e:
            logging.error(f"Error processing post: {e}")
    
    # Render the template as a string
    rendered_template = render_template('home.html', posts=processed_posts)
    
    # Print the rendered template
    # print(rendered_template)
    
    return rendered_template