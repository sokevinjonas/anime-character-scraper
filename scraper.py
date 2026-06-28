#!/usr/bin/env python3
"""
Anime Character Scraper - Collecte les infos des personnages d'anime.
Support: Anthropic API et AWS Bedrock
"""

import json
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from scrapers.myanimelist import MyAnimeListScraper
from scrapers.wikipedia import WikipediaScraper
from scrapers.fandom import FandomScraper
from llm_client import get_llm_client
from colorama import Fore, Style, init

init(autoreset=True)
load_dotenv()

class AnimeCharacterScraper:
    def __init__(self):
        self.mal_scraper = MyAnimeListScraper(delay=0.5)
        self.wiki_scraper = WikipediaScraper(delay=0.5)
        self.fandom_scraper = FandomScraper(delay=0.5)
        self.llm_client = get_llm_client()

    def load_characters(self, file_path: str) -> List[Dict]:
        """Load characters from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('characters', [])

    def scrape_character(self, character_name: str, anime_name: str) -> Dict:
        """Scrape a single character from multiple sources."""
        print(f"\n{Fore.CYAN}═══ {character_name} ({anime_name}) ═══{Style.RESET_ALL}")

        result = {
            'name': character_name,
            'anime': anime_name,
            'sources': {},
            'knowledge_base': []
        }

        # MyAnimeList
        print(f"{Fore.YELLOW}[MAL]{Style.RESET_ALL}")
        try:
            mal_result = self.mal_scraper.search_character(character_name, anime_name)
            if mal_result:
                details = self.mal_scraper.scrape_character_details(mal_result['url'])
                if details:
                    result['sources']['mal'] = details
                    result['knowledge_base'].extend(
                        self.mal_scraper.extract_facts(details)
                    )
        except Exception as e:
            print(f"    {Fore.YELLOW}⚠️  MAL skip: {e}{Style.RESET_ALL}")

        # Wikipedia
        print(f"{Fore.YELLOW}[Wikipedia]{Style.RESET_ALL}")
        try:
            wiki_result = self.wiki_scraper.search_character(character_name, anime_name)
            if wiki_result:
                details = self.wiki_scraper.scrape_character_details(wiki_result['url'])
                if details:
                    result['sources']['wiki'] = details
                    result['knowledge_base'].extend(
                        self.wiki_scraper.extract_facts(details)
                    )
        except Exception as e:
            print(f"    {Fore.YELLOW}⚠️  Wiki skip: {e}{Style.RESET_ALL}")

        # Fandom
        print(f"{Fore.YELLOW}[Fandom]{Style.RESET_ALL}")
        try:
            fandom_result = self.fandom_scraper.search_character(character_name, anime_name)
            if fandom_result:
                details = self.fandom_scraper.scrape_character_details(
                    fandom_result['fandom_url'], character_name
                )
                if details:
                    result['sources']['fandom'] = details
                    result['knowledge_base'].extend(
                        self.fandom_scraper.extract_facts(details)
                    )
        except Exception as e:
            print(f"    {Fore.YELLOW}⚠️  Fandom skip: {e}{Style.RESET_ALL}")

        # Remove duplicates
        result['knowledge_base'] = list(dict.fromkeys(result['knowledge_base']))

        print(f"{Fore.GREEN}✓ Scraped {len(result['knowledge_base'])} facts{Style.RESET_ALL}")

        return result

    def enrich_with_llm(self, character_data: Dict) -> Dict:
        """Use LLM to enrich and generate additional facts."""
        provider = os.getenv('LLM_PROVIDER', 'bedrock').upper()
        print(f"\n{Fore.MAGENTA}🤖 Enriching with {provider}...{Style.RESET_ALL}")

        try:
            facts = self.llm_client.generate_facts(
                character_data['name'],
                character_data['anime'],
                character_data['knowledge_base']
            )

            if isinstance(facts, list) and len(facts) > 0:
                character_data['knowledge_base'] = facts[:20]
                print(f"{Fore.GREEN}✓ Generated 20 facts with {provider}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️  Invalid response from {provider}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Error with {provider}: {e}{Style.RESET_ALL}")

        return character_data

    def process_characters(self, characters: List[Dict], enrich: bool = True) -> List[Dict]:
        """Process all characters."""
        results = []

        for i, char in enumerate(characters, 1):
            print(f"\n{Fore.BLUE}[{i}/{len(characters)}]{Style.RESET_ALL}")

            result = self.scrape_character(char['name'], char['anime'])

            if enrich and result['knowledge_base']:
                result = self.enrich_with_llm(result)

            results.append(result)

        return results

    def save_results(self, results: List[Dict], output_path: str):
        """Save results to JSON."""
        output = {
            'levels': [
                {
                    'characterName': r['name'],
                    'anime': r['anime'],
                    'knowledgeBase': r['knowledge_base'],
                    'sources': r['sources']
                }
                for r in results
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n{Fore.GREEN}✅ Results saved to {output_path}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(
        description="Scrape anime character information from multiple sources"
    )
    parser.add_argument('--file', help='Path to characters.json')
    parser.add_argument('--character', help='Character name')
    parser.add_argument('--anime', help='Anime name')
    parser.add_argument('--output', default='knowledge-base.json', help='Output file')
    parser.add_argument('--no-enrich', action='store_true', help='Skip Claude enrichment')

    args = parser.parse_args()

    scraper = AnimeCharacterScraper()

    # Single character
    if args.character and args.anime:
        result = scraper.scrape_character(args.character, args.anime)
        if not args.no_enrich:
            result = scraper.enrich_with_llm(result)
        scraper.save_results([result], args.output)

    # File of characters
    elif args.file:
        characters = scraper.load_characters(args.file)
        print(f"\n{Fore.BLUE}Found {len(characters)} characters to scrape{Style.RESET_ALL}")
        results = scraper.process_characters(characters, enrich=not args.no_enrich)
        scraper.save_results(results, args.output)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
