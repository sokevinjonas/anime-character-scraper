"""
Scraper pour Wikipedia - Extrait les infos des personnages d'anime.
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Optional, Dict, List
from urllib.parse import quote

class WikipediaScraper:
    BASE_URL = "https://en.wikipedia.org"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self, delay: float = 1.0):
        """Initialize scraper with rate limiting."""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_character(self, character_name: str, anime_name: str) -> Optional[Dict]:
        """Search for a character on Wikipedia."""
        print(f"  🔍 Wikipedia Search: {character_name}")

        try:
            # Essayer le titre direct
            page_title = f"{character_name}"
            url = f"{self.BASE_URL}/wiki/{quote(page_title)}"

            time.sleep(self.delay)
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return {
                    'name': character_name,
                    'anime': anime_name,
                    'url': url
                }

            # Sinon, essayer de chercher sur la page d'anime
            anime_url = f"{self.BASE_URL}/wiki/{quote(anime_name)}"
            response = self.session.get(anime_url, timeout=10)

            if response.status_code == 200:
                return {
                    'name': character_name,
                    'anime': anime_name,
                    'url': anime_url
                }

            return None

        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None

    def scrape_character_details(self, page_url: str) -> Optional[Dict]:
        """Scrape detailed information from Wikipedia."""
        try:
            time.sleep(self.delay)
            response = self.session.get(page_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            details = {
                'url': page_url,
                'imageUrl': '',
                'description': '',
                'infobox': {},
                'sections': []
            }

            # Image URL from infobox
            infobox = soup.find('table', class_='infobox')
            if infobox:
                img_tag = infobox.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    # Convert relative to absolute URL
                    if image_url.startswith('/'):
                        image_url = f"https://en.wikipedia.org{image_url}"
                    details['imageUrl'] = image_url

            # Récupérer la description (premiers paragraphes)
            paragraphs = soup.find_all('p')
            if paragraphs:
                details['description'] = paragraphs[0].get_text(strip=True)[:500]

            # Infobox (if exists)
            infobox = soup.find('table', class_='infobox')
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        details['infobox'][key] = value

            # Récupérer les titres de sections
            headings = soup.find_all(['h2', 'h3'])
            for heading in headings[:5]:
                details['sections'].append(heading.get_text(strip=True))

            return details

        except Exception as e:
            print(f"    ❌ Error scraping: {e}")
            return None

    def extract_facts(self, character_data: Dict) -> List[str]:
        """Extract key facts from Wikipedia data."""
        facts = []

        # Description
        if character_data.get('description'):
            sentences = character_data['description'].split('.')
            for sentence in sentences[:3]:
                if sentence.strip():
                    facts.append(sentence.strip())

        # Infobox data
        if character_data.get('infobox'):
            for key, value in list(character_data['infobox'].items())[:5]:
                if value:
                    facts.append(f"{key}: {value[:100]}")

        # Sections
        if character_data.get('sections'):
            for section in character_data['sections']:
                facts.append(f"Appears in section: {section}")

        return facts[:20]
