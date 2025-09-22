// Video Player Controls
const { ipcRenderer } = require('electron');
const events = require('../shared/events');

class VideoPlayer {
    constructor() {
        this.isPlaying = false;
        this.duration = 0;
        this.currentTime = 0;
        this.volume = 70;
        this.init();
    }

    init() {
        this.setupControls();
    }

    setupControls() {
        // Play/Pause button
        const playPauseBtn = document.getElementById('playPause');
        playPauseBtn.addEventListener('click', () => {
            this.togglePlayPause();
        });

        // Progress bar
        const progressBar = document.getElementById('progressBar');
        progressBar.addEventListener('input', (e) => {
            this.seek(e.target.value);
        });

        // Volume controls
        const volumeSlider = document.getElementById('volumeSlider');
        volumeSlider.addEventListener('input', (e) => {
            this.setVolume(e.target.value);
        });

        const volumeBtn = document.getElementById('volumeBtn');
        volumeBtn.addEventListener('click', () => {
            this.toggleMute();
        });
    }

    async togglePlayPause() {
        try {
            if (this.isPlaying) {
                await ipcRenderer.invoke(events.VIDEO_PAUSE);
                this.isPlaying = false;
                window.aniplay.updateUI('paused');
            } else {
                await ipcRenderer.invoke(events.VIDEO_PLAY);
                this.isPlaying = true;
                window.aniplay.updateUI('playing');
            }
        } catch (error) {
            console.error('Error toggling playback:', error);
        }
    }

    async seek(position) {
        try {
            const time = (position / 100) * this.duration;
            await ipcRenderer.invoke(events.VIDEO_SEEK, time);
        } catch (error) {
            console.error('Error seeking:', error);
        }
    }

    setVolume(volume) {
        this.volume = volume;
        const volumeBtn = document.getElementById('volumeBtn');
        
        if (volume == 0) {
            volumeBtn.textContent = '🔇';
        } else if (volume < 50) {
            volumeBtn.textContent = '🔉';
        } else {
            volumeBtn.textContent = '🔊';
        }
    }

    toggleMute() {
        const volumeSlider = document.getElementById('volumeSlider');
        if (this.volume > 0) {
            this.previousVolume = this.volume;
            this.setVolume(0);
            volumeSlider.value = 0;
        } else {
            const restoreVolume = this.previousVolume || 70;
            this.setVolume(restoreVolume);
            volumeSlider.value = restoreVolume;
        }
    }

    updateProgress(currentTime, duration) {
        this.currentTime = currentTime;
        this.duration = duration;

        const progressBar = document.getElementById('progressBar');
        const currentTimeEl = document.getElementById('currentTime');
        const durationEl = document.getElementById('duration');

        if (duration > 0) {
            progressBar.value = (currentTime / duration) * 100;
        }

        currentTimeEl.textContent = this.formatTime(currentTime);
        durationEl.textContent = this.formatTime(duration);
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize player when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.videoPlayer = new VideoPlayer();
});
