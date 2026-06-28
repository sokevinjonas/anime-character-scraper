# Anime Character Scraper

🕷️ Scrape des informations détaillées sur les personnages d'anime depuis **MyAnimeList**, **Wikipedia** et **Fandom**.

Enrichit automatiquement avec **Claude AI (AWS Bedrock)** pour générer 20 faits uniques par personnage.

**Features** : Progressive saving, retry logic avec backoff exponentiel, resumable, error logging.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
```

Ajoute dans `.env` (AWS Bedrock) :
```
LLM_PROVIDER=bedrock
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BEDROCK_REGION=us-east-1
AWS_BEDROCK_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

Ou pour l'API Anthropic :
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
```

## Workflow Complet

### 1️⃣ Scraper les Personnages (1000+)

```bash
# Scraper avec enrichissement Claude - resumable
python scraper.py --file data/all_characters.json --output knowledge-base.json
```

**Features** :
- ✅ Scrape MyAnimeList (description, voice actors, images)
- ✅ Scrape Wikipedia (biographie, infobox, images)
- ✅ Scrape Fandom (wikis spécifiques, images)
- ✅ Enrichit avec Claude Haiku (20 faits par perso)
- ✅ **Retry logic** : 3 tentatives avec backoff exponentiel (2s, 4s, 8s)
- ✅ **Progressive saving** : Checkpoint tous les 50 persos (configurable)
- ✅ **Resume capability** : Ctrl+C puis relance = continue depuis checkpoint
- ✅ **Error logging** : `scraper_errors.log` pour troubleshooting
- ✅ Génère `knowledge-base.json`

**Options** :
```bash
# Personnaliser la fréquence de checkpoint
python scraper.py --file data/all_characters.json --output knowledge-base.json --batch-size 100

# Scraper un seul personnage
python scraper.py --character "Naruto" --anime "Naruto" --output test.json

# Skip enrichissement Claude (test rapide)
python scraper.py --file data/all_characters.json --no-enrich
```

### 2️⃣ Formatter pour le Backend

```bash
python3 format_for_backend.py knowledge-base.json
```

Génère (dans `backend_data/`) :
- ✅ `anime.json` - Catalogue des animes
- ✅ `characters.json` - Persos avec images et attributs
- ✅ `levels.json` - Niveaux avec knowledge base (20 faits)
- ✅ `tiers.json` - Structure des paliers

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
├── scraper.py              # Script principal (retry + resume + progressive save)
├── llm_client.py           # Abstraction LLM (Anthropic API ou AWS Bedrock)
├── format_for_backend.py   # Convertir en format backend
├── requirements.txt        # Dépendances Python
├── .env                    # Config AWS Bedrock ou Anthropic
├── scraper_errors.log      # Généré - logs des erreurs
├── knowledge-base.json     # Généré - checkpoints progressifs
├── data/
│   └── all_characters.json # 1000+ persos à scraper
├── backend_data/           # Généré - prêt pour le backend
│   ├── anime.json
│   ├── characters.json
│   ├── levels.json
│   └── tiers.json
└── scrapers/
    ├── myanimelist.py      # Scrape MAL (1.5s delay)
    ├── wikipedia.py        # Scrape Wikipedia (1.5s delay)
    ├── fandom.py           # Scrape Fandom wikis (1.5s delay)
    └── image_scraper.py    # (optionnel)
```

## Ajouter des Personnages

Édite `data/all_characters.json` :

```json
{
  "characters": [
    {"name": "Character Name", "anime": "Anime Title"},
    {"name": "Another Char", "anime": "Another Anime"},
    ...
  ]
}
```

Relance le scraper — les nouveaux persos seront traités depuis le checkpoint.

## Gestion des Interruptions

**Si le scraper s'arrête** (crash, réseau, Ctrl+C) :

```bash
# Relance la même commande
python scraper.py --file data/all_characters.json --output knowledge-base.json
```

Le script :
1. Détecte `knowledge-base.json` existant
2. Charge les persos déjà scrapés
3. Continue depuis le prochain perso
4. Sauvegarde tous les 50 persos (ou selon `--batch-size`)

**Zéro perte de données** — seuls les persos non complétés sont re-scrapés.

## Logs et Troubleshooting

### `scraper_errors.log`

Généré automatiquement avec timestamps de tous les erreurs fatales.

```bash
tail -f scraper_errors.log  # Voir les erreurs en temps réel
```

### Erreurs Communes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `[Errno 13] Permission denied` | `.env` non readable | `chmod 600 .env` |
| `AWS_ACCESS_KEY_ID not found` | Config AWS manquante | Vérifie `.env` |
| `Rate limit 429` | Trop de requêtes | Augmente delay dans `.env` ou attends |
| `UNAUTHENTICATED` | Token AWS expiré | Renouvelle credentials |
| Interrupted (Ctrl+C) | Pause intentionnelle | Relance cmd = reprend du checkpoint |

### Debug

```bash
# Voir config chargée
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('LLM_PROVIDER:', os.getenv('LLM_PROVIDER'))"

# Test un perso
python scraper.py --character "Goku" --anime "Dragon Ball Z" --no-enrich

# Voir persos chargés
python -c "import json; data=json.load(open('data/all_characters.json')); print(f'{len(data[\"characters\"])} characters')"
```

## Performance Estimée

**Configuration actuelle** :
- Delay : 1.5s par requête (3 sources = ~4.5s par perso)
- Retry : 3 tentatives si erreur
- LLM enrichment : ~2s par perso (Bedrock)
- **Total : ~6-7s par perso**

**Pour 1000 persos** :
- Estimation : 1.5-2 heures sans interruption
- Checkpoint tous les 50 persos = ~5 min entre saves

## API Providers

### AWS Bedrock (Recommandé - gratuit via Anthropic)
- Modèle : `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- Region : `us-east-1`
- Avantages : Pas de rate-limiting restrictif, Haiku optimisé

### Anthropic API
- Modèle : Claude 3.5 Sonnet (optionnel)
- Avantages : Interface unifiée
- Coût : Pay-as-you-go

## Structure de Sortie (Backend Ready)

```json
{
  "levels": [
    {
      "characterName": "Naruto Uzumaki",
      "anime": "Naruto",
      "imageUrl": "https://...",
      "knowledgeBase": [
        "Fact 1 from MAL",
        "Fact 2 from Wikipedia",
        "Fact 3 from Fandom",
        "Generated fact 4",
        ...
      ],
      "sources": {
        "mal": {...},
        "wiki": {...},
        "fandom": {...}
      }
    }
  ]
}
```

## Sources Web

- **MyAnimeList** - https://myanimelist.net (official)
- **Wikipedia** - https://en.wikipedia.org (free)
- **Fandom** - https://fandom.com (wikis spécifiques)
