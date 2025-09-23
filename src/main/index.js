const { app, BrowserWindow } = require('electron');
const path = require('path');
const WindowManager = require('./window-manager');
const { setupIpcHandlers } = require('./ipc-handlers');
const LibraryManager = require('./library/library-manager');
const Database = require('./library/database');

class AniPlay {
  constructor() {
    this.windowManager = new WindowManager();
    this.libraryManager = null;
    this.database = null;
    this.isDevelopment = process.argv.includes('--development');
    this.setupApp();
  }

  setupApp() {
    app.whenReady().then(async () => {
      try {
        // Initialize database first
        this.database = new Database();
        await this.database.init();
        
        // Initialize library manager with database reference
        this.libraryManager = new LibraryManager();
        this.libraryManager.database = this.database; // Pass database reference
        await this.libraryManager.init();
        
        // Create main window
        this.windowManager.createMainWindow();
        setupIpcHandlers(this.libraryManager, this.database);
        
        if (this.isDevelopment) {
          this.windowManager.mainWindow.webContents.openDevTools();
        }
      } catch (error) {
        console.error('Failed to initialize AniPlay:', error);
      }
    });

    app.on('window-all-closed', () => {
      if (this.database) {
        this.database.close();
      }
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