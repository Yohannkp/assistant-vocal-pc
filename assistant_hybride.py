"""
Assistant Vocal PC - Version Hybride
===================================

Cette version peut fonctionner en mode vocal ou textuel selon les composants disponibles.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Tentative d'import des composants audio
AUDIO_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    AUDIO_AVAILABLE = True
    print("✅ Composants audio disponibles")
except ImportError as e:
    print(f"⚠️  Composants audio non disponibles: {e}")
    print("🔧 Fonctionnement en mode texte uniquement")

class AssistantVocalHybride:
    def __init__(self, force_text_mode=False):
        # Configuration Ollama
        self.ollama_url = "http://127.0.0.1:11434"
        self.model_name = "mistral:instruct"
        
        # Mode de fonctionnement
        self.audio_mode = AUDIO_AVAILABLE and not force_text_mode
        
        if self.audio_mode:
            self.setup_audio()
        
        # État de l'assistant
        self.active = True
        
        print(f"🤖 Assistant Vocal {'(Audio+Texte)' if self.audio_mode else '(Texte uniquement)'} initialisé")
        
        if self.audio_mode:
            self.speak("Bonjour ! Je suis votre assistant vocal. Dites 'Assistant' pour me réveiller ou tapez vos questions.")
        else:
            print("💡 Tapez vos questions ou 'quit' pour quitter")
        print("-" * 50)
    
    def setup_audio(self):
        """Configure les composants audio"""
        try:
            # Configuration de la reconnaissance vocale
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configuration de la synthèse vocale
            self.tts_engine = pyttsx3.init()
            self.setup_tts()
            
            print("🎤 Microphone et synthèse vocale configurés")
            
        except Exception as e:
            print(f"⚠️  Erreur configuration audio: {e}")
            self.audio_mode = False
    
    def setup_tts(self):
        """Configure les paramètres de synthèse vocale"""
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Chercher une voix française si disponible
            for voice in voices:
                if voice and ('french' in voice.name.lower() or 'fr' in voice.id.lower()):
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # Régler la vitesse et le volume
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"⚠️  Erreur configuration TTS: {e}")
    
    def speak(self, text):
        """Fait parler l'assistant (si audio disponible)"""
        print(f"🔊 Assistant: {text}")
        
        if self.audio_mode:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"⚠️  Erreur TTS: {e}")
    
    def listen_for_speech(self, timeout=5):
        """Écoute pour la reconnaissance vocale"""
        if not self.audio_mode:
            return None
        
        try:
            with self.microphone as source:
                print("👂 En écoute...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            try:
                text = self.recognizer.recognize_google(audio, language='fr-FR')
                print(f"🎤 Détecté: {text}")
                return text
                
            except sr.UnknownValueError:
                print("🤷 Parole non comprise")
                return None
            except sr.RequestError as e:
                print(f"❌ Erreur reconnaissance: {e}")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ Timeout d'écoute")
            return None
        except Exception as e:
            print(f"❌ Erreur microphone: {e}")
            return None
    
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
        """Traite une commande (vocale ou textuelle)"""
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
        
        if command_lower in ['mode texte', 'texte']:
            self.audio_mode = False
            self.speak("Passage en mode texte uniquement.")
            return True
        
        if command_lower in ['mode vocal', 'vocal'] and AUDIO_AVAILABLE:
            self.audio_mode = True
            self.speak("Passage en mode vocal.")
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
  - 'aide' ou 'help' : Affiche cette aide
  - 'mode texte' : Force le mode texte
  - 'mode vocal' : Active le mode vocal (si disponible)
  - 'quit', 'exit', 'stop', 'au revoir' : Quitte l'assistant
        """
        
        if self.audio_mode:
            help_text += "\n🎤 Mode vocal actif : dites 'Assistant' pour me réveiller"
        
        print(help_text)
        
        if self.audio_mode:
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
        else:
            print("❌ Erreur Mistral")
        
        # Test audio
        if self.audio_mode:
            print("🎤 Test microphone (dites quelque chose)...")
            speech = self.listen_for_speech(timeout=3)
            if speech:
                print(f"✅ Microphone OK: {speech}")
                self.speak("Microphone testé avec succès !")
            else:
                print("⚠️  Aucune parole détectée")
        
        print("=" * 50)
    
    def run_interactive_mode(self):
        """Mode interactif avec saisie clavier"""
        while self.active:
            try:
                # Option vocale si disponible
                if self.audio_mode:
                    print("\n💡 Tapez votre question ou appuyez sur Entrée pour écouter...")
                    user_input = input("👤 Vous (ou Entrée pour vocal): ").strip()
                    
                    if not user_input:  # Entrée vide = mode vocal
                        print("🎤 Mode écoute activé...")
                        speech = self.listen_for_speech()
                        if speech:
                            user_input = speech
                        else:
                            continue
                else:
                    user_input = input("\n👤 Vous: ").strip()
                
                if not self.process_command(user_input):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Arrêt de l'assistant...")
                break
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
    
    def run_voice_mode(self):
        """Mode vocal pur avec mot de réveil"""
        if not self.audio_mode:
            print("❌ Mode vocal non disponible")
            return
        
        print("👂 Écoute du mot de réveil 'Assistant'...")
        self.speak("Dites 'Assistant' pour me réveiller.")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while self.active:
            try:
                speech = self.listen_for_speech(timeout=2)
                
                if speech and 'assistant' in speech.lower():
                    self.speak("Oui, je vous écoute.")
                    
                    command = self.listen_for_speech(timeout=8)
                    if command:
                        if not self.process_command(command):
                            break
                    else:
                        self.speak("Je n'ai rien entendu. Redites 'Assistant' pour me réveiller.")
                
            except KeyboardInterrupt:
                print("\n👋 Arrêt de l'assistant...")
                break
    
    def run(self):
        """Lance l'assistant"""
        print(f"🚀 Assistant Vocal - {datetime.now().strftime('%H:%M:%S')}")
        print(f"🌐 Serveur: {self.ollama_url}")
        print(f"🤖 Modèle: {self.model_name}")
        print(f"🔊 Audio: {'Activé' if self.audio_mode else 'Désactivé'}")
        
        # Test initial
        print("\n🔧 Test initial...")
        self.run_tests()
        
        # Choix du mode
        if self.audio_mode:
            print("\n📋 Modes disponibles:")
            print("1. Mode interactif (clavier + vocal)")
            print("2. Mode vocal pur (mot de réveil)")
            print("3. Mode texte uniquement")
            
            try:
                choice = input("\nChoisissez un mode (1-3, ou Entrée pour mode 1): ").strip()
                
                if choice == "2":
                    self.run_voice_mode()
                elif choice == "3":
                    self.audio_mode = False
                    self.run_interactive_mode()
                else:
                    self.run_interactive_mode()
                    
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
        else:
            self.run_interactive_mode()

def main():
    print("🤖 Assistant Vocal PC avec Ollama Mistral")
    print("=" * 50)
    
    # Choix du mode au démarrage
    if AUDIO_AVAILABLE:
        force_text = input("Forcer le mode texte uniquement ? (o/n): ").lower() in ['o', 'oui', 'y', 'yes']
    else:
        force_text = True
    
    try:
        assistant = AssistantVocalHybride(force_text_mode=force_text)
        assistant.run()
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
