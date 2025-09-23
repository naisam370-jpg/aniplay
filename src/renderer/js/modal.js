// Modal management
const { ipcRenderer } = require('electron');

class ModalManager {
    constructor() {
        this.currentAnime = null;
        this.setupModalListeners();
    }

    setupModalListeners() {
        // Anime modal
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeAnimeModal();
        });

        // Settings modal
        document.getElementById('closeSettings').addEventListener('click', () => {
            this.closeSettingsModal();
        });

        // Modal backdrop clicks
        document.getElementById('animeModal').addEventListener('click', (e) => {
            if (e.target.id === 'animeModal') {
                this.closeAnimeModal();
            }
        });

        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target.id === 'settingsModal') {
                this.closeSettingsModal();
            }
        });

        // Episode actions
        document.getElementById('playRandomEpisode').addEventListener('click', () => {
            this.playRandomEpisode();
        });

        document.getElementById('continueWatching').addEventListener('click', () => {
            this.continueWatching();
        });

        // Settings actions
        document.getElementById('selectLibraryPath').addEventListener('click', () => {
            this.selectLibraryPath();
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    async openAnimeModal(anime) {
        this.currentAnime = anime;
        
        // Populate modal with anime info
        document.getElementById('modalTitle').textContent = anime.title;
        document.getElementById('modalScore').textContent = anime.score ? anime.score.toFixed(1) : 'N/A';
        document.getElementById('modalEpisodes').textContent = anime.episodes || 'Unknown';
        document.getElementById('modalStatus').textContent = anime.status || 'Unknown';
        document.getElementById('modalYear').textContent = anime.year || 'Unknown';
        document.getElementById('modalDescription').textContent = anime.description || 'No description available.';
        
        // Handle genres
        const genres = Array.isArray(anime.genres) ? anime.genres : [];
        document.getElementById('modalGenres').textContent = genres.length > 0 ? genres.join(', ') : 'Unknown';
        
        // Handle cover image
        const coverImg = document.getElementById('modalCover');
        if (anime.cover) {
            coverImg.src = `covers/${anime.cover}`;
            coverImg.alt = anime.title;
        } else {
            coverImg.src = '';
            coverImg.alt = 'No cover available';
        }

        // Load episodes
        await this.loadEpisodes(anime);

        // Show modal
        document.getElementById('animeModal').classList.remove('hidden');
    }

    async loadEpisodes(anime) {
        const episodesList = document.getElementById('episodesList');
        episodesList.innerHTML = '<div class="loading-episodes">Loading episodes...</div>';

        try {
            const episodes = await window.libraryManager.getAnimeEpisodes(anime.path);
            
            if (episodes.length === 0) {
                episodesList.innerHTML = '<div class="loading-episodes">No episodes found</div>';
                return;
            }

            // Sort episodes
            const sortedEpisodes = window.libraryManager.sortEpisodes(episodes);
            
            // Create episode list
            episodesList.innerHTML = sortedEpisodes.map((episode, index) => `
                <div class="episode-item" data-episode-path="${episode.path}">
                    <span class="episode-number">${index + 1}</span>
                    <span class="episode-name">${window.libraryManager.formatEpisodeName(episode.name)}</span>
                    <span class="episode-size">${window.aniplay.formatFileSize(episode.size)}</span>
                </div>
            `).join('');

            // Add click listeners to episodes
            episodesList.querySelectorAll('.episode-item').forEach(item => {
                item.addEventListener('click', () => {
                    const episodePath = item.dataset.episodePath;
                    this.playEpisode(episodePath);
                });
            });

        } catch (error) {
            console.error('Error loading episodes:', error);
            episodesList.innerHTML = '<div class="loading-episodes">Error loading episodes</div>';
        }
    }

    async playEpisode(episodePath) {
        try {
            await window.libraryManager.playEpisode(episodePath, this.currentAnime);
            this.closeAnimeModal();
        } catch (error) {
            console.error('Error playing episode:', error);
        }
    }

    async playRandomEpisode() {
        if (!this.currentAnime) return;

        try {
            const episodes = await window.libraryManager.getAnimeEpisodes(this.currentAnime.path);
            const randomEpisode = window.libraryManager.getRandomEpisode(episodes);
            
            if (randomEpisode) {
                await this.playEpisode(randomEpisode.path);
            } else {
                alert('No episodes available');
            }
        } catch (error) {
            console.error('Error playing random episode:', error);
        }
    }

    async continueWatching() {
        if (!this.currentAnime) return;

        try {
            const episodes = await window.libraryManager.getAnimeEpisodes(this.currentAnime.path);
            const sortedEpisodes = window.libraryManager.sortEpisodes(episodes);
            
            // For now, just play the first episode
            // TODO: Implement actual watch history tracking
            if (sortedEpisodes.length > 0) {
                await this.playEpisode(sortedEpisodes[0].path);
            } else {
                alert('No episodes available');
            }
        } catch (error) {
            console.error('Error continuing watch:', error);
        }
    }

    closeAnimeModal() {
        document.getElementById('animeModal').classList.add('hidden');
        this.currentAnime = null;
    }

    openSettingsModal() {
        document.getElementById('settingsModal').classList.remove('hidden');
    }

    closeSettingsModal() {
        document.getElementById('settingsModal').classList.add('hidden');
    }

    closeAllModals() {
        this.closeAnimeModal();
        this.closeSettingsModal();
    }

    async selectLibraryPath() {
        try {
            const path = await ipcRenderer.invoke('file:select-library');
            if (path) {
                document.getElementById('libraryPath').value = path;
                // TODO: Save to settings and update library manager
            }
        } catch (error) {
            console.error('Error selecting library path:', error);
        }
    }
}

// Initialize modal manager
document.addEventListener('DOMContentLoaded', () => {
    window.modalManager = new ModalManager();
});
