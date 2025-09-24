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
        // Refresh library button
        document.getElementById('refreshLibrary').addEventListener('click', () => {
            this.refreshLibrary();
        });

        // Reset library button  
        document.getElementById('resetLibrary').addEventListener('click', () => {
            this.resetLibrary();
        });

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

    async refreshLibrary() {    
        const confirmed = confirm('Refresh library? This will update existing anime with fresh data from MyAnimeList.');
    if (!confirmed) return;

        this.showLoading(true, 'Refreshing library...');

        try {
            const result = await ipcRenderer.invoke('library:refresh');
            await this.loadLibrary();

            let message = `🔄 Library refresh complete!\n\n`;
            message += `📊 Results:\n`;
            message += `• Added: ${result.added || 0}\n`;
            message += `• Updated: ${result.updated || 0}\n`;
            message += `• Removed: ${result.removed || 0}\n`;

            alert(message);

        } catch (error) {
            console.error('❌ Refresh failed:', error);
            alert('Refresh failed: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    async resetLibrary() {
        const confirmed = confirm('⚠️ This will delete your entire library and all cover images. Are you sure?');
        if (!confirmed) return;

        this.showLoading(true, 'Resetting library...');

        try {
            const result = await window.electron.ipcRenderer.invoke('library:reset');
            await this.loadLibrary();
        
            alert(`🗑️ Library reset complete!\n\nRescanned ${result.processed}/${result.total} anime folders.`);
        } catch (error) {
            console.error('❌ Reset failed:', error);
            alert('Reset failed: ' + error.message);
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
                grid.innerHTML = '<div class="no-results">No anime found matching your search.</div>';
                grid.style.display = 'block';
            }
            
            return;
        }
        
        emptyState.style.display = 'none';
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = `repeat(auto-fill, minmax(${this.currentGridSize}px, 1fr))`;

        // Clear and append element nodes (not HTML strings)
        grid.innerHTML = '';
        this.filteredLibrary.forEach((anime) => {
            const el = this.createAnimeCard(anime);
            grid.appendChild(el);
        });

        // Resolve local covers AFTER elements are in DOM
        const localImgs = grid.querySelectorAll('img.anime-cover[data-local-cover]');
        localImgs.forEach(img => {
            const coverPath = img.getAttribute('data-local-cover');
            const tryPath = coverPath; // keep as stored; main handler will try candidates
            ipcRenderer.invoke('file:read-base64', tryPath)
                .then(dataUrl => {
                    if (dataUrl) {
                        img.src = dataUrl;
                        img.removeAttribute('data-local-cover');
                    } else {
                        console.warn('file:read-base64 returned null for', tryPath);
                    }
                })
                .catch(err => {
                    console.warn('Failed to load local cover via IPC:', tryPath, err);
                });
        });

        // Add click listeners to cards (use current DOM order)
        grid.querySelectorAll('.anime-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                this.openAnimeDetails(this.filteredLibrary[index]);
            });
        });
    }

    createAnimeCard(anime) {
        const card = document.createElement('div');
        card.className = 'anime-card';
        card.dataset.animeId = anime.id;

        const img = document.createElement('img');
        img.className = 'anime-cover';

        // Inline SVG placeholder data URL
        const placeholder = 'data:image/svg+xml;utf8,' + encodeURIComponent(
            `<svg xmlns="http://www.w3.org/2000/svg" width="300" height="420" viewBox="0 0 300 420">
               <rect width="100%" height="100%" fill="#efefef"/>
               <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#888" font-family="sans-serif" font-size="18">No cover</text>
             </svg>`
        );

        let src = anime.cover || anime.image_url || '';

        // if remote URL or already data url, use directly
        if (src && /^https?:\/\//i.test(src)) {
            img.src = src;
        } else if (src && src.startsWith('data:')) {
            img.src = src;
        } else if (src) {
            // Local path: set placeholder and tag element for later resolution
            img.src = placeholder;
            img.setAttribute('data-local-cover', src);
        } else {
            img.src = placeholder;
        }

        img.onerror = () => { img.src = placeholder; };
        card.appendChild(img);

        const title = document.createElement('h3');
        title.className = 'anime-title';
        title.textContent = anime.title;
        card.appendChild(title);

        const meta = document.createElement('div');
        meta.className = 'anime-meta';

        const score = document.createElement('span');
        score.className = 'anime-score';
        score.textContent = anime.score ? anime.score.toFixed(1) : 'N/A';
        meta.appendChild(score);

        const episodeCount = document.createElement('span');
        episodeCount.className = 'anime-episodes';
        episodeCount.textContent = (anime.episodes || 'Unknown') + ' eps';
        meta.appendChild(episodeCount);

        card.appendChild(meta);

        const genres = document.createElement('div');
        genres.className = 'anime-genres';
        genres.innerHTML = Array.isArray(anime.genres) ? anime.genres.slice(0, 3).map(genre => `<span class="genre-tag">${this.escapeHtml(genre)}</span>`).join('') : '';
        card.appendChild(genres);

        // return element instead of outerHTML
        return card;
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