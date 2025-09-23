const { app, BrowserWindow } = require('electron');
const path = require('path');
const WindowManager = require('./window-manager');
const { setupIpcHandlers } = require('./ipc-handlers');
const LibraryManager = require('./library/library-manager');
const Database = require('./library/database');

class AniPlay {
  constructor() {
    this.windowManager = new WindowManager();
    this.libraryManager = new LibraryManager();
    this.database = new Database();
    this.isDevelopment = process.argv.includes('--development');
    this.setupApp();
  }

  setupApp() {
    app.whenReady().then(async () => {
      // Initialize database
      await this.database.init();
      
      // Initialize library manager
      await this.libraryManager.init();
      
      // Create main window
      this.windowManager.createMainWindow();
      setupIpcHandlers(this.libraryManager, this.database);
      
      if (this.isDevelopment) {
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
