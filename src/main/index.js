const { app, BrowserWindow } = require('electron');
const path = require('path');
const WindowManager = require('./window-manager');
const { setupIpcHandlers } = require('./ipc-handlers');

class AniPlay {
  constructor() {
    this.windowManager = new WindowManager();
    this.isDevelopment = process.argv.includes('--development');
    this.setupApp();
  }

  setupApp() {
    app.whenReady().then(() => {
      this.windowManager.createMainWindow();
      setupIpcHandlers();
      
      if (this.isDevelopment) {
        // Open DevTools in development
        this.windowManager.mainWindow.webContents.openDevTools();
      }
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.windowManager.createMainWindow();
      }
    });
  }
}

new AniPlay();
