"""
Client LLM abstrait - Support Anthropic et AWS Bedrock.
"""

import json
import os
from typing import Optional
from abc import ABC, abstractmethod
from colorama import Fore, Style

class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_facts(self, character_name: str, anime_name: str, existing_facts: list) -> list:
        """Generate 20 facts about a character."""
        pass

class AnthropicClient(LLMClient):
    """Anthropic API client."""

    def __init__(self, api_key: str):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def generate_facts(self, character_name: str, anime_name: str, existing_facts: list) -> list:
        """Generate 20 facts using Anthropic API."""
        existing = "\n".join(f"- {fact}" for fact in existing_facts[:10])

        prompt = f"""Generate exactly 20 unique, diverse facts about the character {character_name} from {anime_name}.

Existing facts (DO NOT repeat):
{existing}

Generate NEW facts covering:
- Appearance (hair, eyes, scars, clothes, etc.)
- Personality traits
- Powers/abilities
- Relationships with other characters
- Key story moments
- Motivations and goals
- Combat style
- Weakness
- Background/origin
- Interesting trivia

Format: Return ONLY a JSON array of 20 strings, nothing else.
Example: ["fact1", "fact2", ...]"""

        message = self.client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        facts = json.loads(response_text)
        return facts[:20] if isinstance(facts, list) else existing_facts

class BedrockClient(LLMClient):
    """AWS Bedrock client."""

    def __init__(self):
        try:
            import boto3
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_BEDROCK_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            self.model_id = os.getenv('AWS_BEDROCK_MODEL', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
        except ImportError:
            raise ImportError("boto3 package not installed. Run: pip install boto3")

    def generate_facts(self, character_name: str, anime_name: str, existing_facts: list) -> list:
        """Generate 14 facts using AWS Bedrock (in French)."""
        existing = "\n".join(f"- {fact}" for fact in existing_facts[:10])

        prompt = f"""Génère exactement 14 faits uniques et diversifiés sur le personnage {character_name} de l'anime {anime_name}.

Faits existants (NE PAS répéter):
{existing}

Génère de NOUVEAUX faits couvrant:
- Apparence (cheveux, yeux, cicatrices, vêtements, etc.)
- Traits de personnalité
- Pouvoirs/capacités
- Relations avec d'autres personnages
- Moments clés de l'histoire
- Motivations et objectifs
- Style de combat
- Faiblesses
- Origine/passé
- Anecdotes intéressantes

Format: Retourne UNIQUEMENT un tableau JSON de 14 chaînes de caractères en français, rien d'autre. Pas de texte avant ou après.
["fait1", "fait2", ...]"""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )

            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text'].strip()

            # Extraire le JSON même si Claude ajoute du texte autour
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                facts = json.loads(json_str)
                return facts[:14] if isinstance(facts, list) else existing_facts
            else:
                return existing_facts

        except Exception as e:
            print(f"{Fore.RED}Bedrock error: {e}{Style.RESET_ALL}")
            return existing_facts

def get_llm_client() -> LLMClient:
    """Get LLM client based on environment configuration."""
    provider = os.getenv('LLM_PROVIDER', 'bedrock').lower()

    if provider == 'anthropic':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        return AnthropicClient(api_key)

    elif provider == 'bedrock':
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_BEDROCK_REGION']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing AWS variables: {', '.join(missing)}")
        return BedrockClient()

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
