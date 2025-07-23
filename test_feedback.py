"""
Test du feedback vocal de l'assistant
====================================

Script pour tester les différents cas de feedback de l'assistant
"""

import requests
import json

# Test de connexion Ollama avec feedback
def test_ollama_connection():
    print("🧪 Test de connexion Ollama...")
    
    try:
        response = requests.get("http://127.0.0.1:11434", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama accessible")
            return True
        else:
            print(f"⚠️  Ollama répond mais statut: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama inaccessible: {e}")
        return False

# Test d'une requête Mistral
def test_mistral_query():
    print("🧪 Test requête Mistral...")
    
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "mistral:instruct",
        "prompt": "Dis simplement 'Test réussi'",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        mistral_response = result.get('response', '').strip()
        
        print(f"✅ Mistral répond: {mistral_response}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Mistral: {e}")
        return False

def main():
    print("🎯 Test du feedback de l'assistant vocal")
    print("=" * 50)
    
    # Tests des composants
    ollama_ok = test_ollama_connection()
    mistral_ok = test_mistral_query() if ollama_ok else False
    
    print("\n📊 Résultats des tests:")
    print(f"Ollama: {'✅ OK' if ollama_ok else '❌ Erreur'}")
    print(f"Mistral: {'✅ OK' if mistral_ok else '❌ Erreur'}")
    
    print("\n💡 L'assistant vocal donnera maintenant des feedbacks pour:")
    print("- ✅ Confirmation de présence: 'Présent ! Je vous écoute'")
    print("- ✅ Confirmation de commande: 'Compris ! Je traite votre demande'")
    print("- ✅ État du traitement: 'Connexion à Mistral en cours'")
    print("- ✅ Succès: 'Réponse reçue avec succès' + 'Traitement terminé'")
    print("- ✅ Fin de tâche: 'Tâche terminée ! Que puis-je faire d'autre'")
    print("- ❌ Erreurs détaillées: Description précise du problème")
    print("- ⏰ Timeouts: 'Je n'ai rien entendu pendant X secondes'")

if __name__ == "__main__":
    main()
