"""
Assistant Vocal PC - Version TTS uniquement
===========================================

Cette version utilise uniquement la synthèse vocale (Text-to-Speech)
sans reconnaissance vocale pour éviter les problèmes PyAudio.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Import de la synthèse vocale
try:
    import pyttsx3
    TTS_AVAILABLE = True
    print("✅ Synthèse vocale disponible")
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  Synthèse vocale non disponible")

class AssistantVocalTTS:
    def __init__(self):
        # Configuration Ollama
        self.ollama_url = "http://127.0.0.1:11434"
        self.model_name = "mistral:instruct"
        
        # Configuration de la synthèse vocale
        self.tts_enabled = TTS_AVAILABLE
        if self.tts_enabled:
            self.setup_tts()
        
        self.active = True
        
        print(f"🤖 Assistant Vocal {'avec TTS' if self.tts_enabled else 'texte uniquement'} initialisé")
        
        if self.tts_enabled:
            self.speak("Bonjour ! Je suis votre assistant vocal. Tapez vos questions et j'y répondrai à voix haute.")
        else:
            print("💡 Tapez vos questions et je vous répondrai par écrit")
        print("-" * 50)
    
    def setup_tts(self):
        """Configure la synthèse vocale"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Chercher une voix française si disponible
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if voice and ('french' in voice.name.lower() or 'fr' in voice.id.lower()):
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"🗣️  Voix française détectée: {voice.name}")
                        break
            
            # Configuration de la voix
            self.tts_engine.setProperty('rate', 180)  # Vitesse
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            print("✅ Synthèse vocale configurée")
            
        except Exception as e:
            print(f"⚠️  Erreur TTS: {e}")
            self.tts_enabled = False
    
    def speak(self, text):
        """Fait parler l'assistant"""
        print(f"🔊 Assistant: {text}")
        
        if self.tts_enabled:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"⚠️  Erreur lors de la parole: {e}")
    
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
            
            print(f"⏱️  Réponse en {end_time - start_time:.2f}s ({result.get('eval_count', 'N/A')} tokens)")
            
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API Mistral: {e}")
            return None
    
    def process_command(self, command):
        """Traite une commande textuelle"""
        if not command or not command.strip():
            return True
        
        command_lower = command.lower().strip()
        
        # Commandes spéciales
        if any(word in command_lower for word in ['quit', 'exit', 'stop', 'au revoir', 'arrêt']):
            response = "Au revoir ! À bientôt."
            self.speak(response)
            return False
        
        if command_lower in ['aide', 'help']:
            self.show_help()
            return True
        
        if command_lower == 'test':
            self.run_tests()
            return True
        
        if command_lower in ['tts on', 'voix on'] and TTS_AVAILABLE:
            self.tts_enabled = True
            self.speak("Synthèse vocale activée.")
            return True
        
        if command_lower in ['tts off', 'voix off']:
            print("🔇 Synthèse vocale désactivée.")
            self.tts_enabled = False
            return True
        
        if command_lower == 'test voix' and self.tts_enabled:
            self.speak("Test de la synthèse vocale. Si vous entendez ceci, tout fonctionne parfaitement !")
            return True
        
        # Envoi à Mistral
        response = self.query_mistral(command)
        
        if response:
            self.speak(response)
        else:
            self.speak("Désolé, je n'ai pas pu traiter votre demande.")
        
        return True
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """
📖 Commandes disponibles:
  - Posez n'importe quelle question à Mistral
  - 'test' : Lance les tests de connexion
  - 'test voix' : Teste la synthèse vocale
  - 'tts on' / 'voix on' : Active la synthèse vocale
  - 'tts off' / 'voix off' : Désactive la synthèse vocale
  - 'aide' ou 'help' : Affiche cette aide
  - 'quit', 'exit', 'stop', 'au revoir' : Quitte l'assistant
        """
        
        print(help_text)
        
        if self.tts_enabled:
            self.speak("Consultez la console pour voir toutes les commandes disponibles.")
    
    def run_tests(self):
        """Lance les tests de connexion"""
        print("\n🧪 Tests de l'assistant...")
        
        # Test Ollama
        try:
            response = requests.get(f"{self.ollama_url}", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama accessible")
            else:
                print(f"⚠️  Ollama statut: {response.status_code}")
        except Exception as e:
            print(f"❌ Ollama inaccessible: {e}")
            return
        
        # Test Mistral
        response = self.query_mistral("Dis 'Test réussi'")
        if response:
            print(f"✅ Mistral OK: {response}")
            self.speak(response)
        else:
            print("❌ Erreur Mistral")
        
        # Test TTS
        if self.tts_enabled:
            print("🔊 Test de la synthèse vocale...")
            self.speak("Test de la synthèse vocale réussi !")
        
        print("=" * 50)
    
    def run_demo(self):
        """Lance une démonstration avec questions prédéfinies"""
        demo_questions = [
            "Salut ! Comment ça va ?",
            "Explique-moi en 2 phrases ce qu'est l'intelligence artificielle",
            "Écris une courte fonction Python pour dire bonjour",
            "Quels sont les avantages des assistants locaux ?",
            "Merci pour cette démonstration !"
        ]
        
        print(f"\n🎬 Démonstration avec {len(demo_questions)} questions")
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n📝 Question {i}: {question}")
            
            response = self.query_mistral(question)
            if response:
                self.speak(response)
            else:
                self.speak("Erreur lors de la génération de la réponse")
            
            if i < len(demo_questions):
                time.sleep(2)  # Pause entre les questions
        
        print("\n🎉 Démonstration terminée !")
    
    def run(self):
        """Lance l'assistant"""
        print(f"🚀 Assistant Vocal TTS - {datetime.now().strftime('%H:%M:%S')}")
        print(f"🌐 Serveur: {self.ollama_url}")
        print(f"🤖 Modèle: {self.model_name}")
        print(f"🔊 Synthèse vocale: {'Activée' if self.tts_enabled else 'Désactivée'}")
        
        # Test initial
        print("\n🔧 Test initial...")
        self.run_tests()
        
        # Choix du mode
        print("\n📋 Modes disponibles:")
        print("1. Mode interactif (par défaut)")
        print("2. Démonstration automatique")
        
        try:
            choice = input("\nChoisissez un mode (1-2, ou Entrée pour mode 1): ").strip()
            
            if choice == "2":
                self.run_demo()
                input("\nAppuyez sur Entrée pour passer au mode interactif...")
            
            # Mode interactif
            print("\n💬 Mode interactif activé")
            print("💡 Tapez vos questions (l'assistant vous répondra à voix haute)")
            
            while self.active:
                try:
                    user_input = input("\n👤 Vous: ").strip()
                    
                    if not self.process_command(user_input):
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Arrêt de l'assistant...")
                    break
                except Exception as e:
                    print(f"\n❌ Erreur: {e}")
                    
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")

def main():
    print("🤖 Assistant Vocal PC - Version TTS")
    print("=" * 50)
    
    try:
        assistant = AssistantVocalTTS()
        assistant.run()
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
