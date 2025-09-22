const mpv = require('node-mpv');
const { EventEmitter } = require('events');

class MPVController extends EventEmitter {
  constructor() {
    super();
    this.player = null;
    this.isInitialized = false;
    this.init();
  }

  async init() {
    try {
      this.player = new mpv({
        debug: false,
        verbose: false,
        audio_only: false
      });

      await this.player.start();
      this.isInitialized = true;
      
      // Set up event listeners
      this.setupEventListeners();
      
      console.log('MPV initialized successfully');
    } catch (error) {
      console.error('Failed to initialize MPV:', error);
      throw error;
    }
  }

  setupEventListeners() {
    this.player.on('statuschange', (status) => {
      this.emit('status', status);
    });

    this.player.on('stopped', () => {
      this.emit('stopped');
    });

    this.player.on('seek', () => {
      this.emit('seek');
    });
  }

  async loadVideo(filePath) {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      await this.player.load(filePath);
      return { success: true, file: filePath };
    } catch (error) {
      console.error('Error loading video:', error);
      return { success: false, error: error.message };
    }
  }

  async play() {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      await this.player.play();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async pause() {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      await this.player.pause();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async seek(time) {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      await this.player.seek(time);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getStatus() {
    if (!this.isInitialized) return null;
    
    try {
      return await this.player.getProperty('time-pos');
    } catch (error) {
      return null;
    }
  }
}

module.exports = MPVController;
