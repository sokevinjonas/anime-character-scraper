"""
Scraper pour MyAnimeList - Extrait les infos des personnages d'anime.
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Optional, Dict, List
from urllib.parse import quote

class MyAnimeListScraper:
    BASE_URL = "https://myanimelist.net"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self, delay: float = 1.0):
        """Initialize scraper with rate limiting."""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_character(self, character_name: str, anime_name: str) -> Optional[Dict]:
        """Search for a character on MAL."""
        print(f"  🔍 Searching: {character_name} from {anime_name}")

        query = f"{character_name} {anime_name}"
        url = f"{self.BASE_URL}/api/v2/users/get_my_info"

        try:
            search_url = f"https://myanimelist.net/search/all"
            params = {"q": query}

            time.sleep(self.delay)
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Chercher les résultats
            results = soup.find_all('div', class_='picSurround')

            if not results:
                print(f"    ⚠️  No results found")
                return None

            # Premier résultat
            result = results[0]
            link = result.find('a')

            if link:
                char_url = link.get('href')
                char_id = char_url.split('/')[-1]

                return {
                    'name': character_name,
                    'anime': anime_name,
                    'mal_id': char_id,
                    'url': char_url
                }

            return None

        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None

    def scrape_character_details(self, character_url: str) -> Optional[Dict]:
        """Scrape detailed information about a character."""
        try:
            time.sleep(self.delay)
            response = self.session.get(character_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            details = {
                'url': character_url,
                'imageUrl': '',
                'description': '',
                'voiced_by': [],
                'appears_in': [],
                'attributes': {}
            }

            # Image URL
            img_div = soup.find('div', class_='pl4')
            if img_div:
                img_tag = img_div.find('img')
                if img_tag and img_tag.get('src'):
                    details['imageUrl'] = img_tag.get('src')

            # Description
            desc_div = soup.find('div', class_='js-scrollfix-bottom-rel')
            if desc_div:
                details['description'] = desc_div.get_text(strip=True)[:500]

            # Voice actors
            va_section = soup.find('div', class_='spaceit_pad')
            if va_section:
                details['voiced_by'] = va_section.get_text(strip=True)

            # Manga/Anime appearances
            appearances = soup.find_all('td', class_='borderClass')
            if appearances:
                details['appears_in'] = [a.get_text(strip=True) for a in appearances[:5]]

            return details

        except Exception as e:
            print(f"    ❌ Error scraping details: {e}")
            return None

    def extract_facts(self, character_data: Dict) -> List[str]:
        """Extract key facts from scraped data."""
        facts = []

        if character_data.get('description'):
            # Split description into sentences
            sentences = character_data['description'].split('.')
            for sentence in sentences[:3]:
                if sentence.strip():
                    facts.append(sentence.strip())

        if character_data.get('voiced_by'):
            facts.append(f"Voiced by: {character_data['voiced_by'][:100]}")

        if character_data.get('appears_in'):
            for anime in character_data['appears_in']:
                facts.append(f"Appears in: {anime}")

        return facts[:20]  # Limite à 20 faits
