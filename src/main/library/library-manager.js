const fs = require('fs').promises;
const path = require('path');
const MALApi = require('../api/anilist-api'); // Use AniList API (drop-in replacement)
const Database = require('./database');
const Fuse = require('fuse.js');

class LibraryManager {
  constructor() {
    this.libraryPath = path.join(process.cwd(), 'anime-library');
    this.coversPath = path.join(process.cwd(), 'covers');
    this.malApi = new MALApi(); // AniList API
    this.database = null; // Will be set by main process
    this.animeCache = [];
  }

  /**
   * Save or update an anime record in the configured database.
   * Tries a few common method names so LibraryManager can work with different DB implementations.
   */
  async _saveAnime(record) {
    if (!this.database) throw new Error('Database not set on LibraryManager');

    if (typeof this.database.updateAnime === 'function') {
      return await this.database.updateAnime(record);
    }

    if (typeof this.database.upsertAnime === 'function') {
      return await this.database.upsertAnime(record);
    }

    if (typeof this.database.insertOrReplace === 'function') {
      return await this.database.insertOrReplace(record);
    }

    if (typeof this.database.insertAnime === 'function') {
      try {
        return await this.database.insertAnime(record);
      } catch (err) {
        // If insert failed because the record exists, try an update if available
        if (typeof this.database.findAnimeByPath === 'function' && typeof this.database.updateAnime === 'function') {
          const existing = await this.database.findAnimeByPath(record.path).catch(() => null);
          if (existing) return await this.database.updateAnime(record);
        }
        throw err;
      }
    }

    throw new Error('Database implementation missing update/upsert/insert method');
  }

  async init() {
    await this.ensureDirectories();
    
    console.log('📚 Library Manager initialized');
    console.log('📁 Library path:', this.libraryPath);
    console.log('🖼️  Covers path:', this.coversPath);
  }

  async ensureDirectories() {
    try {
      await fs.access(this.libraryPath);
    } catch {
      await fs.mkdir(this.libraryPath, { recursive: true });
      console.log('✅ Created anime-library directory');
    }

    try {
      await fs.access(this.coversPath);
    } catch {
      await fs.mkdir(this.coversPath, { recursive: true });
      console.log('✅ Created covers directory');
    }
  }

  async scanLibrary() {
    console.log('🔄 Starting library scan...');
    
    try {
      const animeFolders = await this.getAnimeFolders();
      const results = {
        total: animeFolders.length,
        processed: 0,
        errors: [],
        updated: 0,
        added: 0
      };

      for (const folder of animeFolders) {
        try {
          console.log(`\n📂 Processing: ${folder}`);
          
          // Check if anime already exists in database
          const existing = await this.database.getAnimeByPath(folder);
          
          if (existing) {
            console.log(`⏭️  Already exists: ${existing.title}`);
            results.processed++;
            continue;
          }

          // Search AniList API
          console.log(`🔍 Searching AniList for: ${folder}`);
          const malData = await this.malApi.searchAnime(folder);
          
          if (malData && malData.title) {
            // Download cover if available
            let coverPath = null;
            if (malData.image_url) {
              try {
                coverPath = await this.downloadCover(malData);
              } catch (error) {
                console.log(`⚠️  Could not download cover: ${error.message}`);
              }
            }
            
            // Save to database
            const animeData = {
              title: malData.title,
              path: folder,
              cover: coverPath,
              description: malData.synopsis || 'No description available.',
              score: malData.score || 0,
              episodes: malData.episodes || 0,
              status: malData.status || 'Unknown',
              genres: malData.genres || [],
              year: malData.year
            };
            
            await this.database.addAnime(animeData);
            results.added++;
            console.log(`✅ Added: ${malData.title} (Score: ${malData.score || 'N/A'})`);
            
          } else {
            console.log(`❌ No AniList data found for: ${folder}`);
            
            // Add basic entry without MAL data
            const basicData = {
              title: folder,
              path: folder,
              cover: null,
              description: 'No description available - could not find on AniList.',
              score: 0,
              episodes: 0,
              status: 'Unknown',
              genres: [],
              year: null
            };
            
            await this.database.addAnime(basicData);
            results.added++;
            console.log(`➕ Added basic entry: ${folder}`);
          }
          
          results.processed++;
          
          // Delay to be respectful to MAL servers
          await new Promise(resolve => setTimeout(resolve, 2000));
          
        } catch (error) {
          console.error(`❌ Error processing ${folder}:`, error);
          results.errors.push({ folder, error: error.message });
        }
      }

      // Update cache
      this.animeCache = await this.database.getAllAnime();
      
      console.log(`\n🎉 Library scan complete!`);
      console.log(`📊 Results: ${results.added} added, ${results.processed}/${results.total} processed, ${results.errors.length} errors`);
      
      return results;
      
    } catch (error) {
      console.error('❌ Library scan failed:', error);
      throw error;
    }
  }

  async refreshLibrary() {
    console.log('🔄 Starting library refresh...');
    
    try {
      const animeFolders = await this.getAnimeFolders();
      const existingAnime = await this.database.getAllAnime();
      
      const results = {
        total: animeFolders.length,
        processed: 0,
        errors: [],
        updated: 0,
        added: 0,
        removed: 0
      };

      // Check for removed anime (folders that no longer exist)
      for (const anime of existingAnime) {
        if (!animeFolders.includes(anime.path)) {
          console.log(`🗑️ Removing deleted anime: ${anime.title}`);
          try {
            await this.database.removeAnime(anime.id);
            results.removed++;
          } catch (error) {
            console.error(`❌ Error removing ${anime.title}:`, error);
            results.errors.push({ folder: anime.path, error: error.message });
          }
        }
      }

      // Process all folders
      for (const folder of animeFolders) {
        try {
          console.log(`\n📂 Processing: ${folder}`);
          
          const existing = await this.database.getAnimeByPath(folder);
          
          if (existing) {
            // Update existing anime with fresh MAL data
            console.log(`🔄 Updating existing: ${existing.title}`);
            const malData = await this.malApi.searchAnime(folder);
            
            if (malData && malData.title) {
              // Download new cover if URL changed
              let coverPath = existing.cover;
              if (malData.image_url && (!existing.cover || malData.image_url !== existing.image_url)) {
                try {
                  coverPath = await this.downloadCover(malData);
                } catch (error) {
                  console.log(`⚠️ Could not update cover: ${error.message}`);
                  coverPath = existing.cover; // Keep existing cover
                }
              }
              
              const updatedData = {
                title: malData.title,
                path: folder, // Keep original path
                cover: coverPath,
                description: malData.synopsis || existing.description,
                score: malData.score || existing.score,
                episodes: malData.episodes || existing.episodes,
                status: malData.status || existing.status,
                genres: malData.genres || existing.genres,
                year: malData.year || existing.year
              };
              
              await this.database.updateAnime(existing.id, updatedData);
              results.updated++;
              console.log(`✅ Updated: ${malData.title}`);
            } else {
              console.log(`⏭️ No new MAL data, keeping existing: ${existing.title}`);
            }
          } else {
            // Add new anime
            console.log(`➕ Adding new anime: ${folder}`);
            const malData = await this.malApi.searchAnime(folder);
            
            if (malData && malData.title) {
              let coverPath = null;
              if (malData.image_url) {
                try {
                  coverPath = await this.downloadCover(malData);
                } catch (error) {
                  console.log(`⚠️ Could not download cover: ${error.message}`);
                }
              }
              
              const animeData = {
                title: malData.title,
                path: folder,
                cover: coverPath,
                description: malData.synopsis || 'No description available.',
                score: malData.score || 0,
                episodes: malData.episodes || 0,
                status: malData.status || 'Unknown',
                genres: malData.genres || [],
                year: malData.year
              };
              
              await this.database.addAnime(animeData);
              results.added++;
              console.log(`✅ Added: ${malData.title}`);
            }
          }
          
          results.processed++;
          
          // Delay to be respectful to MAL servers
          await new Promise(resolve => setTimeout(resolve, 2000));
          
        } catch (error) {
          console.error(`❌ Error processing ${folder}:`, error);
          results.errors.push({ folder, error: error.message });
        }
      }

      // Update cache
      this.animeCache = await this.database.getAllAnime();
      
      console.log(`\n🎉 Library refresh complete!`);
      console.log(`📊 Results: ${results.added} added, ${results.updated} updated, ${results.removed} removed`);
      
      return results;
      
    } catch (error) {
      console.error('❌ Library refresh failed:', error);
      throw error;
    }
  }

  async resetLibrary() {
    console.log('🗑️ Resetting library database...');
    
    try {
      // Clear all anime from database
      await this.database.clearAllAnime();
      
      // Clear cache
      this.animeCache = [];
      
      console.log('✅ Database cleared');
      
      // Run fresh scan
      const results = await this.scanLibrary();
      
      console.log('🎉 Library reset complete!');
      return {
        ...results,
        reset: true
      };
      
    } catch (error) {
      console.error('❌ Library reset failed:', error);
      throw error;
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
        console.log(`📁 Cover already exists: ${coverFilename}`);
        return coverFilename;
      } catch {
        // Cover doesn't exist, download it
      }
      
      console.log(`📥 Downloading cover for: ${malData.title}`);
      const imageBuffer = await this.malApi.downloadImage(malData.image_url);
      await fs.writeFile(coverPath, imageBuffer);
      
      console.log(`✅ Downloaded cover: ${coverFilename}`);
      return coverFilename;
      
    } catch (error) {
      console.error(`❌ Error downloading cover for ${malData.title}:`, error);
      return null;
    }
  }

  sanitizeFilename(filename) {
    return filename
      .replace(/[<>:"/\\|?*]/g, '_')
      .replace(/\s+/g, '_')
      .trim();
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
      
      console.log(`📁 Found ${folders.length} anime folders`);
      return folders;
    } catch (error) {
      console.error('❌ Error reading library directory:', error);
      return [];
    }
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
      threshold: 0.3,
      includeScore: true
    });

    const results = fuse.search(query);
    return results.map(result => result.item);
  }
}

module.exports = LibraryManager;
