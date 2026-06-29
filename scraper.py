#!/usr/bin/env python3
"""
Anime Character Scraper - Collecte les infos des personnages d'anime.
Support: Anthropic API et AWS Bedrock
Features: Progressive saving, retry logic, resumable
"""

import json
import argparse
import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from scrapers.myanimelist import MyAnimeListScraper
from scrapers.wikipedia import WikipediaScraper
from scrapers.fandom import FandomScraper
from llm_client import get_llm_client
from colorama import Fore, Style, init

init(autoreset=True)
load_dotenv()

class AnimeCharacterScraper:
    def __init__(self, batch_size: int = 50):
        self.mal_scraper = MyAnimeListScraper(delay=1.5)
        self.wiki_scraper = WikipediaScraper(delay=1.5)
        self.fandom_scraper = FandomScraper(delay=1.5)
        self.llm_client = get_llm_client()
        self.batch_size = batch_size
        self.retry_count = 3
        self.retry_delay = 2

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
            'imageUrl': '',
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
                    # Récupérer l'image si disponible
                    if details.get('imageUrl') and not result['imageUrl']:
                        result['imageUrl'] = details['imageUrl']
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
                    # Récupérer l'image si disponible
                    if details.get('imageUrl') and not result['imageUrl']:
                        result['imageUrl'] = details['imageUrl']
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
                    # Récupérer l'image si disponible
                    if details.get('imageUrl') and not result['imageUrl']:
                        result['imageUrl'] = details['imageUrl']
        except Exception as e:
            print(f"    {Fore.YELLOW}⚠️  Fandom skip: {e}{Style.RESET_ALL}")

        # Remove duplicates et limiter à 14 facts
        result['knowledge_base'] = list(dict.fromkeys(result['knowledge_base']))[:14]

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

    def scrape_with_retry(self, character_name: str, anime_name: str) -> Dict:
        """Scrape with retry logic and backoff."""
        for attempt in range(self.retry_count):
            try:
                return self.scrape_character(character_name, anime_name)
            except Exception as e:
                if attempt < self.retry_count - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"{Fore.YELLOW}⚠️  Retry in {wait_time}s (attempt {attempt + 1}/{self.retry_count}){Style.RESET_ALL}")
                    time.sleep(wait_time)
                else:
                    print(f"{Fore.RED}❌ Failed after {self.retry_count} attempts{Style.RESET_ALL}")
                    return {
                        'name': character_name,
                        'anime': anime_name,
                        'imageUrl': '',
                        'sources': {},
                        'knowledge_base': [],
                        'failed': True
                    }

    def load_progress(self, output_path: str) -> tuple[List[Dict], int]:
        """Load existing progress if resuming."""
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results = data.get('levels', [])
                    print(f"{Fore.GREEN}📂 Resuming from {len(results)} saved characters{Style.RESET_ALL}")
                    return results, len(results)
            except:
                pass
        return [], 0

    def save_progress(self, results: List[Dict], output_path: str, intermediate: bool = False):
        """Save progress to file (intermediate or final)."""
        output = {'levels': results}

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        if intermediate:
            print(f"{Fore.CYAN}💾 Saved {len(results)} characters...{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Results saved to {output_path}{Style.RESET_ALL}")

    def process_characters(self, characters: List[Dict], enrich: bool = True, output_path: str = 'knowledge-base.json') -> List[Dict]:
        """Process all characters with progressive saving and resume capability."""
        results, resume_from = self.load_progress(output_path)
        start_idx = resume_from

        for i in range(resume_from, len(characters)):
            char = characters[i]
            progress = i + 1

            print(f"\n{Fore.BLUE}[{progress}/{len(characters)}]{Style.RESET_ALL}")

            result = self.scrape_with_retry(char['name'], char['anime'])

            if enrich and result.get('knowledge_base') and not result.get('failed'):
                result = self.enrich_with_llm(result)

            # Convert to output format
            output_result = {
                'characterName': result['name'],
                'anime': result['anime'],
                'knowledgeBase': result['knowledge_base'],
                'sources': result['sources']
            }
            if result.get('imageUrl'):
                output_result['imageUrl'] = result['imageUrl']

            results.append(output_result)

            # Save progress every batch_size characters
            if (progress - start_idx) % self.batch_size == 0 or progress == len(characters):
                self.save_progress(results, output_path, intermediate=(progress < len(characters)))

        return results

    def log_error(self, error_msg: str, log_file: str = 'scraper_errors.log'):
        """Log errors to file for troubleshooting."""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Scrape anime character information from multiple sources (resumable)"
    )
    parser.add_argument('--file', help='Path to characters.json')
    parser.add_argument('--character', help='Character name')
    parser.add_argument('--anime', help='Anime name')
    parser.add_argument('--output', default='knowledge-base.json', help='Output file')
    parser.add_argument('--no-enrich', action='store_true', help='Skip Claude enrichment')
    parser.add_argument('--batch-size', type=int, default=50, help='Save checkpoint every N characters')

    args = parser.parse_args()

    scraper = AnimeCharacterScraper(batch_size=args.batch_size)

    try:
        # Single character
        if args.character and args.anime:
            result = scraper.scrape_character(args.character, args.anime)
            if not args.no_enrich and result.get('knowledge_base'):
                result = scraper.enrich_with_llm(result)

            output_result = {
                'characterName': result['name'],
                'anime': result['anime'],
                'knowledgeBase': result['knowledge_base'],
                'sources': result['sources']
            }
            scraper.save_progress([output_result], args.output)

        # File of characters (resumable)
        elif args.file:
            characters = scraper.load_characters(args.file)
            total = len(characters)
            print(f"\n{Fore.BLUE}📋 Total characters to process: {total}{Style.RESET_ALL}")

            results = scraper.process_characters(characters, enrich=not args.no_enrich, output_path=args.output)

            success_count = len([r for r in results if 'knowledgeBase' in r and len(r['knowledgeBase']) > 0])
            failed_count = total - success_count

            print(f"\n{Fore.GREEN}✅ Scraping complete!{Style.RESET_ALL}")
            print(f"   ✓ Successfully processed: {success_count}/{total}")
            if failed_count > 0:
                print(f"   ⚠️  Failed/empty characters: {failed_count}")

        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏸️  Paused by user. Progress saved!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        error_msg = f"FATAL ERROR: {str(e)}"
        print(f"\n{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        scraper.log_error(error_msg)
        sys.exit(1)

if __name__ == '__main__':
    main()
