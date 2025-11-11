import requests
import os
import time

class AnilistAPI:
    def __init__(self):
        self.api_url = "https://graphql.anilist.co"

    def fetch_anime_metadata(self, anime_title):
        """
        Fetches metadata for a given anime title from Anilist.
        Returns the first search result.
        """
        query = """
        query ($search: String) {
            Media (search: $search, type: ANIME) {
                id
                title {
                    romaji
                    english
                    native
                }
                description(asHtml: false)
                genres
                coverImage {
                    extraLarge
                    color
                }
            }
        }
        """
        variables = {
            "search": anime_title
        }

        try:
            response = requests.post(self.api_url, json={'query': query, 'variables': variables})
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            time.sleep(1) # Add a delay to respect rate limits
            return data.get("data", {}).get("Media")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching metadata for '{anime_title}': {e}")
            return None

    def download_cover(self, image_url, save_path):
        """
        Downloads an image from a URL and saves it to the specified path.
        """
        if not image_url:
            return False
        
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded cover to {save_path}")
            time.sleep(1) # Add a delay to respect rate limits
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading cover from '{image_url}': {e}")
            return False

if __name__ == '__main__':
    # Example Usage
    anilist = AnilistAPI()
    
    # Test fetching metadata
    anime_title_to_search = "Spy x Family"
    print(f"Searching for: {anime_title_to_search}")
    metadata = anilist.fetch_anime_metadata(anime_title_to_search)
    
    if metadata:
        print(f"Found: {metadata['title']['english']}")
        print(f"Genres: {metadata['genres']}")
        print(f"Cover URL: {metadata['coverImage']['extraLarge']}")
        
        # Test downloading the cover
        cover_url = metadata['coverImage']['extraLarge']
        save_directory = "covers"
        # Use the English title for the filename, replacing invalid characters
        filename = f"{metadata['title']['english'].replace(':', ' - ')}.jpg"
        save_path = os.path.join(save_directory, filename)
        
        anilist.download_cover(cover_url, save_path)
        
        if os.path.exists(save_path):
            print(f"Test cover downloaded to: {save_path}")
            # os.remove(save_path) # Clean up test file
    else:
        print("Could not fetch metadata.")
