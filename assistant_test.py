"""
Assistant Vocal PC - Version Test Simplifiée
===========================================

Cette version utilise uniquement du texte pour tester l'intégration avec Mistral
avant d'installer les composants audio.
"""

import requests
import json
import time
from datetime import datetime

class AssistantVocalTest:
    def __init__(self):
        # Configuration Ollama
        self.ollama_url = "http://127.0.0.1:11434"
        self.model_name = "mistral:instruct"
        
        print("🤖 Assistant Vocal (Mode Test) initialisé")
        print("💡 Tapez vos questions ou 'quit' pour quitter")
        print("-" * 50)
    
    def query_mistral(self, prompt):
        """Envoie une requête à l'API Ollama Mistral"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": f"Réponds en français de manière concise et naturelle à cette question ou demande : {prompt}",
            "stream": False
        }
        
        try:
            print(f"🤖 Envoi à Mistral...")
            start_time = time.time()
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            end_time = time.time()
            result = response.json()
            
            print(f"⏱️  Temps de réponse: {end_time - start_time:.2f}s")
            print(f"🔢 Tokens générés: {result.get('eval_count', 'N/A')}")
            
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API Mistral: {e}")
            return None
    
    def process_command(self, command):
        """Traite une commande textuelle"""
        if not command.strip():
            return True
        
        command_lower = command.lower()
        
        # Commandes spéciales
        if command_lower in ['quit', 'exit', 'stop', 'au revoir']:
            print("👋 Au revoir !")
            return False
        
        if command_lower in ['help', 'aide']:
            self.show_help()
            return True
        
        if command_lower == 'test':
            self.run_tests()
            return True
        
        # Envoi à Mistral
        response = self.query_mistral(command)
        
        if response:
            print(f"\n🤖 Assistant: {response}\n")
        else:
            print("❌ Erreur lors du traitement de votre demande\n")
        
        return True
    
    def show_help(self):
        """Affiche l'aide"""
        print("\n📖 Commandes disponibles:")
        print("  - Tapez n'importe quelle question pour Mistral")
        print("  - 'test' : Lance les tests de connexion")
        print("  - 'help' ou 'aide' : Affiche cette aide")
        print("  - 'quit', 'exit', 'stop' : Quitte l'assistant")
        print()
    
    def run_tests(self):
        """Lance les tests de connexion"""
        print("\n🧪 Tests de connexion...")
        
        # Test ping Ollama
        try:
            response = requests.get(f"{self.ollama_url}", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama accessible")
            else:
                print(f"⚠️  Ollama répond mais statut: {response.status_code}")
        except Exception as e:
            print(f"❌ Ollama inaccessible: {e}")
            return
        
        # Test liste des modèles
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ {len(models)} modèle(s) disponible(s)")
                
                mistral_found = False
                for model in models:
                    print(f"   - {model['name']}")
                    if 'mistral' in model['name'].lower():
                        mistral_found = True
                
                if mistral_found:
                    print("✅ Modèle Mistral trouvé")
                else:
                    print("⚠️  Modèle Mistral non trouvé")
                    
        except Exception as e:
            print(f"❌ Erreur liste modèles: {e}")
            return
        
        # Test simple avec Mistral
        print("\n🔬 Test de communication avec Mistral...")
        response = self.query_mistral("Dis simplement 'Test réussi' si tu me reçois.")
        
        if response:
            print(f"✅ Communication OK: {response}")
        else:
            print("❌ Echec de communication")
        
        print("\n" + "="*50)
    
    def run(self):
        """Lance l'assistant en mode test"""
        print(f"🚀 Assistant Vocal Test - {datetime.now().strftime('%H:%M:%S')}")
        print(f"🌐 Serveur Ollama: {self.ollama_url}")
        print(f"🤖 Modèle: {self.model_name}")
        print()
        
        # Test initial automatique
        self.run_tests()
        
        # Boucle interactive
        while True:
            try:
                command = input("\n👤 Vous: ").strip()
                
                if not self.process_command(command):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Arrêt de l'assistant...")
                break
            except Exception as e:
                print(f"\n❌ Erreur: {e}")

def main():
    print("🤖 Assistant Vocal PC - Mode Test")
    print("=" * 50)
    
    try:
        assistant = AssistantVocalTest()
        assistant.run()
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()
