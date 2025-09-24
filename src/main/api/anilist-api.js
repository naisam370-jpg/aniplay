// AniList API integration for AniPlay
// Uses AniList GraphQL API to search for anime details and download cover images
const https = require('https');
const { URL } = require('url');

class AniListApi {
  constructor() {
    this.graphqlUrl = 'https://graphql.anilist.co';
  }

  async postGraphQL(query, variables = {}) {
    return new Promise((resolve, reject) => {
      const payload = JSON.stringify({ query, variables });
      const url = new URL(this.graphqlUrl);

      const opts = {
        method: 'POST',
        hostname: url.hostname,
        path: url.pathname,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Content-Length': Buffer.byteLength(payload),
          'User-Agent': 'AniPlay/1.0 (anilist integration)'
        }
      };

      const req = https.request(opts, (res) => {
        let data = '';
        res.setEncoding('utf8');

        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          try {
            const parsed = JSON.parse(data);
            resolve(parsed);
          } catch (err) {
            reject(new Error('Invalid JSON from AniList: ' + err.message));
          }
        });
      });

      req.on('error', (err) => reject(err));
      req.write(payload);
      req.end();
    });
  }

  async searchAnime(query) {
    if (!query) return this.createFallbackData(query, 'Empty query');

    const gql = `
      query ($search: String) {
        Media(search: $search, type: ANIME) {
          id
          title { romaji english native }
          description
          episodes
          status
          genres
          averageScore
          coverImage { large medium }
          startDate { year }
        }
      }
    `;

    try {
      const resp = await this.postGraphQL(gql, { search: query });
      const media = resp && resp.data && resp.data.Media;
      if (!media) return this.createFallbackData(query);

      const title = (media.title && (media.title.english || media.title.romaji || media.title.native)) || query;
      const rawDesc = media.description || '';
      const synopsis = rawDesc.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim() || 'No description available.';
      const score = media.averageScore ? Math.round((media.averageScore / 10) * 10) / 10 : 0.0; // convert 0-100 -> 0-10
      const episodes = media.episodes || 0;
      const statusMap = { FINISHED: 'Finished', RELEASING: 'Ongoing', NOT_YET_RELEASED: 'Not yet aired', CANCELLED: 'Cancelled' };
      const status = statusMap[media.status] || (media.status || 'Unknown');
      const genres = Array.isArray(media.genres) ? media.genres.slice(0, 6) : [];
      const year = media.startDate && media.startDate.year ? media.startDate.year : null;
      const image_url = (media.coverImage && (media.coverImage.large || media.coverImage.medium)) || null;
      const url = media.id ? `https://anilist.co/anime/${media.id}` : null;

      return {
        title,
        synopsis,
        score,
        episodes,
        status,
        genres,
        year,
        image_url,
        url
      };
    } catch (err) {
      console.error('AniList search error:', err.message);
      return this.createFallbackData(query, err.message);
    }
  }

  async downloadImage(imageUrl) {
    if (!imageUrl) throw new Error('No image URL provided');

    const fetchOnce = (urlToGet, redirects = 0) => new Promise((resolve, reject) => {
      const urlObj = new URL(urlToGet);
      const opts = {
        method: 'GET',
        hostname: urlObj.hostname,
        path: urlObj.pathname + (urlObj.search || ''),
        headers: { 'User-Agent': 'AniPlay/1.0' }
      };

      const req = https.request(opts, (res) => {
        // handle redirects (basic)
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirects < 5) {
          resolve(fetchOnce(res.headers.location, redirects + 1));
          return;
        }

        if (res.statusCode !== 200) {
          reject(new Error(`Image request failed: ${res.statusCode}`));
          return;
        }

        const chunks = [];
        res.on('data', (c) => chunks.push(Buffer.from(c)));
        res.on('end', () => resolve(Buffer.concat(chunks)));
      });

      req.on('error', reject);
      req.end();
    });

    try {
      const buf = await fetchOnce(imageUrl);
      return buf;
    } catch (err) {
      console.error('AniList image download error:', err.message);
      throw err;
    }
  }

  createFallbackData(query, errorMsg = '') {
    return {
      title: query,
      synopsis: `No AniList data available for "${query}".${errorMsg ? ' Error: ' + errorMsg : ''}`,
      score: 0,
      episodes: 0,
      status: 'Unknown',
      genres: [],
      year: null,
      image_url: null
    };
  }
}

module.exports = AniListApi;