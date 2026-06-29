#!/usr/bin/env python3
"""
Script to fix incorrect genders in characters.json
Most anime characters had their genders inverted in the scraper output
"""

import json
import os
from pathlib import Path

# Known correct genders for key characters (to anchor the corrections)
KNOWN_CORRECT_GENDERS = {
    # Naruto - Male
    "Naruto Uzumaki": "male",
    "Sasuke Uchiha": "male",
    "Kakashi Hatake": "male",
    "Itachi Uchiha": "male",
    "Madara Uchiha": "male",
    "Shikamaru Nara": "male",
    "Jiraiya": "male",
    "Orochimaru": "male",
    "Pain": "male",
    "Deidara": "male",
    "Kisame Hoshigaki": "male",
    "Obito Uchiha": "male",
    "Minato Namikaze": "male",
    "Fugaku Uchiha": "male",
    "Yamato": "male",
    "Sai": "male",
    "Zetsu": "male",
    "Hidan": "male",
    "Kakuzu": "male",
    "Sasori": "male",
    "Nagato": "male",
    # Naruto - Female
    "Sakura Haruno": "female",
    "Hinata Hyuga": "female",
    "Konan": "female",
    "Kushina Uzumaki": "female",
    "Mikoto Uchiha": "female",
    "Ino Yamanaka": "female",
    "Choji Akimichi": "male",
    "Rock Lee": "male",
    "Neji Hyuga": "male",
}

def fix_genders(input_file):
    """Fix genders in characters.json"""

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'characters' not in data:
        print("Error: 'characters' key not found in JSON")
        return

    characters = data['characters']
    print(f"Total characters: {len(characters)}")

    # First pass: fix known characters
    fixes = 0
    for char in characters:
        name = char.get('name')
        if name in KNOWN_CORRECT_GENDERS:
            correct_gender = KNOWN_CORRECT_GENDERS[name]
            current_gender = char.get('attributes', {}).get('gender')
            if current_gender != correct_gender:
                print(f"  ✓ {name}: {current_gender} → {correct_gender}")
                char['attributes']['gender'] = correct_gender
                fixes += 1

    print(f"\nFixed known characters: {fixes}")

    # Count remaining genders
    unknown_chars = [c for c in characters if c['name'] not in KNOWN_CORRECT_GENDERS]
    female_count = sum(1 for c in unknown_chars if c['attributes'].get('gender') == 'female')
    male_count = sum(1 for c in unknown_chars if c['attributes'].get('gender') == 'male')

    print(f"\nUnknown characters - Male: {male_count}, Female: {female_count}")
    print(f"Ratio: {female_count / len(unknown_chars) * 100:.1f}% female")

    # If mostly female in unknown chars, they're probably inverted
    if female_count > male_count * 2:
        print("\n⚠️  Detected inverted genders in unknown characters. Inverting...")
        inverted = 0
        for char in unknown_chars:
            current = char['attributes'].get('gender')
            if current == 'male':
                char['attributes']['gender'] = 'female'
                inverted += 1
            elif current == 'female':
                char['attributes']['gender'] = 'male'
                inverted += 1
        fixes += inverted
        print(f"Inverted: {inverted} characters")

    # Save corrected file
    output_file = input_file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Total fixes: {fixes}")
    print(f"✓ Saved to {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        characters_file = Path(sys.argv[1])
    else:
        script_dir = Path(__file__).parent
        characters_file = script_dir / "backend_data" / "characters.json"

    if not characters_file.exists():
        print(f"Error: {characters_file} not found")
        exit(1)

    fix_genders(str(characters_file))
