#!/usr/bin/env python3
"""
Convertit le knowledge_base.json généré par le scraper en format prêt pour le backend.
Génère 3 fichiers :
1. anime.json - Les animes
2. characters.json - Les personnages avec attributs
3. levels.json - Les niveaux avec knowledge base
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from colorama import Fore, Style, init

init(autoreset=True)

def load_scraped_data(input_file: str) -> list:
    """Load scraped character data."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('levels', [])

def generate_anime_file(characters: list) -> dict:
    """Generate anime.json from character data."""
    anime_map = {}
    anime_list = []

    for char in characters:
        anime_name = char.get('anime', 'Unknown')

        if anime_name not in anime_map:
            anime_map[anime_name] = {
                'title': anime_name,
                'genre': 'Anime',
                'year': 2024,
                'imageUrl': None
            }
            anime_list.append(anime_map[anime_name])

    return {'anime': anime_list}

def extract_attributes(character_data: dict) -> dict:
    """Extract character attributes from knowledge base."""
    facts = character_data.get('knowledgeBase', [])
    sources = character_data.get('sources', {})

    attributes = {
        'gender': 'unknown',
        'role': 'protagonist',
        'powers': [],
        'is_villain': False,
        'has_weapon': False,
        'species': 'human',
        'affiliation': 'unknown',
        'description': ''
    }

    # Parse facts for attributes
    facts_text = ' '.join(facts).lower()

    if 'female' in facts_text or 'woman' in facts_text or 'girl' in facts_text or 'elle' in facts_text:
        attributes['gender'] = 'female'
    elif 'male' in facts_text or 'man' in facts_text or 'boy' in facts_text or 'il' in facts_text:
        attributes['gender'] = 'male'

    if 'villain' in facts_text or 'evil' in facts_text or 'antagonist' in facts_text:
        attributes['is_villain'] = True
    else:
        attributes['is_villain'] = False

    if 'sword' in facts_text or 'gun' in facts_text or 'weapon' in facts_text or 'épée' in facts_text:
        attributes['has_weapon'] = True

    # Extract powers
    power_keywords = ['power', 'ability', 'attack', 'technique', 'pouvoir', 'attaque', 'skill']
    for fact in facts:
        fact_lower = fact.lower()
        if any(keyword in fact_lower for keyword in power_keywords):
            attributes['powers'].append(fact[:80])

    # Set description from first fact
    if facts:
        attributes['description'] = facts[0][:200]

    return attributes

def generate_characters_file(characters: list) -> dict:
    """Generate characters.json with catalog data."""
    catalog_chars = []

    for i, char in enumerate(characters, 1):
        character_obj = {
            'name': char.get('characterName', 'Unknown'),
            'anime': char.get('anime', 'Unknown'),
            'imageUrl': char.get('imageUrl') or None,  # Récupéré du scraper
            'attributes': extract_attributes(char),
            'verified': True,
            'isCommunity': False
        }
        catalog_chars.append(character_obj)

    return {'characters': catalog_chars}

def generate_levels_file(characters: list) -> dict:
    """Generate levels.json with knowledge base."""
    levels = []

    for i, char in enumerate(characters, 1):
        level_obj = {
            'levelNumber': i,
            'characterName': char.get('characterName', 'Unknown'),
            'difficulty': 'EASY' if i <= 15 else ('EASY' if i <= 40 else ('MEDIUM' if i <= 65 else 'HARD')),
            'palier': 0 if i <= 15 else (1 if i <= 40 else (2 if i <= 65 else 3)),
            'knowledgeBase': char.get('knowledgeBase', [])
        }
        levels.append(level_obj)

    return {'levels': levels}

def generate_tiers_file() -> dict:
    """Generate tiers.json - static, doesn't change."""
    return {
        'tiers': [
            {'tierNumber': 0, 'name': 'Débutant', 'levelCount': 15, 'price': 0},
            {'tierNumber': 1, 'name': 'Guerrier du Feu', 'levelCount': 25, 'price': 50},
            {'tierNumber': 2, 'name': 'Pirate des Mers', 'levelCount': 25, 'price': 65},
            {'tierNumber': 3, 'name': 'Maître de la Foudre', 'levelCount': 25, 'price': 84}
        ]
    }

def main():
    input_file = 'knowledge-base.json'
    output_dir = Path('backend_data')
    output_dir.mkdir(exist_ok=True)

    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"{Fore.RED}❌ File not found: {input_file}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"{Fore.CYAN}📦 Converting scraped data to backend format...{Style.RESET_ALL}\n")

    # Load data
    characters = load_scraped_data(input_file)
    print(f"{Fore.BLUE}Loaded {len(characters)} characters{Style.RESET_ALL}")

    # Generate files
    print(f"\n{Fore.YELLOW}Generating files...{Style.RESET_ALL}")

    anime_data = generate_anime_file(characters)
    chars_data = generate_characters_file(characters)
    levels_data = generate_levels_file(characters)
    tiers_data = generate_tiers_file()

    # Save files
    files = {
        'anime.json': anime_data,
        'characters.json': chars_data,
        'levels.json': levels_data,
        'tiers.json': tiers_data
    }

    for filename, data in files.items():
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ {filename} ({len(data.get(list(data.keys())[0], []))} items)")

    print(f"\n{Fore.GREEN}✅ Backend files generated in {output_dir}/{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
    print(f"  1. Copy files from {output_dir}/ to ../anime-duel-api/data/")
    print(f"  2. Run: npm run import:data")

if __name__ == '__main__':
    main()
