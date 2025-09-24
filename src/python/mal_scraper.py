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
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def clean_query(self, query):
        """Clean anime title for better search results"""
        cleaned = re.sub(r'\[.*?\]', '', query)  # Remove [brackets]
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove (parentheses)
        cleaned = re.sub(r'Season\s+\d+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bS\d+\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(1080p|720p|480p|BD|BluRay|DVD|WEB|TV)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(19|20)\d{2}\b', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
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
        """Perform actual search request (more robust parsing + basic bot detection)."""
        search_url = f"{self.base_url}/search/all"
        params = {
            'q': query,
            'cat': 'anime'
        }
        
        # include a Referer (helps avoid trivial blocks) and reuse UA
        headers = {
            'Referer': f'{self.base_url}/',
            'User-Agent': self.session.headers.get('User-Agent', '')
        }
        response = self.session.get(search_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()

        text = response.text

        # basic bot/captcha detection
        low = text.lower()
        if 'captcha' in low or 'are you human' in low or 'please enable javascript' in low or 'access denied' in low:
            raise RuntimeError("Blocked by MAL / Cloudflare (captcha or bot protection detected)")

        # debug: print a short snippet so caller can inspect unexpected pages
        print(f"[mal_scraper] search response {response.status_code}, len={len(text)}", file=sys.stderr)
        print(text[:1000].replace('\n', ' '), file=sys.stderr)
        
        soup = BeautifulSoup(text, 'html.parser')

        # Find the first anchor linking to an anime page anywhere on the search results page.
        link = soup.find('a', href=re.compile(r'^/anime/\d+(/|$)'))
        if not link:
            # fallback: any link that contains '/anime/<id>'
            candidates = soup.select('a[href*="/anime/"]')
            if candidates:
                link = candidates[0]

        if not link:
            return None

        title = link.get_text(strip=True) or link.get('title') or ''
        anime_url = link.get('href')
        anime_url = urllib.parse.urljoin(self.base_url, anime_url)

        print(f"📋 Getting details for: {title} -> {anime_url}", file=sys.stderr)
        details = self._get_anime_details(anime_url)

        return {
            'title': title,
            'url': anime_url,
            **details
        }
    
    def _get_anime_details(self, url):
        """Get detailed anime information from anime page (improved detection + debug)."""
        try:
            headers = {
                'Referer': self.base_url + '/',
                'User-Agent': self.session.headers.get('User-Agent', '')
            }
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            text = response.text
            low = text.lower()
            if 'captcha' in low or 'are you human' in low or 'please enable javascript' in low or 'access denied' in low:
                raise RuntimeError("Blocked by MAL / Cloudflare (captcha or bot protection detected)")

            soup = BeautifulSoup(text, 'html.parser')
            
            details = {}
            
            # Image URL - prefer og:image meta, then fallbacks
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                details['image_url'] = og_img.get('content')
            else:
                img_selectors = [
                    'img[data-src*="myanimelist"]',
                    'img[src*="myanimelist"]',
                    '.leftside img',
                    'img[itemprop="image"]'
                ]
                img_url = None
                for selector in img_selectors:
                    img_tag = soup.select_one(selector)
                    if img_tag:
                        img_url = img_tag.get('data-src') or img_tag.get('src')
                        if img_url:
                            break
                details['image_url'] = img_url

            # Synopsis - try meta description, then itemprop or synopsis blocks
            synopsis = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                synopsis = meta_desc.get('content').strip()
            else:
                synopsis_selectors = [
                    'p[itemprop="description"]',
                    '.synopsis p',
                    'span[itemprop="description"]',
                    '#content .spaceit_pad'  # MAL often uses .spaceit_pad for info blocks
                ]
                for selector in synopsis_selectors:
                    synopsis_elem = soup.select_one(selector)
                    if synopsis_elem:
                        txt = synopsis_elem.get_text(separator=' ', strip=True)
                        if len(txt) > 20:
                            synopsis = txt
                            break
            details['synopsis'] = synopsis or 'No description available.'
                
            # Score
            score = None
            score_selectors = [
                'span[itemprop="ratingValue"]',
                '.score-label',
                '[data-title*="score"]',
                '.fl-l.score'
            ]
            for selector in score_selectors:
                score_elem = soup.select_one(selector)
                if score_elem:
                    score_text = score_elem.get_text(strip=True)
                    score_match = re.search(r'(\d+\.?\d*)', score_text)
                    if score_match:
                        try:
                            score = float(score_match.group(1))
                            break
                        except:
                            continue
            details['score'] = score if score is not None else 0.0
                
            # Episodes, Status, Year - regex over page text (robust fallback)
            page_text = soup.get_text(separator=' ', strip=True)
            episodes_matches = [
                re.search(r'Episodes:\s*(\d+)', page_text, re.IGNORECASE),
                re.search(r'"episodes":\s*(\d+)', page_text),
                re.search(r'(\d+)\s*episodes?', page_text, re.IGNORECASE)
            ]
            episodes = None
            for match in episodes_matches:
                if match:
                    try:
                        episodes = int(match.group(1))
                        break
                    except:
                        continue
            details['episodes'] = episodes if episodes is not None else 0

            status = None
            status_matches = [
                re.search(r'Status:\s*([^<\n]+)', page_text, re.IGNORECASE),
                re.search(r'"status"\s*:\s*"([^"]+)"', page_text)
            ]
            for match in status_matches:
                if match:
                    status = match.group(1).strip()
                    break
            details['status'] = status or 'Unknown'

            year = None
            year_matches = [
                re.search(r'Aired:\s*[^<\n]*(\d{4})', page_text, re.IGNORECASE),
                re.search(r'"aired".*?(\d{4})', page_text),
                re.search(r'(\d{4})', page_text)
            ]
            for match in year_matches:
                if match:
                    try:
                        y = int(match.group(1))
                        if 1950 <= y <= 2030:
                            year = y
                            break
                    except:
                        continue
            details['year'] = year
                    
            # Genres
            details['genres'] = []
            genre_links = soup.find_all('a', href=re.compile(r'/anime/genre/\d+'))
            for link in genre_links[:6]:  # Limit to 6 genres
                genre = link.get_text(strip=True)
                if genre and len(genre) > 1 and genre not in details['genres']:
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
        print(json.dumps({'error': 'No command provided'}))
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