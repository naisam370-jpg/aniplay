const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class MALApi {
  constructor() {
    this.pythonScript = path.join(__dirname, '../../python/mal_scraper.py');
  }

  async checkPythonDependencies() {
    try {
      // Check if Python is available
      await this.runPythonCommand(['--version']);
      
      // Check if required packages are installed
      const result = await this.runPythonCommand(['-c', 'import requests, bs4; print("Dependencies OK")']);
      console.log('✅ Python dependencies available');
      return true;
    } catch (error) {
      console.error('❌ Python dependencies missing:', error.message);
      console.log('💡 To install: cd src/python && pip3 install -r requirements.txt');
      return false;
    }
  }

  async runPythonCommand(args) {
    return new Promise((resolve, reject) => {
      const python = spawn('python3', args, { stdio: ['pipe', 'pipe', 'pipe'] });
      
      let stdout = '';
      let stderr = '';
      
      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      python.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(`Python exited with code ${code}: ${stderr}`));
        }
      });
      
      python.on('error', (error) => {
        reject(error);
      });
    });
  }

  async searchAnime(query) {
    try {
      console.log(`🔍 Python MAL search for: ${query}`);
      
      // Check dependencies first
      const depsOK = await this.checkPythonDependencies();
      if (!depsOK) {
        return this.createFallbackData(query, 'Python dependencies missing');
      }
      
      const result = await this.runPythonCommand([this.pythonScript, 'search', query]);
      
      // Parse JSON result
      const animeData = JSON.parse(result.stdout);
      
      console.log(`✅ Python search result: ${animeData.title}`);
      return animeData;
      
    } catch (error) {
      console.error(`❌ Python search error:`, error.message);
      return this.createFallbackData(query, error.message);
    }
  }

  async downloadImage(imageUrl) {
    try {
      console.log(`📥 Python image download: ${imageUrl}`);
      
      const python = spawn('python3', [this.pythonScript, 'download', imageUrl], {
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      const chunks = [];
      let stderr = '';
      
      python.stdout.on('data', (chunk) => {
        chunks.push(chunk);
      });
      
      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      return new Promise((resolve, reject) => {
        python.on('close', (code) => {
          if (code === 0 && chunks.length > 0) {
            const buffer = Buffer.concat(chunks);
            console.log(`✅ Downloaded ${buffer.length} bytes`);
            resolve(buffer);
          } else {
            reject(new Error(`Download failed: ${stderr}`));
          }
        });
        
        python.on('error', (error) => {
          reject(error);
        });
      });
      
    } catch (error) {
      console.error(`❌ Python download error:`, error);
      throw error;
    }
  }

  createFallbackData(query, errorMsg = '') {
    return {
      title: query,
      synopsis: `No MyAnimeList data available for "${query}".${errorMsg ? ' Error: ' + errorMsg : ''}`,
      score: 0,
      episodes: 0,
      status: 'Unknown',
      genres: [],
      year: null,
      image_url: null
    };
  }
}

module.exports = MALApi;