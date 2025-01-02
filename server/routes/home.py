import os
from flask import render_template, request, jsonify, Blueprint, redirect, url_for
from dotenv import load_dotenv
from scripts.posts import get_all_posts
from scripts.stream import is_stream_live

home = Blueprint('home', __name__)

load_dotenv()
STREAM_PULL_PUBLIC_ADDRESS = os.environ.get('STREAM_PULL_PUBLIC_ADDRESS')

@home.route('/')
def home_page():
    post_id = request.args.get('post_id')
    posts = get_all_posts()
    
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
        'home.html', 
        posts=response_posts, 
        stream_pull_url=STREAM_PULL_PUBLIC_ADDRESS,
        is_stream_live=is_stream_live(),
        highlight_post_id=post_id
    )
        
    return rendered_template

@home.route('/posts/<post_id>')
def redirect_to_post(post_id):
    return redirect(url_for('home.home_page', post_id=post_id))