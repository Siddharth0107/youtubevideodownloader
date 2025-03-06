import eventlet
eventlet.monkey_patch()  # Must be at the top

from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import threading

app = Flask(__name__)

DOWNLOAD_FOLDER = "static/videos/"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

def download_video(youtube_url):
    """Downloads the video and returns the file path."""
    filename = os.path.join(DOWNLOAD_FOLDER, "temp_video.mp4")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': filename,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return filename

@app.route('/start_download', methods=['POST'])
def start_download():
    """Start the video download and return the file path for the user."""
    youtube_url = request.form['youtube_url']
    
    file_path = download_video(youtube_url)
    
    return jsonify({"download_url": f"/download?file={os.path.basename(file_path)}"}), 200

@app.route('/download')
def download():
    """Allow the user to download the file and delete it after downloading."""
    file_name = request.args.get('file')
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    if not os.path.exists(file_path):
        return "File not found!", 404

    # Serve file and delete it after sending
    def delete_file():
        os.remove(file_path)
        print(f"Deleted: {file_path}")

    response = send_file(file_path, as_attachment=True)
    threading.Thread(target=delete_file).start()
    
    return response

if __name__ == '__main__':
    app.run(threaded=True)
