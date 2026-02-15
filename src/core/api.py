import requests
import time


class JikanAPI:
    def __init__(self):
        self.base_url = "https://api.jikan.moe/v4"

    def search_anime(self, title):
        """Searches for an anime and returns the top result's metadata."""
        try:
            # Jikan has a rate limit (3 requests per second), we add a small delay
            time.sleep(0.5)

            response = requests.get(f"{self.base_url}/anime", params={"q": title, "limit": 1})
            response.raise_for_status()
            data = response.json()

            if data['data']:
                anime = data['data'][0]
                return {
                    "mal_id": anime['mal_id'],
                    "rating": anime['score'],
                    "synopsis": anime['synopsis'],
                    "genres": ", ".join([g['name'] for g in anime['genres']])
                }
        except Exception as e:
            print(f"API Error for {title}: {e}")
        return None