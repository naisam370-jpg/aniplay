const axios = require('axios');
const cheerio = require('cheerio');

class MALApi {
  constructor() {
    this.baseUrl = 'https://myanimelist.net';
    this.searchUrl = 'https://myanimelist.net/search/all';
    this.userAgent = 'AniPlay/1.0.0';
  }

  async searchAnime(query) {
    try {
      console.log(`Searching MAL for: ${query}`);
      
      // Clean up the query
      const cleanQuery = this.cleanQuery(query);
      
      // Search MyAnimeList
      const searchUrl = `${this.searchUrl}?q=${encodeURIComponent(cleanQuery)}&cat=anime`;
      
      const response = await axios.get(searchUrl, {
        headers: {
          'User-Agent': this.userAgent,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Connection': 'keep-alive'
        },
        timeout: 10000
      });

      const $ = cheerio.load(response.data);
      
      // Find the first anime result
      const firstResult = $('.anime.list').first();
      
      if (firstResult.length === 0) {
        console.log(`No results found for: ${query}`);
        return null;
      }

      // Extract anime data
      const animeData = await this.extractAnimeData($, firstResult);
      
      if (animeData) {
        console.log(`Found: ${animeData.title}`);
        return animeData;
      }

      return null;
      
    } catch (error) {
      console.error(`MAL API error for ${query}:`, error.message);
      return null;
    }
  }

  cleanQuery(query) {
    // Remove common prefixes/suffixes that might interfere with search
    let cleaned = query
      .replace(/\[.*?\]/g, '') // Remove brackets like [SubGroup]
      .replace(/\(.*?\)/g, '') // Remove parentheses
      .replace(/Season\s+\d+/i, '') // Remove "Season X"
      .replace(/S\d+/i, '') // Remove "S1", "S2", etc.
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();
    
    return cleaned;
  }

  async extractAnimeData($, element) {
    try {
      const titleElement = element.find('h3 a, .title a').first();
      const title = titleElement.text().trim();
      const animeUrl = titleElement.attr('href');
      
      if (!title || !animeUrl) {
        return null;
      }

      // Get detailed info from anime page
      const detailData = await this.getAnimeDetails(animeUrl);
      
      return {
        title,
        url: animeUrl,
        ...detailData
      };
      
    } catch (error) {
      console.error('Error extracting anime data:', error);
      return null;
    }
  }

  async getAnimeDetails(animeUrl) {
    try {
      const fullUrl = animeUrl.startsWith('http') ? animeUrl : `${this.baseUrl}${animeUrl}`;
      
      const response = await axios.get(fullUrl, {
        headers: {
          'User-Agent': this.userAgent
        },
        timeout: 10000
      });

      const $ = cheerio.load(response.data);
      
      // Extract details
      const imageUrl = $('img.lazyload').attr('data-src') || $('img[itemprop="image"]').attr('src');
      const synopsis = $('[itemprop="description"]').text().trim() || 
                      $('.synopsis .spaceit_pad').text().trim();
      
      const score = parseFloat($('.score-label').text()) || 0;
      const episodes = parseInt($('.spaceit_pad:contains("Episodes:")').text().match(/\d+/)?.[0]) || 0;
      const status = $('.spaceit_pad:contains("Status:")').text().replace('Status:', '').trim();
      const yearText = $('.spaceit_pad:contains("Aired:")').text();
      const year = yearText.match(/(\d{4})/)?.[1] ? parseInt(yearText.match(/(\d{4})/)[1]) : null;
      
      // Extract genres
      const genres = [];
      $('[itemprop="genre"]').each((i, el) => {
        genres.push($(el).text().trim());
      });
      
      return {
        synopsis,
        score,
        episodes,
        status,
        genres,
        year,
        image_url: imageUrl
      };
      
    } catch (error) {
      console.error('Error getting anime details:', error);
      return {
        synopsis: 'No description available',
        score: 0,
        episodes: 0,
        status: 'Unknown',
        genres: [],
        year: null,
        image_url: null
      };
    }
  }

  async downloadImage(imageUrl) {
    try {
      const response = await axios.get(imageUrl, {
        responseType: 'arraybuffer',
        headers: {
          'User-Agent': this.userAgent
        },
        timeout: 15000
      });
      
      return Buffer.from(response.data);
      
    } catch (error) {
      console.error('Error downloading image:', error);
      throw error;
    }
  }
}

module.exports = MALApi;
