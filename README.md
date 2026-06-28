# Anime Character Scraper

🕷️ Scrape des informations détaillées sur les personnages d'anime depuis **MyAnimeList**, **Wikipedia** et **Fandom**.

Enrichit automatiquement avec **Claude AI** pour générer 20 faits uniques par personnage.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
# Ajoute ta ANTHROPIC_API_KEY dans .env
```

## Workflow Complet

### 1️⃣ Scraper les Personnages

```bash
# Scraper les 180 personnages avec enrichissement Claude
python scraper.py --file data/all_characters.json --output knowledge-base.json
```

Cela va :
- ✅ Scraper MyAnimeList (description, voice actors)
- ✅ Scraper Wikipedia (biographie, infobox)
- ✅ Scraper Fandom (wikis spécifiques)
- ✅ Enrichir avec Claude (20 faits par perso)
- ✅ Générer `knowledge-base.json`

### 2️⃣ Formatter pour le Backend

```bash
# Convertir en format backend
python3 format_for_backend.py knowledge-base.json
```

Génère :
- ✅ `backend_data/anime.json` - Les animes
- ✅ `backend_data/characters.json` - Catalogue de personnages
- ✅ `backend_data/levels.json` - Niveaux avec knowledge base
- ✅ `backend_data/tiers.json` - Structure des paliers

### 3️⃣ Importer dans le Backend

```bash
# Copier les fichiers
cp backend_data/*.json ../anime-duel-api/data/

# Importer en BDD
cd ../anime-duel-api
npm run import:data
```

## Structure

```
anime-character-scraper/
├── scraper.py              # Script de scraping principal
├── format_for_backend.py   # Convertir pour le backend
├── requirements.txt        # Dépendances Python
├── package.json            # Scripts npm
├── data/
│   └── all_characters.json # 180+ personnages à scraper
├── backend_data/           # Généré - prêt pour le backend
│   ├── anime.json
│   ├── characters.json
│   ├── levels.json
│   └── tiers.json
└── scrapers/
    ├── myanimelist.py      # Scraper MyAnimeList
    ├── wikipedia.py        # Scraper Wikipedia
    ├── fandom.py           # Scraper Fandom
    └── image_scraper.py    # Scraper images (optionnel)
```

## Ajouter des Personnages

Édite simplement `data/all_characters.json` :

```json
{
  "characters": [
    {"name": "Character Name", "anime": "Anime Title"},
    ...
  ]
}
```

Re-lance le scraper et les nouveaux persos seront traités !

## Structure de Sortie (Backend Ready)

```json
{
  "levels": [
    {
      "levelNumber": 1,
      "characterName": "Naruto Uzumaki",
      "anime": "Naruto",
      "difficulty": "EASY",
      "palier": 0,
      "knowledgeBase": [
        "Fact 1 from MAL",
        "Fact 2 from Wikipedia",
        "Fact 3 from Fandom",
        "Generated fact from Claude",
        ...
      ]
    }
  ],
  "characters": [
    {
      "name": "Naruto Uzumaki",
      "anime": "Naruto",
      "imageUrl": null,
      "attributes": {
        "gender": "male",
        "powers": ["Rasengan", "Shadow Clone"],
        "is_villain": false,
        ...
      }
    }
  ],
  "anime": [
    {
      "title": "Naruto",
      "genre": "Shonen",
      "year": 2002
    }
  ],
  "tiers": [...]
}
```

## Sources Web

- **MyAnimeList** - https://myanimelist.net
- **Wikipedia** - https://en.wikipedia.org
- **Fandom** - https://fandom.com

## Troubleshooting

**Erreur venv :** `python3 -m venv venv && source venv/bin/activate`

**API Key manquante :** Vérifie ton `.env` et la variable `ANTHROPIC_API_KEY`

**Rate limiting :** Si beaucoup de 429 errors, augmente les `delay` dans les scrapers
