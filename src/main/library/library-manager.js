const fs = require('fs').promises;
const path = require('path');
const MALApi = require('../api/mal-api');
const Database = require('./database');
const Fuse = require('fuse.js');

class LibraryManager {
  constructor() {
    this.libraryPath = path.join(process.cwd(), 'anime-library');
    this.coversPath = path.join(process.cwd(), 'covers');
    this.malApi = new MALApi();
    this.database = new Database();
    this.animeCache = [];
  }

  async init() {
    // Ensure directories exist
    await this.ensureDirectories();
    
    console.log('Library Manager initialized');
    console.log('Library path:', this.libraryPath);
    console.log('Covers path:', this.coversPath);
  }

  async ensureDirectories() {
    try {
      await fs.access(this.libraryPath);
    } catch {
      await fs.mkdir(this.libraryPath, { recursive: true });
      console.log('Created anime-library directory');
    }

    try {
      await fs.access(this.coversPath);
    } catch {
      await fs.mkdir(this.coversPath, { recursive: true });
      console.log('Created covers directory');
    }
  }

  async scanLibrary() {
    console.log('Starting library scan...');
    
    try {
      const animeFolders = await this.getAnimeFolders();
      const results = {
        total: animeFolders.length,
        processed: 0,
        errors: []
      };

      for (const folder of animeFolders) {
        try {
          console.log(`Processing: ${folder}`);
          
          // Check if anime already exists in database
          const existing = await this.database.getAnimeByPath(folder);
          
          if (!existing) {
            // Search MyAnimeList for this anime
            const malData = await this.malApi.searchAnime(folder);
            
            if (malData) {
              // Download cover if needed
              const coverPath = await this.downloadCover(malData);
              
              // Save to database
              const animeData = {
                title: malData.title,
                path: folder,
                cover: coverPath,
                description: malData.synopsis,
                score: malData.score,
                episodes: malData.episodes,
                status: malData.status,
                genres: malData.genres,
                year: malData.year
              };
              
              await this.database.addAnime(animeData);
              console.log(`Added: ${malData.title}`);
            } else {
              console.log(`No MAL data found for: ${folder}`);
              
              // Add basic entry without MAL data
              await this.database.addAnime({
                title: folder,
                path: folder,
                cover: null,
                description: 'No description available',
                score: 0,
                episodes: 0,
                status: 'Unknown',
                genres: [],
                year: null
              });
            }
          }
          
          results.processed++;
          
        } catch (error) {
          console.error(`Error processing ${folder}:`, error);
          results.errors.push({ folder, error: error.message });
        }
      }

      // Update cache
      this.animeCache = await this.database.getAllAnime();
      
      console.log(`Library scan complete: ${results.processed}/${results.total} processed`);
      return results;
      
    } catch (error) {
      console.error('Library scan failed:', error);
      throw error;
    }
  }

  async getAnimeFolders() {
    try {
      const items = await fs.readdir(this.libraryPath);
      const folders = [];
      
      for (const item of items) {
        const itemPath = path.join(this.libraryPath, item);
        const stat = await fs.stat(itemPath);
        
        if (stat.isDirectory() && item !== '.gitkeep') {
          folders.push(item);
        }
      }
      
      return folders;
    } catch (error) {
      console.error('Error reading library directory:', error);
      return [];
    }
  }

  async downloadCover(malData) {
    if (!malData.image_url) return null;
    
    try {
      const coverFilename = `${this.sanitizeFilename(malData.title)}.jpg`;
      const coverPath = path.join(this.coversPath, coverFilename);
      
      // Check if cover already exists
      try {
        await fs.access(coverPath);
        return coverFilename; // Cover already exists
      } catch {
        // Cover doesn't exist, download it
      }
      
      const response = await this.malApi.downloadImage(malData.image_url);
      await fs.writeFile(coverPath, response);
      
      console.log(`Downloaded cover: ${coverFilename}`);
      return coverFilename;
      
    } catch (error) {
      console.error('Error downloading cover:', error);
      return null;
    }
  }

  sanitizeFilename(filename) {
    return filename.replace(/[<>:"/\\|?*]/g, '_').trim();
  }

  async searchLibrary(query) {
    if (!this.animeCache.length) {
      this.animeCache = await this.database.getAllAnime();
    }

    if (!query || query.trim() === '') {
      return this.animeCache;
    }

    const fuse = new Fuse(this.animeCache, {
      keys: ['title', 'genres'],
      threshold: 0.3
    });

    const results = fuse.search(query);
    return results.map(result => result.item);
  }

  async getAnimeEpisodes(animePath) {
    const fullPath = path.join(this.libraryPath, animePath);
    
    try {
      const episodes = [];
      await this.scanForEpisodes(fullPath, episodes, '');
      
      // Sort episodes naturally
      episodes.sort((a, b) => {
        const aMatch = a.name.match(/(\d+)/);
        const bMatch = b.name.match(/(\d+)/);
        
        if (aMatch && bMatch) {
          return parseInt(aMatch[1]) - parseInt(bMatch[1]);
        }
        
        return a.name.localeCompare(b.name);
      });
      
      return episodes;
      
    } catch (error) {
      console.error('Error getting episodes:', error);
      return [];
    }
  }

  async scanForEpisodes(dirPath, episodes, relativePath) {
    const items = await fs.readdir(dirPath);
    
    for (const item of items) {
      const itemPath = path.join(dirPath, item);
      const stat = await fs.stat(itemPath);
      const currentRelativePath = relativePath ? path.join(relativePath, item) : item;
      
      if (stat.isDirectory()) {
        // Recursively scan subdirectories
        await this.scanForEpisodes(itemPath, episodes, currentRelativePath);
      } else if (this.isVideoFile(item)) {
        episodes.push({
          name: item,
          path: itemPath,
          relativePath: currentRelativePath,
          size: stat.size
        });
      }
    }
  }

  isVideoFile(filename) {
    const videoExtensions = [
      '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
      '.m4v', '.3gp', '.ogv', '.ts', '.mpg', '.mpeg', '.m2v'
    ];
    
    const ext = path.extname(filename).toLowerCase();
    return videoExtensions.includes(ext);
  }
}

module.exports = LibraryManager;
