const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs').promises;

class Database {
  constructor() {
    this.dbPath = path.join(process.cwd(), 'data', 'aniplay.db');
    this.db = null;
  }

  async init() {
    // Ensure data directory exists
    const dataDir = path.dirname(this.dbPath);
    try {
      await fs.access(dataDir);
    } catch {
      await fs.mkdir(dataDir, { recursive: true });
    }

    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          console.error('Database connection error:', err);
          reject(err);
        } else {
          console.log('Connected to SQLite database');
          this.createTables().then(resolve).catch(reject);
        }
      });
    });
  }

  async createTables() {
    return new Promise((resolve, reject) => {
      const createAnimeTable = `
        CREATE TABLE IF NOT EXISTS anime (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          path TEXT UNIQUE NOT NULL,
          cover TEXT,
          description TEXT,
          score REAL,
          episodes INTEGER,
          status TEXT,
          genres TEXT,
          year INTEGER,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `;

      const createWatchHistoryTable = `
        CREATE TABLE IF NOT EXISTS watch_history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          anime_id INTEGER,
          episode_path TEXT,
          position REAL,
          duration REAL,
          watched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (anime_id) REFERENCES anime (id)
        )
      `;

      this.db.run(createAnimeTable, (err) => {
        if (err) {
          reject(err);
          return;
        }

        this.db.run(createWatchHistoryTable, (err) => {
          if (err) {
            reject(err);
            return;
          }

          console.log('Database tables created/verified');
          resolve();
        });
      });
    });
  }

  async addAnime(animeData) {
    // Check if database is still connected
    if (!this.db) {
      throw new Error('Database not connected');
    }

    return new Promise((resolve, reject) => {
      const sql = `
        INSERT OR REPLACE INTO anime 
        (title, path, cover, description, score, episodes, status, genres, year, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
      `;

      const genres = Array.isArray(animeData.genres) 
        ? animeData.genres.join(',') 
        : animeData.genres;

      this.db.run(sql, [
        animeData.title,
        animeData.path,
        animeData.cover,
        animeData.description,
        animeData.score,
        animeData.episodes,
        animeData.status,
        genres,
        animeData.year
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID, ...animeData });
        }
      });
    });
  }

  // Upsert / compatibility helpers expected by LibraryManager
  async upsertAnime(animeData) {
    return this.addAnime(animeData);
  }
  
  async insertOrReplace(animeData) {
    return this.addAnime(animeData);
  }
  
  async insertAnime(animeData) {
    // Insert only, fail if path already exists
    if (!this.db) throw new Error('Database not connected');

    const existing = await this.getAnimeByPath(animeData.path);
    if (existing) throw new Error('Anime already exists at path: ' + animeData.path);

    return new Promise((resolve, reject) => {
      const sql = `
        INSERT INTO anime 
        (title, path, cover, description, score, episodes, status, genres, year, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
      `;
      const genres = Array.isArray(animeData.genres) 
        ? animeData.genres.join(',') 
        : animeData.genres;

      this.db.run(sql, [
        animeData.title,
        animeData.path,
        animeData.cover,
        animeData.description,
        animeData.score,
        animeData.episodes,
        animeData.status,
        genres,
        animeData.year
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID, ...animeData });
        }
      });
    });
  }

  async updateAnime(animeData) {
    if (!this.db) throw new Error('Database not connected');

    const genres = Array.isArray(animeData.genres)
      ? animeData.genres.join(',')
      : animeData.genres;

    const db = this.db; // capture DB reference for use inside callbacks

    return new Promise((resolve, reject) => {
      const sql = `
        UPDATE anime SET
          title = ?,
          cover = ?,
          description = ?,
          score = ?,
          episodes = ?,
          status = ?,
          genres = ?,
          year = ?,
          updated_at = CURRENT_TIMESTAMP
        WHERE path = ?
      `;
      const params = [
        animeData.title,
        animeData.cover,
        animeData.description,
        animeData.score,
        animeData.episodes,
        animeData.status,
        genres,
        animeData.year,
        animeData.path
      ];

      // Use a normal function callback so sqlite sets `this` to the Statement
      db.run(sql, params, function(err) {
        if (err) {
          return reject(err);
        }

        // `this` is the Statement; check changes from the statement
        if (this.changes === 0) {
          // Nothing updated — try fallback by id if provided
          if (animeData.id) {
            const sqlById = `
              UPDATE anime SET
                title = ?, path = ?, cover = ?, description = ?, score = ?, episodes = ?, status = ?, genres = ?, year = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?
            `;
            const paramsById = [
              animeData.title,
              animeData.path,
              animeData.cover,
              animeData.description,
              animeData.score,
              animeData.episodes,
              animeData.status,
              genres,
              animeData.year,
              animeData.id
            ];
            db.run(sqlById, paramsById, function(err2) {
              if (err2) return reject(err2);
              // fetch updated row
              db.get('SELECT * FROM anime WHERE id = ?', [animeData.id], (err3, row) => {
                if (err3) return reject(err3);
                resolve({
                  ...row,
                  genres: row && row.genres ? row.genres.split(',') : []
                });
              });
            });
          } else {
            // No matching row
            return resolve(null);
          }
        } else {
          // Return updated row (fetch by path)
          db.get('SELECT * FROM anime WHERE path = ?', [animeData.path], (err2, row) => {
            if (err2) return reject(err2);
            resolve({
              ...row,
              genres: row && row.genres ? row.genres.split(',') : []
            });
          });
        }
      });
    });
  }

  // Compatibility alias used by LibraryManager
  async findAnimeByPath(p) {
    return this.getAnimeByPath(p);
  }

  async getAllAnime() {
    // Check if database is still connected
    if (!this.db) {
      throw new Error('Database not connected');
    }
    
    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM anime ORDER BY title ASC';
      
      this.db.all(sql, [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const anime = rows.map(row => ({
            ...row,
            genres: row.genres ? row.genres.split(',') : []
          }));
          resolve(anime);
        }
      });
    });
  }

  async getAnimeById(id) {
    // Check if database is still connected
    if (!this.db) {
      throw new Error('Database not connected');
    }

    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM anime WHERE id = ?';
      
      this.db.get(sql, [id], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          resolve({
            ...row,
            genres: row.genres ? row.genres.split(',') : []
          });
        } else {
          resolve(null);
        }
      });
    });
  }

  async getAnimeByPath(path) {
    // Check if database is still connected
    if (!this.db) {
      throw new Error('Database not connected');
    }

    return new Promise((resolve, reject) => {
      const sql = 'SELECT * FROM anime WHERE path = ?';
      
      this.db.get(sql, [path], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          resolve({
            ...row,
            genres: row.genres ? row.genres.split(',') : []
          });
        } else {
          resolve(null);
        }
      });
    });
  }

  async updateWatchHistory(animeId, episodePath, position, duration) {
    // Check if database is still connected
    if (!this.db) {
      throw new Error('Database not connected');
    }

    return new Promise((resolve, reject) => {
      const sql = `
        INSERT OR REPLACE INTO watch_history 
        (anime_id, episode_path, position, duration, watched_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
      `;

      this.db.run(sql, [animeId, episodePath, position, duration], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID });
        }
      });
    });
  }

  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) {
          console.error('Error closing database:', err);
        } else {
          console.log('Database connection closed');
        }
      });
    }
  }
}

module.exports = Database;