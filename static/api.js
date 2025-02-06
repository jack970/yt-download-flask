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

    videos.forEach((video, id) => {
        const { title, url, channel } = video;
        const videoItem = document.createElement('div');
        const className = `video-item-${id}`;
        videoItem.className = className
        videoItem.innerHTML = `
            <div>
                <iframe src="https://www.youtube.com/embed/${extractVideoId(url)}" class="video-player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
            <div class="video-details">
                <a class="video-title" href="${url}" target="_blank">${title}</a>
                <p>Canal: ${channel}</p>
                <button onclick="downloadVideo('${url}', '${title}', '${className}');" class="download-button" download>Baixar Vídeo</button>
                <div id="progress-container">
                    <p id="status">Status: Waiting to start...</p>
                    <progress id="progress-bar" value="0" max="100"></progress>
                    <p id="percent">0%</p>
                </div>
            </div>
        `;
        videosList.appendChild(videoItem);
    });
}

async function downloadVideo(url, title, videoId) {
    const button = event.target
    button.disabled = true
    button.innerText = 'Baixando...'

    try {
        const response = await fetch(`/api/youtube/download?url=${encodeURIComponent(url)}`);
        const data = await response.blob();

        if (!response.ok) {
            alert(data.error);
        }

        const urlObject = URL.createObjectURL(data);
        const link = document.createElement('a');

        link.href = urlObject;
        link.download = title;
        link.click();

        URL.revokeObjectURL(urlObject);

        alert('Vídeo baixado com sucesso!');

    } catch (error) {
        console.error('Erro ao baixar o vídeo:', error);
        alert('Ocorreu um erro ao baixar o vídeo.');
    } finally {
        button.disabled = false
        button.innerText = 'Baixar Vídeo'
    }
}

function extractVideoId(url) {
    const urlParams = new URLSearchParams(new URL(url).search);
    return urlParams.get('v') || url.split('/').pop();
}
