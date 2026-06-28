"""
Scraper pour Fandom (Wikia) - Scrape des wikis d'anime.
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Optional, Dict, List
from urllib.parse import quote

class FandomScraper:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self, delay: float = 1.0):
        """Initialize scraper with rate limiting."""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_character(self, character_name: str, anime_name: str) -> Optional[Dict]:
        """Search for a character on Fandom."""
        print(f"  🔍 Fandom Search: {character_name}")

        try:
            # Construire l'URL Fandom basée sur l'anime
            anime_slug = anime_name.lower().replace(" ", "-")
            fandom_url = f"https://{anime_slug}.fandom.com/wiki"

            time.sleep(self.delay)
            response = self.session.get(fandom_url, timeout=10)

            if response.status_code == 200:
                return {
                    'name': character_name,
                    'anime': anime_name,
                    'fandom_url': fandom_url
                }

            return None

        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None

    def scrape_character_details(self, fandom_url: str, character_name: str) -> Optional[Dict]:
        """Scrape character from Fandom wiki."""
        try:
            char_url = f"{fandom_url}/{quote(character_name.replace(' ', '_'))}"
            time.sleep(self.delay)
            response = self.session.get(char_url, timeout=10)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            details = {
                'url': char_url,
                'infobox': {},
                'biography': '',
                'personality': ''
            }

            # Infobox
            infobox = soup.find('table', class_='wikitable')
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows[:10]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            details['infobox'][key] = value

            # Biography section
            bio_heading = soup.find('h2', string='Biography')
            if bio_heading:
                content = bio_heading.find_next('p')
                if content:
                    details['biography'] = content.get_text(strip=True)[:300]

            # Personality section
            pers_heading = soup.find('h2', string='Personality')
            if pers_heading:
                content = pers_heading.find_next('p')
                if content:
                    details['personality'] = content.get_text(strip=True)[:300]

            return details

        except Exception as e:
            print(f"    ❌ Error scraping: {e}")
            return None

    def extract_facts(self, character_data: Dict) -> List[str]:
        """Extract facts from Fandom data."""
        facts = []

        # Infobox facts
        for key, value in list(character_data.get('infobox', {}).items())[:5]:
            if value:
                facts.append(f"{key}: {value[:80]}")

        # Biography
        if character_data.get('biography'):
            facts.append(f"Biography: {character_data['biography']}")

        # Personality
        if character_data.get('personality'):
            facts.append(f"Personality: {character_data['personality']}")

        return facts[:20]
