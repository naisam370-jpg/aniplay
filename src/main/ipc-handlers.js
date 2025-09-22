const { ipcMain } = require('electron');
const MPVController = require('./video/mpv-controller');
const events = require('../shared/events');

let mpvController = null;

function setupIpcHandlers() {
  // Initialize MPV controller
  ipcMain.handle('app:init', async () => {
    mpvController = new MPVController();
    return { success: true };
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
  ipcMain.handle('file:open', async () => {
    const { dialog } = require('electron');
    const result = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: [
        { name: 'Video Files', extensions: ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    
    return result.canceled ? null : result.filePaths[0];
  });
}

module.exports = { setupIpcHandlers };
