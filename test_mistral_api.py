#!/usr/bin/env python3
"""
Script de test pour utiliser le modèle Mistral via l'API Ollama
"""

import requests
import json
import time

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME = "mistral:instruct"

def test_mistral_api(prompt, stream=False):
    """
    Teste l'API Mistral avec un prompt donné
    """
    url = f"{OLLAMA_URL}/api/generate"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": stream
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🤖 Envoi de la requête à Mistral...")
    print(f"📝 Prompt: {prompt}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        end_time = time.time()
        
        print(f"✅ Réponse de Mistral:")
        print(f"📄 {result['response']}")
        print("-" * 50)
        print(f"⏱️  Temps de réponse: {end_time - start_time:.2f} secondes")
        print(f"🔢 Tokens générés: {result.get('eval_count', 'N/A')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return None

def test_mistral_streaming(prompt):
    """
    Teste l'API Mistral en mode streaming
    """
    url = f"{OLLAMA_URL}/api/generate"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🤖 Test en mode streaming...")
    print(f"📝 Prompt: {prompt}")
    print("-" * 50)
    print("📡 Réponse en temps réel:")
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if 'response' in data:
                    print(data['response'], end='', flush=True)
                    full_response += data['response']
                
                if data.get('done', False):
                    break
        
        print("\n" + "-" * 50)
        print("✅ Streaming terminé")
        return full_response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du streaming: {e}")
        return None

def get_available_models():
    """
    Récupère la liste des modèles disponibles
    """
    url = f"{OLLAMA_URL}/api/tags"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        
        print("📋 Modèles disponibles:")
        for model in result['models']:
            print(f"  - {model['name']} (Taille: {model['size'] / (1024**3):.1f} GB)")
        
        return result['models']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des modèles: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Test de l'API Mistral via Ollama")
    print("=" * 60)
    
    # Afficher les modèles disponibles
    get_available_models()
    print()
    
    # Test simple
    test_mistral_api("Explique-moi en 2 phrases ce qu'est l'intelligence artificielle.")
    print()
    
    # Test avec du code
    test_mistral_api("Écris une fonction Python pour calculer la factorielle d'un nombre.")
    print()
    
    # Test en mode streaming
    test_mistral_streaming("Raconte-moi une courte histoire sur un robot qui apprend à cuisiner.")
