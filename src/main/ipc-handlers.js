const { ipcMain, dialog } = require('electron');
const MPVController = require('./video/mpv-controller');
const events = require('../shared/events');
const path = require('path');

let mpvController = null;

function setupIpcHandlers(libraryManager, database) {
  // App initialization
  ipcMain.handle('app:init', async () => {
    mpvController = new MPVController();
    return { success: true };
  });

  // Library management
  ipcMain.handle('library:scan', async () => {
    try {
      const result = await libraryManager.scanLibrary();
      return result;
    } catch (error) {
      console.error('Library scan error:', error);
      return { success: false, error: error.message };
    }
  });

  // NEW: Refresh library (rescan existing + add new)
  ipcMain.handle('library:refresh', async () => {
    try {
      console.log('🔄 Starting library refresh...');
      const result = await libraryManager.refreshLibrary();
      return result;
    } catch (error) {
      console.error('Library refresh error:', error);
      return { success: false, error: error.message };
    }
  });

  // NEW: Clear database and rescan everything
  ipcMain.handle('library:reset', async () => {
    try {
      console.log('🗑️ Resetting library database...');
      const result = await libraryManager.resetLibrary();
      return result;
    } catch (error) {
      console.error('Library reset error:', error);
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('library:get-all', async () => {
    try {
      return await database.getAllAnime();
    } catch (error) {
      console.error('Get library error:', error);
      return [];
    }
  });

  ipcMain.handle('library:get-anime', async (event, animeId) => {
    try {
      return await database.getAnimeById(animeId);
    } catch (error) {
      console.error('Get anime error:', error);
      return null;
    }
  });

  ipcMain.handle('library:search', async (event, query) => {
    try {
      return await libraryManager.searchLibrary(query);
    } catch (error) {
      console.error('Search error:', error);
      return [];
    }
  });

  // Video controls
  ipcMain.handle(events.VIDEO_LOAD, async (event, filePath) => {
    if (!mpvController) throw new Error('MPV not initialized');
    return await mpvController.loadVideo(filePath);
  });

  ipcMain.handle(events.VIDEO_PLAY, async () => {
    if (!mpvController) throw new Error('MPV not initialized');
    return await mpvController.play();
  });

  ipcMain.handle(events.VIDEO_PAUSE, async () => {
    if (!mpvController) throw new Error('MPV not initialized');
    return await mpvController.pause();
  });

  ipcMain.handle(events.VIDEO_SEEK, async (event, time) => {
    if (!mpvController) throw new Error('MPV not initialized');
    return await mpvController.seek(time);
  });

  // File operations
  ipcMain.handle('file:select-library', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory'],
      title: 'Select Anime Library Directory'
    });
    
    return result.canceled ? null : result.filePaths[0];
  });

  ipcMain.handle('anime:get-episodes', async (event, animePath) => {
    try {
      return await libraryManager.getAnimeEpisodes(animePath);
    } catch (error) {
      console.error('Get episodes error:', error);
      return [];
    }
  });
}

module.exports = { setupIpcHandlers };