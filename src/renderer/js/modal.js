// Modal management - removed duplicate ipcRenderer declaration

class ModalManager {
    constructor() {
        this.currentAnime = null;
        this.setupModalListeners();
    }

    setupModalListeners() {
        // Settings modal
        const settingsBtn = document.getElementById('settingsBtn');
        const closeSettings = document.getElementById('closeSettings');
        const settingsModal = document.getElementById('settingsModal');
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                console.log('Settings button clicked'); // Debug
                this.openSettingsModal();
            });
        }

        if (closeSettings) {
            closeSettings.addEventListener('click', () => {
                this.closeSettingsModal();
            });
        }

        // Close modal when clicking backdrop
        if (settingsModal) {
            settingsModal.addEventListener('click', (e) => {
                if (e.target.id === 'settingsModal') {
                    this.closeSettingsModal();
                }
            });
        }

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Escape') {
                this.closeAllModals();
            }
        });

        // Other modal buttons
        const saveSettings = document.getElementById('saveSettings');
        const cancelSettings = document.getElementById('cancelSettings');
        
        if (saveSettings) {
            saveSettings.addEventListener('click', () => {
                this.saveSettings();
            });
        }

        if (cancelSettings) {
            cancelSettings.addEventListener('click', () => {
                this.closeSettingsModal();
            });
        }
    }

    openSettingsModal() {
        console.log('Opening settings modal'); // Debug
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.remove('hidden');
            console.log('Settings modal should be visible now'); // Debug
        } else {
            console.error('Settings modal not found'); // Debug
        }
    }

    closeSettingsModal() {
        console.log('Closing settings modal'); // Debug
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    closeAllModals() {
        this.closeSettingsModal();
        // Close anime modal if it exists
        const animeModal = document.getElementById('animeModal');
        if (animeModal) {
            animeModal.classList.add('hidden');
        }
    }

    saveSettings() {
        console.log('Saving settings...'); // Debug
        // Add your settings save logic here
        this.closeSettingsModal();
    }
    openAnimeModal() {
        console.log('Opening anime modal'); // Debug
        const modal = document.getElementById('animeModal');
        if (modal) {
            modal.classList.remove('hidden');
            console.log('Anime modal should be visible now'); // Debug
        } else {
            console.error('Anime modal not found'); // Debug
        }
    }
    
}

// Initialize modal manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing modal manager'); // Debug
    window.modalManager = new ModalManager();
});