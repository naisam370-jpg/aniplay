// AniPlay Main Renderer Script
const { ipcRenderer } = require('electron');
const events = require('../shared/events');

class AniPlayApp {
    constructor() {
        this.isInitialized = false;
        this.animeLibrary = [];
        this.filteredLibrary = [];
        this.currentGridSize = 200;
        this.searchTimeout = null;
        this.init();
    }

    async init() {
        console.log('Initializing AniPlay...');
        
        try {
            await ipcRenderer.invoke('app:init');
            this.isInitialized = true;
            this.setupEventListeners();
            this.loadLibrary();
            console.log('AniPlay initialized successfully');
        } catch (error) {
            console.error('Failed to initialize AniPlay:', error);
        }
    }

    setupEventListeners() {
        // Scan library buttons
        document.getElementById('scanLibrary').addEventListener('click', () => {
            this.scanLibrary();
        });
        
        const scanLibraryEmpty = document.getElementById('scanLibraryEmpty');
        if (scanLibraryEmpty) {
            scanLibraryEmpty.addEventListener('click', () => {
                this.scanLibrary();
            });
        }

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.searchLibrary(e.target.value);
            }, 300);
        });

        // Grid size control
        const gridSizeSlider = document.getElementById('gridSize');
        gridSizeSlider.addEventListener('input', (e) => {
            this.updateGridSize(parseInt(e.target.value));
        });

        // View toggle buttons
        document.getElementById('gridView').addEventListener('click', () => {
            this.setView('grid');
        });
        
        document.getElementById('listView').addEventListener('click', () => {
            this.setView('list');
        });

        // Settings - Fixed to wait for modal manager
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    async loadLibrary() {
        this.showLoading(true);
        
        try {
            this.animeLibrary = await ipcRenderer.invoke('library:get-all');
            this.filteredLibrary = [...this.animeLibrary];
            this.updateLibraryDisplay();
            this.updateStats();
        } catch (error) {
            console.error('Error loading library:', error);
        } finally {
            this.showLoading(false);
        }
    }

    async scanLibrary() {
        this.showLoading(true, 'Scanning library and fetching covers...');
        
        try {
            const result = await ipcRenderer.invoke('library:scan');
            
            console.log('Scan result:', result);
            
            // Reload library after scan
            await this.loadLibrary();
            
            // Show scan results
            const message = `Scan complete!\n\nProcessed: ${result.processed}/${result.total} anime\nErrors: ${result.errors.length}`;
            
            if (result.errors.length > 0) {
                console.log('Scan errors:', result.errors);
            }
            
            alert(message);
            
        } catch (error) {
            console.error('Library scan failed:', error);
            alert('Library scan failed: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async searchLibrary(query) {
        if (!query.trim()) {
            this.filteredLibrary = [...this.animeLibrary];
        } else {
            try {
                this.filteredLibrary = await ipcRenderer.invoke('library:search', query);
            } catch (error) {
                console.error('Search error:', error);
                this.filteredLibrary = [];
            }
        }
        
        this.updateLibraryDisplay();
    }

    updateLibraryDisplay() {
        const grid = document.getElementById('animeGrid');
        const emptyState = document.getElementById('emptyState');
        
        if (this.filteredLibrary.length === 0) {
            grid.style.display = 'none';
            emptyState.style.display = this.animeLibrary.length === 0 ? 'flex' : 'none';
            
            if (this.animeLibrary.length > 0) {
                // Show "no results" message
                grid.innerHTML = '<div class="no-results">No anime found matching your search.</div>';
                grid.style.display = 'block';
            }
            
            return;
        }
        
        emptyState.style.display = 'none';
        grid.style.display = 'grid';
        
        // Update grid template based on current size
        grid.style.gridTemplateColumns = `repeat(auto-fill, minmax(${this.currentGridSize}px, 1fr))`;
        
        grid.innerHTML = this.filteredLibrary.map(anime => this.createAnimeCard(anime)).join('');
        
        // Add click listeners to cards
        grid.querySelectorAll('.anime-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                this.openAnimeDetails(this.filteredLibrary[index]);
            });
        });
    }

    createAnimeCard(anime) {
        const coverPath = anime.cover 
            ? `covers/${anime.cover}` 
            : null;
        
        const score = anime.score ? anime.score.toFixed(1) : 'N/A';
        const episodeCount = anime.episodes || 'Unknown';
        
        // Limit genres display
        const genres = Array.isArray(anime.genres) ? anime.genres.slice(0, 3) : [];
        
        return `
            <div class="anime-card" data-anime-id="${anime.id}">
                <div class="anime-cover">
                    ${coverPath 
                        ? `<img src="${coverPath}" alt="${anime.title}" loading="lazy">` 
                        : `<div class="cover-placeholder">🎌</div>`
                    }
                </div>
                <div class="anime-info">
                    <h3 class="anime-title">${this.escapeHtml(anime.title)}</h3>
                    <div class="anime-meta">
                        <span class="anime-score">${score}</span>
                        <span class="anime-episodes">${episodeCount} eps</span>
                    </div>
                    <div class="anime-genres">
                        ${genres.map(genre => `<span class="genre-tag">${this.escapeHtml(genre)}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    openAnimeDetails(anime) {
        // Wait for modal manager to be available
        if (window.modalManager) {
            window.modalManager.openAnimeModal(anime);
        } else {
            console.error('Modal manager not available yet');
        }
    }

    updateGridSize(size) {
        this.currentGridSize = size;
        this.updateLibraryDisplay();
    }

    setView(viewType) {
        // Update button states
        document.querySelector('.view-btn.active').classList.remove('active');
        document.getElementById(viewType + 'View').classList.add('active');
        
        // Update grid display
        const grid = document.getElementById('animeGrid');
        if (viewType === 'list') {
            grid.classList.add('list-view');
        } else {
            grid.classList.remove('list-view');
        }
    }

    updateStats() {
        document.getElementById('totalCount').textContent = this.animeLibrary.length;
    }

    showLoading(show, message = 'Loading library...') {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (show) {
            loadingIndicator.querySelector('p').textContent = message;
            loadingIndicator.classList.remove('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }

    openSettings() {
        // Wait for modal manager to be available
        if (window.modalManager) {
            window.modalManager.openSettingsModal();
        } else {
            // Fallback - try again in a moment
            setTimeout(() => {
                if (window.modalManager) {
                    window.modalManager.openSettingsModal();
                } else {
                    console.error('Modal manager not available');
                    alert('Settings modal not ready yet. Please try again.');
                }
            }, 100);
        }
    }

    handleKeyboard(e) {
        switch (e.code) {
            case 'KeyF':
                if (e.ctrlKey) {
                    e.preventDefault();
                    document.getElementById('searchInput').focus();
                }
                break;
            case 'F5':
                e.preventDefault();
                this.scanLibrary();
                break;
            case 'Escape':
                document.getElementById('searchInput').value = '';
                this.searchLibrary('');
                break;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        
        const sizes = ['B', 'KB', 'MB', 'GB'];
        let i = 0;
        
        while (bytes >= 1024 && i < sizes.length - 1) {
            bytes /= 1024;
            i++;
        }
        
        return `${bytes.toFixed(1)} ${sizes[i]}`;
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aniplay = new AniPlayApp();
});