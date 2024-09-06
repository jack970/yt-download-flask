from flask import Flask, abort, request, jsonify, send_from_directory, send_file
import yt_dlp
import os

app = Flask(__name__, static_folder='static', static_url_path='')

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
                videos = [get_video_info(entry) for entry in search_result['entries']]
                return jsonify({'videos': videos})
            else:
                return jsonify({'error': 'No results found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def get_video_info(data):
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
        'format': 'bestvideo+bestaudio/best',
        'ffmpeg_location': 'bin/ffmpeg.exe',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [progress_hook]
    }
    print("Iniciando o download")
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
        
        
def progress_hook(d):
    if d['status'] == 'finished':
        print(f"\nDone downloading video: {d['filename']}")


@app.route('/download', methods=['GET'])
def download_file():
    # Ensure the filename is secure
    safe_filename = os.path.join(DOWNLOAD_DIR, 'I Wonder.webm')
    # Check if the file exists
    if not os.path.isfile(safe_filename):
        abort(404, description="File not found")

    # Send the file to the client
    return send_file(safe_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
