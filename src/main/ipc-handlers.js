const { ipcMain, dialog } = require('electron');
const MPVController = require('./video/mpv-controller');
const events = require('../shared/events');
const fs = require('fs').promises;
const fsSync = require('fs');
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

  // Read local image file and return data URL (base64) to renderer
  // Tries several candidate locations (absolute, library covers folder, project assets)
  ipcMain.handle('file:read-base64', async (event, filePath) => {
    if (!filePath) return null;
    try {
      const candidates = [];
      if (path.isAbsolute(filePath)) candidates.push(filePath);
      if (/^[A-Za-z]:\\/.test(filePath)) {
        const drive = filePath[0].toLowerCase();
        const rest = filePath.slice(2).replace(/\\/g, '/');
        candidates.push(`/mnt/${drive}${rest}`);
      }
      candidates.push(path.join(process.cwd(), filePath));
      candidates.push(path.join(process.cwd(), 'covers', filePath));
      candidates.push(path.join(process.cwd(), 'src', 'renderer', 'assets', 'img', filePath));
      candidates.push(path.join(process.cwd(), 'assets', 'img', filePath));
      if (typeof libraryManager !== 'undefined' && libraryManager && libraryManager.coversPath) {
        candidates.unshift(path.join(libraryManager.coversPath, filePath));
      }

      for (const p of Array.from(new Set(candidates))) {
        try {
          const s = await fs.stat(p);
          console.log(`file:read-base64: trying candidate ${p} — size=${s.size} mode=${s.mode}`);
          const buf = await fs.readFile(p);
          console.log(`file:read-base64: read ${buf.length} bytes from ${p}`);
          const ext = path.extname(p).toLowerCase();
          const mimeMap = { '.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.gif':'image/gif','.webp':'image/webp','.svg':'image/svg+xml' };
          const mime = mimeMap[ext] || 'application/octet-stream';
          const dataUrl = `data:${mime};base64,${buf.toString('base64')}`;
          console.log(`file:read-base64 -> matched ${p} (dataUrl length=${dataUrl.length})`);
          return dataUrl;
        } catch (err) {
          console.warn(`file:read-base64: candidate ${p} failed: ${err.message}`);
          // try next
        }
      }

      console.warn('file:read-base64: no file found for', filePath);
      return null;
    } catch (err) {
      console.error('file:read-base64 error for', filePath, err);
      return null;
    }
  });

  ipcMain.handle('file:probe', async (event, filePath) => {
    const result = { requested: filePath, candidates: [], errors: [] };
    if (!filePath) return { error: 'no path' };

    // convert windows -> /mnt mapping for WSL if needed
    const toWsl = (p) => {
      if (/^[A-Za-z]:\\/.test(p)) {
        const drive = p[0].toLowerCase();
        const rest = p.slice(2).replace(/\\/g, '/');
        return `/mnt/${drive}${rest}`;
      }
      return p;
    };

    const candidates = [];
    if (path.isAbsolute(filePath)) candidates.push(filePath);
    candidates.push(toWsl(filePath));
    candidates.push(path.join(process.cwd(), filePath));
    candidates.push(path.join(process.cwd(), 'covers', filePath));
    if (typeof libraryManager !== 'undefined' && libraryManager && libraryManager.coversPath) {
      candidates.push(path.join(libraryManager.coversPath, filePath));
    }
    candidates.push(path.join(process.cwd(), 'src', 'renderer', 'assets', 'img', filePath));
    candidates.push(path.join(process.cwd(), 'assets', 'img', filePath));

    for (const p of Array.from(new Set(candidates))) {
      const info = { path: p, exists: false, stat: null, readable: false };
      result.candidates.push(info);
      try {
        const s = await fs.stat(p);
        info.exists = true;
        info.stat = { size: s.size, mode: s.mode, uid: s.uid, gid: s.gid };
        // sync access check (permission bits)
        try {
          fsSync.accessSync(p, fsSync.constants.R_OK);
          info.readable = true;
        } catch (accErr) {
          info.readable = false;
          result.errors.push(`not readable: ${p} -> ${accErr.message}`);
        }
      } catch (err) {
        result.errors.push(`stat failed: ${p} -> ${err.message}`);
      }
    }

    // Helpful diagnostics in main log
    console.log('file:probe result for', filePath, JSON.stringify(result, null, 2));
    return result;
  });
}

module.exports = { setupIpcHandlers };