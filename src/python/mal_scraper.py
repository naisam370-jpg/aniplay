#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import sys
import time
import re
import urllib.parse

class MALScraper:
    def __init__(self):
        self.base_url = "https://myanimelist.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def clean_query(self, query):
        """Clean anime title for better search results"""
        # Remove common tags and indicators
        cleaned = re.sub(r'\[.*?\]', '', query)  # Remove [brackets]
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove (parentheses)
        cleaned = re.sub(r'Season\s+\d+', '', cleaned, flags=re.IGNORECASE)  # Remove Season X
        cleaned = re.sub(r'\bS\d+\b', '', cleaned, flags=re.IGNORECASE)  # Remove S1, S2
        cleaned = re.sub(r'\b(1080p|720p|480p|BD|BluRay|DVD|WEB|TV)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(19|20)\d{2}\b', '', cleaned)  # Remove years
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        cleaned = cleaned.strip(' -_.')
        
        return cleaned
    
    def search_anime(self, query):
        """Search for anime on MyAnimeList"""
        try:
            print(f"🔍 Searching for: '{query}'", file=sys.stderr)
            
            clean_query = self.clean_query(query)
            print(f"🧹 Cleaned query: '{clean_query}'", file=sys.stderr)
            
            # Try multiple search variations
            search_queries = [clean_query, query]
            if ' ' in clean_query:
                search_queries.append(clean_query.split()[0])  # First word only
                
            for search_query in search_queries:
                if not search_query.strip():
                    continue
                    
                print(f"🔍 Trying: '{search_query}'", file=sys.stderr)
                
                try:
                    result = self._perform_search(search_query)
                    if result:
                        print(f"✅ Found: {result['title']}", file=sys.stderr)
                        return result
                except Exception as e:
                    print(f"⚠️ Search failed for '{search_query}': {e}", file=sys.stderr)
                    continue
                
                time.sleep(0.5)  # Be nice to MAL servers
            
            print(f"❌ No results found for '{query}'", file=sys.stderr)
            return self._create_fallback_data(query)
            
        except Exception as e:
            print(f"❌ Search error for '{query}': {e}", file=sys.stderr)
            return self._create_fallback_data(query, str(e))
    
    def _perform_search(self, query):
        """Perform actual search request"""
        search_url = f"{self.base_url}/search/all"
        params = {
            'q': query,
            'cat': 'anime'
        }
        
        response = self.session.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find first anime result
        anime_result = soup.find('article', class_='list') or soup.find('div', class_='list')
        
        if not anime_result:
            return None
            
        # Extract title and URL
        title_link = anime_result.find('a')
        if not title_link:
            return None
            
        title = title_link.get_text(strip=True)
        anime_url = title_link.get('href')
        
        if not anime_url.startswith('http'):
            anime_url = f"{self.base_url}{anime_url}"
            
        print(f"📋 Getting details for: {title}", file=sys.stderr)
        
        # Get detailed information
        details = self._get_anime_details(anime_url)
        
        return {
            'title': title,
            'url': anime_url,
            **details
        }
    
    def _get_anime_details(self, url):
        """Get detailed anime information from anime page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {}
            
            # Image URL
            img_tag = soup.find('img', {'data-src': True}) or soup.find('img', {'src': True})
            if img_tag:
                details['image_url'] = img_tag.get('data-src') or img_tag.get('src')
            else:
                details['image_url'] = None
                
            # Synopsis
            synopsis_elem = soup.find('p', itemprop='description')
            if not synopsis_elem:
                synopsis_elem = soup.find('div', class_='synopsis')
                if synopsis_elem:
                    synopsis_elem = synopsis_elem.find('p')
                    
            if synopsis_elem:
                details['synopsis'] = synopsis_elem.get_text(strip=True)
            else:
                details['synopsis'] = 'No description available.'
                
            # Score
            score_elem = soup.find('div', class_='score-label')
            if score_elem:
                score_text = score_elem.get_text(strip=True)
                try:
                    details['score'] = float(score_text)
                except:
                    details['score'] = 0.0
            else:
                details['score'] = 0.0
                
            # Episodes
            episodes_elem = soup.find('span', string='Episodes:')
            if episodes_elem and episodes_elem.next_sibling:
                try:
                    details['episodes'] = int(episodes_elem.next_sibling.strip())
                except:
                    details['episodes'] = 0
            else:
                details['episodes'] = 0
                
            # Status
            status_elem = soup.find('span', string='Status:')
            if status_elem and status_elem.next_sibling:
                details['status'] = status_elem.next_sibling.strip()
            else:
                details['status'] = 'Unknown'
                
            # Year (from aired date)
            aired_elem = soup.find('span', string='Aired:')
            details['year'] = None
            if aired_elem and aired_elem.next_sibling:
                aired_text = aired_elem.next_sibling.strip()
                year_match = re.search(r'(\d{4})', aired_text)
                if year_match:
                    details['year'] = int(year_match.group(1))
                    
            # Genres
            details['genres'] = []
            genre_links = soup.find_all('a', href=re.compile(r'/anime/genre/\d+'))
            for link in genre_links[:6]:  # Limit to 6 genres
                genre = link.get_text(strip=True)
                if genre and genre not in details['genres']:
                    details['genres'].append(genre)
            
            print(f"📊 Extracted: score={details['score']}, eps={details['episodes']}, genres={len(details['genres'])}", file=sys.stderr)
            
            return details
            
        except Exception as e:
            print(f"❌ Error getting details: {e}", file=sys.stderr)
            return {
                'synopsis': 'Error fetching description.',
                'score': 0.0,
                'episodes': 0,
                'status': 'Unknown',
                'genres': [],
                'year': None,
                'image_url': None
            }
    
    def _create_fallback_data(self, query, error_msg=''):
        """Create fallback data when search fails"""
        return {
            'title': query,
            'synopsis': f'No MyAnimeList data found for "{query}".{" Error: " + error_msg if error_msg else ""}',
            'score': 0.0,
            'episodes': 0,
            'status': 'Unknown',
            'genres': [],
            'year': None,
            'image_url': None,
            'url': None
        }
    
    def download_image(self, image_url):
        """Download anime cover image"""
        try:
            if not image_url:
                return None
                
            print(f"📥 Downloading image: {image_url}", file=sys.stderr)
            
            response = self.session.get(image_url, timeout=15)
            response.raise_for_status()
            
            print(f"✅ Downloaded {len(response.content)} bytes", file=sys.stderr)
            return response.content
            
        except Exception as e:
            print(f"❌ Image download failed: {e}", file=sys.stderr)
            return None

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No query provided'}))
        return
        
    command = sys.argv[1]
    
    scraper = MALScraper()
    
    if command == 'search':
        if len(sys.argv) < 3:
            print(json.dumps({'error': 'No search query provided'}))
            return
            
        query = sys.argv[2]
        result = scraper.search_anime(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif command == 'download':
        if len(sys.argv) < 3:
            print(json.dumps({'error': 'No image URL provided'}))
            return
            
        image_url = sys.argv[2]
        image_data = scraper.download_image(image_url)
        
        if image_data:
            # Output binary data to stdout
            sys.stdout.buffer.write(image_data)
        else:
            print(json.dumps({'error': 'Failed to download image'}))
            
    else:
        print(json.dumps({'error': f'Unknown command: {command}'}))

if __name__ == '__main__':
    main()