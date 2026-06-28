"""
Scraper pour récupérer les images des personnages.
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Optional
from urllib.parse import quote

class ImageScraper:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def get_character_image(self, character_name: str, anime_name: str) -> Optional[str]:
        """Get character image from MyAnimeList or similar."""
        try:
            time.sleep(self.delay)

            # Essayer MyAnimeList image search
            search_query = f"{character_name} {anime_name}"
            url = f"https://myanimelist.net/api/v2/characters?query={quote(search_query)}&limit=1"

            response = self.session.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    char = data['data'][0]['node']
                    image_url = char.get('main_picture', {}).get('large')
                    if image_url:
                        return image_url

            return None

        except Exception as e:
            print(f"    ⚠️  Image scrape failed: {e}")
            return None

    def download_image(self, image_url: str, filename: str, save_dir: str = "images") -> bool:
        """Download and save image locally."""
        try:
            import os
            os.makedirs(save_dir, exist_ok=True)

            response = self.session.get(image_url, timeout=10)
            if response.status_code == 200:
                filepath = os.path.join(save_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True

            return False

        except Exception as e:
            print(f"    ⚠️  Download failed: {e}")
            return False
