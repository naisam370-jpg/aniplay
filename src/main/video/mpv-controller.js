const { spawn } = require('child_process');
const { EventEmitter } = require('events');
const fs = require('fs');
const path = require('path');
const os = require('os');

class MPVController extends EventEmitter {
  constructor() {
    super();
    this.mpvProcess = null;
    this.isInitialized = false;
    this.socketPath = path.join(os.tmpdir(), 'aniplay-mpv-socket');
    this.currentFile = null;
  }

  async init() {
    try {
      // Check if MPV is available
      await this.checkMPVAvailability();
      this.isInitialized = true;
      console.log('MPV controller initialized successfully');
    } catch (error) {
      console.error('Failed to initialize MPV:', error);
      throw error;
    }
  }

  checkMPVAvailability() {
    return new Promise((resolve, reject) => {
      const mpvCheck = spawn('mpv', ['--version'], { stdio: 'pipe' });
      
      mpvCheck.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error('MPV is not installed or not accessible'));
        }
      });

      mpvCheck.on('error', (error) => {
        reject(new Error('MPV is not installed. Please install MPV: sudo apt install mpv'));
      });
    });
  }

  async loadVideo(filePath) {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      // Kill existing process if running
      if (this.mpvProcess) {
        this.mpvProcess.kill();
      }

      // Remove old socket if exists
      try {
        fs.unlinkSync(this.socketPath);
      } catch (e) {
        // Socket didn't exist, that's fine
      }

      // Start MPV with IPC socket
      this.mpvProcess = spawn('mpv', [
        '--input-ipc-server=' + this.socketPath,
        '--idle',
        '--force-window',
        '--keep-open=always',
        filePath
      ], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.currentFile = filePath;

      this.mpvProcess.on('close', (code) => {
        console.log(`MPV process closed with code ${code}`);
        this.emit('stopped');
      });

      this.mpvProcess.on('error', (error) => {
        console.error('MPV process error:', error);
        this.emit('error', error);
      });

      // Wait a bit for MPV to start
      await new Promise(resolve => setTimeout(resolve, 1000));

      return { success: true, file: filePath };
      
    } catch (error) {
      console.error('Error loading video:', error);
      return { success: false, error: error.message };
    }
  }

  async sendCommand(command) {
    if (!this.mpvProcess || this.mpvProcess.killed) {
      throw new Error('MPV process not running');
    }

    return new Promise((resolve, reject) => {
      const net = require('net');
      const client = net.createConnection(this.socketPath);
      
      client.on('connect', () => {
        client.write(JSON.stringify(command) + '\n');
      });

      client.on('data', (data) => {
        try {
          const response = JSON.parse(data.toString());
          client.end();
          resolve(response);
        } catch (e) {
          client.end();
          reject(new Error('Invalid response from MPV'));
        }
      });

      client.on('error', (error) => {
        reject(error);
      });

      // Timeout after 5 seconds
      setTimeout(() => {
        if (!client.destroyed) {
          client.destroy();
          reject(new Error('Command timeout'));
        }
      }, 5000);
    });
  }

  async play() {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      if (!this.mpvProcess || this.mpvProcess.killed) {
        throw new Error('No video loaded');
      }

      await this.sendCommand({ command: ['set_property', 'pause', false] });
      return { success: true };
    } catch (error) {
      console.error('Error playing:', error);
      return { success: false, error: error.message };
    }
  }

  async pause() {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      if (!this.mpvProcess || this.mpvProcess.killed) {
        throw new Error('No video loaded');
      }

      await this.sendCommand({ command: ['set_property', 'pause', true] });
      return { success: true };
    } catch (error) {
      console.error('Error pausing:', error);
      return { success: false, error: error.message };
    }
  }

  async seek(time) {
    if (!this.isInitialized) throw new Error('MPV not initialized');
    
    try {
      if (!this.mpvProcess || this.mpvProcess.killed) {
        throw new Error('No video loaded');
      }

      await this.sendCommand({ command: ['set_property', 'time-pos', time] });
      return { success: true };
    } catch (error) {
      console.error('Error seeking:', error);
      return { success: false, error: error.message };
    }
  }

  async getStatus() {
    if (!this.isInitialized || !this.mpvProcess || this.mpvProcess.killed) {
      return null;
    }
    
    try {
      const response = await this.sendCommand({ command: ['get_property', 'time-pos'] });
      return response.data;
    } catch (error) {
      console.error('Error getting status:', error);
      return null;
    }
  }

  async stop() {
    if (this.mpvProcess && !this.mpvProcess.killed) {
      this.mpvProcess.kill();
      this.mpvProcess = null;
      this.currentFile = null;
    }
    
    // Clean up socket
    try {
      fs.unlinkSync(this.socketPath);
    } catch (e) {
      // Socket didn't exist, that's fine
    }
  }

  destroy() {
    this.stop();
  }
}

module.exports = MPVController;
