// Library management functionality
const { ipcRenderer } = require('electron');

class LibraryManager {
    constructor() {
        this.currentAnime = null;
        this.episodes = [];
    }

    async getAnimeEpisodes(animePath) {
        try {
            this.episodes = await ipcRenderer.invoke('anime:get-episodes', animePath);
            return this.episodes;
        } catch (error) {
            console.error('Error getting episodes:', error);
            return [];
        }
    }

    async playEpisode(episodePath, animeInfo) {
        try {
            // Create a new player window (handled by main process)
            const result = await ipcRenderer.invoke('video:load', episodePath);
            
            if (result.success) {
                console.log('Episode loaded successfully');
                // The main process will handle opening the player window
            } else {
                throw new Error(result.error || 'Failed to load episode');
            }
        } catch (error) {
            console.error('Error playing episode:', error);
            alert('Failed to play episode: ' + error.message);
        }
    }

    getRandomEpisode(episodes) {
        if (!episodes || episodes.length === 0) return null;
        const randomIndex = Math.floor(Math.random() * episodes.length);
        return episodes[randomIndex];
    }

    sortEpisodes(episodes) {
        return episodes.sort((a, b) => {
            // Extract episode numbers from filenames
            const aMatch = a.name.match(/(?:episode?|ep)?\s*(\d+)/i);
            const bMatch = b.name.match(/(?:episode?|ep)?\s*(\d+)/i);
            
            if (aMatch && bMatch) {
                return parseInt(aMatch[1]) - parseInt(bMatch[1]);
            }
            
            // Fallback to alphabetical sort
            return a.name.localeCompare(b.name);
        });
    }

    formatEpisodeName(filename) {
        // Remove file extension and clean up episode name
        let name = filename.replace(/\.[^/.]+$/, '');
        
        // Try to extract episode number and clean title
        const episodeMatch = name.match(/(?:episode?|ep)?\s*(\d+)(?:\s*-\s*(.+))?/i);
        
        if (episodeMatch) {
            const episodeNum = episodeMatch[1];
            const title = episodeMatch[2] || '';
            
            if (title) {
                return `Episode ${episodeNum}: ${title}`;
            } else {
                return `Episode ${episodeNum}`;
            }
        }
        
        return name;
    }

    async updateWatchHistory(animeId, episodePath, position, duration) {
        try {
            await ipcRenderer.invoke('watch-history:update', animeId, episodePath, position, duration);
        } catch (error) {
            console.error('Error updating watch history:', error);
        }
    }
}

// Make library manager available globally
window.libraryManager = new LibraryManager();
