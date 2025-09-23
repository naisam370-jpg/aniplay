const https = require('https');
const http = require('http');
const { URL } = require('url');

class MALApi {
  constructor() {
    this.baseUrl = 'https://myanimelist.net';
    this.userAgent = 'AniPlay/1.0.0';
  }

  async httpGet(url) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const client = urlObj.protocol === 'https:' ? https : http;
      
      const options = {
        hostname: urlObj.hostname,
        port: urlObj.port,
        path: urlObj.pathname + urlObj.search,
        method: 'GET',
        headers: {
          'User-Agent': this.userAgent,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
      };

      const req = client.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => resolve({ data, status: res.statusCode }));
      });

      req.on('error', reject);
      req.setTimeout(10000, () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      req.end();
    });
  }

  async searchAnime(query) {
    try {
      console.log(`Searching for: ${query}`);
      
      // For now, return mock data to get the app working
      // We'll implement real MAL scraping later once the app is running
      return {
        title: query,
        synopsis: 'Mock anime description for testing purposes.',
        score: 8.5,
        episodes: 12,
        status: 'Finished Airing',
        genres: ['Action', 'Adventure'],
        year: 2023,
        image_url: null
      };
      
    } catch (error) {
      console.error(`MAL API error for ${query}:`, error.message);
      return null;
    }
  }

  async downloadImage(imageUrl) {
    // Return null for now - we'll implement this later
    return null;
  }
}

module.exports = MALApi;