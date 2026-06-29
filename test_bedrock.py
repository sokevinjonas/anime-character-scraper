#!/usr/bin/env python3
"""
Test direct de l'API Bedrock pour déboguer le problème.
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import boto3

    # Initialiser le client Bedrock
    client = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_BEDROCK_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    print(f"🔍 Testing Bedrock Connection...")
    print(f"   Region: {os.getenv('AWS_BEDROCK_REGION')}")
    print()

    # Test 1: Inference profile (us.) + version correcte bedrock-2023-05-31
    print("Test 1: us.anthropic.claude-haiku-4-5-20251001-v1:0 + bedrock-2023-05-31")
    try:
        response = client.invoke_model(
            modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Dis bonjour en francais"}]
            })
        )
        result = json.loads(response['body'].read())
        print(f"   ✅ Success!\n   Response: {result['content'][0]['text']}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test 2: Direct model ID + bedrock-2023-05-31
    print("Test 2: anthropic.claude-haiku-4-5-20251001-v1:0 + bedrock-2023-05-31")
    try:
        response = client.invoke_model(
            modelId="anthropic.claude-haiku-4-5-20251001-v1:0",
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Dis bonjour en francais"}]
            })
        )
        result = json.loads(response['body'].read())
        print(f"   ✅ Success!\n   Response: {result['content'][0]['text']}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test 3: Claude 3 Haiku (ancien modele) + bedrock-2023-05-31
    print("Test 3: anthropic.claude-3-haiku-20240307-v1:0 + bedrock-2023-05-31")
    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Dis bonjour en francais"}]
            })
        )
        result = json.loads(response['body'].read())
        print(f"   ✅ Success!\n   Response: {result['content'][0]['text']}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test 4: Converse API (alternative a invoke_model)
    print("Test 4: Converse API avec us.anthropic.claude-haiku-4-5-20251001-v1:0")
    try:
        response = client.converse(
            modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            messages=[{"role": "user", "content": [{"text": "Dis bonjour en francais"}]}],
            inferenceConfig={"maxTokens": 100}
        )
        result = response['output']['message']['content'][0]['text']
        print(f"   ✅ Success!\n   Response: {result}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    print("✅ Test complete!")

except ImportError:
    print("❌ boto3 not installed. Run: pip install boto3")
except Exception as e:
    print(f"❌ Fatal error: {e}")
