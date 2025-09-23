const { BrowserWindow } = require('electron');
const path = require('path');

class WindowManager {
  constructor() {
    this.mainWindow = null;
  }

  createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1000,
      minHeight: 700,
      title: 'AniPlay - Anime Library Manager',
      icon: path.join(__dirname, '../../assets/icons/icon.png'),
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false,
        enableRemoteModule: true
      },
      titleBarStyle: 'default',
      show: false,
      backgroundColor: '#1a1a1a'
    });

    this.mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    return this.mainWindow;
  }

  createPlayerWindow(animeInfo) {
    const playerWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      title: `AniPlay - ${animeInfo.title}`,
      parent: this.mainWindow,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      },
      backgroundColor: '#000000'
    });

    playerWindow.loadFile(path.join(__dirname, '../renderer/player.html'));
    
    // Pass anime info to player window
    playerWindow.webContents.once('did-finish-load', () => {
      playerWindow.webContents.send('anime-info', animeInfo);
    });

    return playerWindow;
  }
}

module.exports = WindowManager;
