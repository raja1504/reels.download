from flask import Flask, render_template, request, send_file, url_for
import instaloader
import re
import requests
import os

app = Flask(__name__)

# app.config['HOST'] = os.getenv("FLASK_HOST", "192.168.24.186")  #192.168.29.86  #192.168.29.221
# app.config['PORT'] = int(os.getenv("FLASK_PORT", 5000))

@app.route('/')
def home():
    return render_template('home.html', message='')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    result, video_filename = download_instagram_video(url)
    if video_filename:
        video_url = url_for('serve_video', filename=video_filename)
        return render_template('home.html', video_url=video_url, message=result)
    else:
        return render_template('home.html', message=result)

def download_instagram_video(url):
    match = re.search(r'(?:https?://(?:www\.)?instagram\.com/(p|reel)/([A-Za-z0-9_-]+))', url)
    if not match:
        return "Invalid URL. Please provide a valid Instagram post or reel URL.", None

    shortcode = match.group(2)
    L = instaloader.Instaloader()

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if post.is_video:
            video_url = post.video_url
            video_response = requests.get(video_url, stream=True)
            video_filename = f"{shortcode}.mp4"

            with open(video_filename, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return f'Video downloaded successfully as {video_filename}', video_filename
        else:
            return "The provided URL does not contain a video.", None
    except Exception as e:
        return f'An error occurred: {e}', None

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    
# if __name__ == '__main__':
    # app.run(host=app.config['HOST'],port=app.config['PORT'], threaded=True, debug=True)
    # app.run(debug=True)