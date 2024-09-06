async function searchVideos() {
    const query = document.getElementById('query').value;
    if (!query) {
        alert('Por favor, insira uma consulta.');
        return;
    }

    try {
        const response = await fetch(`/api/youtube/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.videos) {
            displayVideos(data.videos);
        } else {
            alert(data.error || 'Nenhum vídeo encontrado.');
        }
    } catch (error) {
        console.error('Erro ao buscar vídeos:', error);
        alert('Ocorreu um erro ao buscar os vídeos.');
    }
}

function displayVideos(videos) {
    const videosList = document.getElementById('videos');
    videosList.innerHTML = '';

    videos.forEach(video => {
        const videoItem = document.createElement('div');
        videoItem.className = 'video-item';
        videoItem.innerHTML = `
            <div>
                <iframe src="https://www.youtube.com/embed/${extractVideoId(video.url)}" class="video-player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
            <div class="video-details">
                <a class="video-title" href="${video.url}" target="_blank">${video.title}</a>
                <p>Canal: ${video.channel}</p>
                <a href="/api/youtube/download?url=${encodeURIComponent(video.url)}" class="download-button" download>Baixar Vídeo</a>
            </div>
        `;
        videosList.appendChild(videoItem);
    });
}

function extractVideoId(url) {
    const urlParams = new URLSearchParams(new URL(url).search);
    return urlParams.get('v') || url.split('/').pop();
}
