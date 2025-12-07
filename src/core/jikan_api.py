import requests
import time

API_BASE_URL = "https://api.jikan.moe/v4"

def search_anime(title):
    """
    Searches for an anime by title on JikanAPI.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/anime", params={"q": title, "limit": 1})
        response.raise_for_status()
        search_results = response.json()
        if search_results["data"]:
            return search_results["data"][0]
    except requests.exceptions.RequestException as e:
        print(f"Error searching for anime '{title}' on JikanAPI: {e}")
    return None

def get_anime_details(mal_id):
    """
    Gets detailed information for an anime from JikanAPI.
    """
    try:
        # Jikan API has a rate limit of 3 requests per second
        time.sleep(0.4)
        response = requests.get(f"{API_BASE_URL}/anime/{mal_id}/full")
        response.raise_for_status()
        return response.json()["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting details for anime with MAL ID '{mal_id}' from JikanAPI: {e}")
    return None
