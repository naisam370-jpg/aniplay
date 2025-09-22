// AniPlay Main Renderer Script
const { ipcRenderer } = require('electron');
const events = require('../shared/events');

class AniPlayApp {
    constructor() {
        this.isInitialized = false;
        this.currentFile = null;
        this.init();
    }

    async init() {
        console.log('Initializing AniPlay...');
        
        try {
            await ipcRenderer.invoke('app:init');
            this.isInitialized = true;
            this.setupEventListeners();
            console.log('AniPlay initialized successfully');
        } catch (error) {
            console.error('Failed to initialize AniPlay:', error);
        }
    }

    setupEventListeners() {
        // File open button
        document.getElementById('openFile').addEventListener('click', () => {
            this.openFile();
        });

        // Drag and drop
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                this.loadVideo(files[0].path);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    async openFile() {
        try {
            const filePath = await ipcRenderer.invoke('file:open');
            if (filePath) {
                await this.loadVideo(filePath);
            }
        } catch (error) {
            console.error('Error opening file:', error);
        }
    }

    async loadVideo(filePath) {
        if (!this.isInitialized) {
            console.error('App not initialized');
            return;
        }

        try {
            console.log('Loading video:', filePath);
            const result = await ipcRenderer.invoke(events.VIDEO_LOAD, filePath);
            
            if (result.success) {
                this.currentFile = filePath;
                this.updateUI('loaded');
                console.log('Video loaded successfully');
            } else {
                console.error('Failed to load video:', result.error);
                this.showError('Failed to load video: ' + result.error);
            }
        } catch (error) {
            console.error('Error loading video:', error);
            this.showError('Error loading video');
        }
    }

    updateUI(state) {
        const placeholder = document.querySelector('.video-placeholder');
        const playPauseBtn = document.getElementById('playPause');
        const progressBar = document.getElementById('progressBar');

        switch (state) {
            case 'loaded':
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
                playPauseBtn.disabled = false;
                progressBar.disabled = false;
                break;
            case 'playing':
                playPauseBtn.innerHTML = '<span class="icon">⏸️</span>';
                break;
            case 'paused':
                playPauseBtn.innerHTML = '<span class="icon">▶️</span>';
                break;
        }
    }

    showError(message) {
        // Simple error display - could be enhanced with a proper modal
        console.error(message);
        alert(message);
    }

    handleKeyboard(e) {
        if (!this.currentFile) return;

        switch (e.code) {
            case 'Space':
                e.preventDefault();
                document.getElementById('playPause').click();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                // Seek backward
                break;
            case 'ArrowRight':
                e.preventDefault();
                // Seek forward
                break;
        }
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aniplay = new AniPlayApp();
});
