const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class MALApi {
  constructor() {
    this.pythonScript = path.join(__dirname, '../../python/mal_scraper.py');
    this.dependenciesChecked = false;
    this.dependenciesOK = false;
  }

  async checkPythonDependencies() {
    if (this.dependenciesChecked) {
      return this.dependenciesOK;
    }

    try {
      console.log('🐍 Checking Python dependencies...');
      
      // Check if Python is available
      const pythonCheck = await this.runCommand(['python3', '--version']);
      console.log('✅ Python3 available:', pythonCheck.stdout.trim());
      
      // Check if required packages are installed
      const depCheck = await this.runCommand(['python3', '-c', 'import requests, bs4; print("Dependencies OK")']);
      console.log('✅ Python dependencies:', depCheck.stdout.trim());
      
      this.dependenciesOK = true;
      this.dependenciesChecked = true;
      return true;
      
    } catch (error) {
      console.error('❌ Python dependencies missing:', error.message);
      console.log('💡 To install dependencies:');
      console.log('   cd src/python');
      console.log('   pip3 install -r requirements.txt');
      
      this.dependenciesOK = false;
      this.dependenciesChecked = true;
      return false;
    }
  }

  async runCommand(args) {
    return new Promise((resolve, reject) => {
      const [command, ...commandArgs] = args;
      const process = spawn(command, commandArgs, { 
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.dirname(this.pythonScript)
      });
      
      let stdout = '';
      let stderr = '';
      
      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      process.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          reject(new Error(`Process exited with code ${code}: ${stderr}`));
        }
      });
      
      process.on('error', (error) => {
        reject(error);
      });
    });
  }

  async searchAnime(query) {
    try {
      console.log(`🔍 Python MAL search for: "${query}"`);
      
      // Check dependencies first
      const depsOK = await this.checkPythonDependencies();
      if (!depsOK) {
        return this.createFallbackData(query, 'Python dependencies missing. Please install: pip3 install requests beautifulsoup4 lxml');
      }
      
      // Run Python scraper
      const result = await this.runCommand([
        'python3', 
        this.pythonScript, 
        'search', 
        query
      ]);
      
      // Parse JSON result
      const animeData = JSON.parse(result.stdout);
      
      console.log(`✅ Python search result: "${animeData.title}" (Score: ${animeData.score})`);
      
      // Log stderr for debugging (Python script outputs debug info there)
      if (result.stderr) {
        console.log('🐍 Python debug:', result.stderr.split('\n').slice(-3).join(' '));
      }
      
      return animeData;
      
    } catch (error) {
      console.error(`❌ Python search error for "${query}":`, error.message);
      return this.createFallbackData(query, error.message);
    }
  }

  async downloadImage(imageUrl) {
    try {
      console.log(`📥 Python image download: ${imageUrl}`);
      
      // Check dependencies first
      const depsOK = await this.checkPythonDependencies();
      if (!depsOK) {
        throw new Error('Python dependencies missing');
      }
      
      const result = await this.runCommand([
        'python3',
        this.pythonScript,
        'download',
        imageUrl
      ]);
      
      // For download command, stdout contains binary data
      const process = spawn('python3', [this.pythonScript, 'download', imageUrl], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.dirname(this.pythonScript)
      });
      
      const chunks = [];
      let stderr = '';
      
      process.stdout.on('data', (chunk) => {
        chunks.push(chunk);
      });
      
      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      return new Promise((resolve, reject) => {
        process.on('close', (code) => {
          if (code === 0 && chunks.length > 0) {
            const buffer = Buffer.concat(chunks);
            console.log(`✅ Downloaded ${buffer.length} bytes via Python`);
            
            // Log Python debug info
            if (stderr) {
              console.log('🐍 Download debug:', stderr.split('\n').slice(-2).join(' '));
            }
            
            resolve(buffer);
          } else {
            reject(new Error(`Download failed (code ${code}): ${stderr}`));
          }
        });
        
        process.on('error', (error) => {
          reject(error);
        });
      });
      
    } catch (error) {
      console.error(`❌ Python download error:`, error.message);
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