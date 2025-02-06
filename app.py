from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import yt_dlp
import os

# Variável global para armazenar o progresso
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/api/youtube/search', methods=['GET'])
def search_youtube():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'extract_flat': True,
        'skip_download': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_result = ydl.extract_info(f'ytsearch5:{query}', download=False)
            if 'entries' in search_result:
                videos = [video(entry) for entry in search_result['entries']]
                return jsonify({'videos': videos})
            else:
                return jsonify({'error': 'No results found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def video(data):
    return {
        'title': data.get('title'),
        'url': data.get('url'),
        'channel': data.get('channel')
    }

@app.route('/api/youtube/download', methods=['GET'])
def download_video():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    # Definir opções de download
    ydl_opts = {
        'format': "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'noprogress': True,
        'quiet': True
        # 'progress_hooks': [progress_hook]
    }
    
    # Extraí informações e faça o download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # return jsonify(info), 200

        filename = info.get('requested_downloads')[0].get('filepath')
        # Verifique se o arquivo foi criado
        if not os.path.isfile(filename):
            return jsonify({'error': 'Failed to download video'}), 500

        # Enviar o arquivo para o cliente
        return send_file(filename, as_attachment=True) 

if __name__ == '__main__':
    app.run(debug=True)


