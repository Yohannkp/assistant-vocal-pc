"""
Assistant Vocal Optimisé - Version Stable
==========================================

Version optimisée pour éviter les conflits TTS
"""

import speech_recognition as sr
import pyttsx3
import requests
import json
import time
import threading
from datetime import datetime

class AssistantVocalOptimise:
    def __init__(self):
        # Configuration API
        self.api_url = "http://127.0.0.1:11434/api/generate"
        self.model = "mistral:instruct"
        
        # Initialisation différée des composants
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.conversation_active = False
        
        # Configuration TTS
        self.tts_config = {
            'rate': 160,
            'volume': 1.0,
            'voice_name': 'Microsoft Hortense Desktop - French'
        }
        
        print("🤖 Assistant Vocal Optimisé initialisé")
    
    def init_tts(self):
        """Initialisation TTS avec gestion d'erreurs robuste"""
        try:
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass
                self.tts_engine = None
            
            # Nouvelle instance TTS
            self.tts_engine = pyttsx3.init()
            
            # Configuration voix française
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if voice and self.tts_config['voice_name'] in voice.name:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Configuration vitesse et volume
            self.tts_engine.setProperty('rate', self.tts_config['rate'])
            self.tts_engine.setProperty('volume', self.tts_config['volume'])
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation TTS: {e}")
            return False
    
    def speak_safe(self, text):
        """Synthèse vocale ultra-sécurisée"""
        if not text or not text.strip():
            return False
        
        print(f"🔊 TTS: {text}")
        
        # Méthode 1: TTS avec réinitialisation complète
        try:
            # Forcer nouvelle instance pour chaque phrase
            temp_engine = pyttsx3.init()
            
            # Configuration rapide
            voices = temp_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if voice and 'hortense' in voice.name.lower():
                        temp_engine.setProperty('voice', voice.id)
                        break
            
            temp_engine.setProperty('rate', 160)
            temp_engine.setProperty('volume', 1.0)
            
            # Synthèse
            temp_engine.say(text)
            temp_engine.runAndWait()
            
            # Nettoyage explicite
            try:
                temp_engine.stop()
            except:
                pass
            temp_engine = None
            
            print("✅ TTS réussie (méthode 1)")
            return True
            
        except Exception as e:
            print(f"⚠️ TTS méthode 1 échouée: {e}")
        
        # Méthode 2: TTS avec délais
        try:
            if not self.init_tts():
                return False
            
            self.tts_engine.stop()
            time.sleep(0.1)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            time.sleep(0.1)
            
            print("✅ TTS réussie (méthode 2)")
            return True
            
        except Exception as e:
            print(f"⚠️ TTS méthode 2 échouée: {e}")
        
        # Méthode 3: Fallback système
        try:
            import os
            # Utiliser PowerShell SAPI comme dernière option
            safe_text = text.replace('"', "'")
            cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SetOutputToDefaultAudioDevice(); $synth.Speak(\\"{safe_text}\\")"'
            os.system(cmd)
            print("✅ TTS réussie (méthode système)")
            return True
            
        except Exception as e:
            print(f"❌ Toutes les méthodes TTS ont échoué: {e}")
            return False
    
    def init_audio(self):
        """Initialisation des composants audio"""
        try:
            # Reconnaissance vocale
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 4000
            self.recognizer.pause_threshold = 1.0
            
            # Microphone
            self.microphone = sr.Microphone()
            
            # Calibration microphone
            print("🎤 Calibration du microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print("✅ Audio initialisé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation audio: {e}")
            return False
    
    def listen_for_command(self, timeout=5):
        """Écoute d'une commande avec timeout"""
        try:
            print(f"🎤 Écoute (timeout: {timeout}s)...")
            
            with self.microphone as source:
                # Écoute avec timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Reconnaissance en cours...")
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            print(f"✅ Reconnu: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ Timeout d'écoute")
            return None
        except sr.UnknownValueError:
            print("❓ Parole non comprise")
            return None
        except Exception as e:
            print(f"❌ Erreur reconnaissance: {e}")
            return None
    
    def call_mistral_api(self, prompt):
        """Appel API Mistral avec gestion d'erreurs"""
        try:
            print("🧠 Envoi à Mistral...")
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 200
                }
            }
            
            response = requests.post(
                self.api_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"❌ Erreur API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur Mistral: {e}")
            return None
    
    def start_conversation(self):
        """Mode conversation avec optimisations"""
        print("\n🎯 Mode conversation optimisé")
        print("Dites 'arrêt' ou 'stop' pour terminer")
        
        # Message d'accueil
        if not self.speak_safe("Bonjour ! Je suis votre assistant vocal optimisé. Comment puis-je vous aider ?"):
            print("❌ Problème TTS initial")
            return
        
        self.conversation_active = True
        tour = 0
        
        while self.conversation_active:
            tour += 1
            print(f"\n--- Tour {tour} ---")
            
            # Écoute de la commande
            command = self.listen_for_command(timeout=10)
            
            if not command:
                # Timeout - message de relance
                if not self.speak_safe("Je vous écoute toujours..."):
                    print("❌ Problème TTS relance")
                continue
            
            # Vérification arrêt
            if any(word in command for word in ['arrêt', 'stop', 'quitter', 'terminer']):
                if not self.speak_safe("Au revoir ! À bientôt !"):
                    print("❌ Problème TTS fermeture")
                break
            
            # Traitement avec Mistral
            self.speak_safe("Je traite votre demande...")
            
            response = self.call_mistral_api(command)
            
            if response:
                print(f"📝 Réponse: {response}")
                if not self.speak_safe(response):
                    print("❌ Problème TTS réponse")
                    # Fallback texte
                    print(f"💬 [TEXTE] {response}")
            else:
                if not self.speak_safe("Désolé, je n'ai pas pu traiter votre demande."):
                    print("❌ Problème TTS erreur")
        
        print("🏁 Conversation terminée")
    
    def run(self):
        """Lancement principal"""
        print("🚀 Démarrage Assistant Vocal Optimisé")
        
        # Initialisation audio
        if not self.init_audio():
            print("❌ Impossible d'initialiser l'audio")
            return
        
        # Test TTS initial
        if not self.speak_safe("Test audio initial"):
            print("❌ Problème TTS - Mode texte uniquement")
        
        # Attente du mot de réveil
        print("\n👂 En attente du mot de réveil 'Assistant'...")
        
        while True:
            try:
                command = self.listen_for_command(timeout=30)
                
                if command and 'assistant' in command:
                    print("🎯 Mot de réveil détecté !")
                    self.speak_safe("Présent ! Je vous écoute.")
                    self.start_conversation()
                    print("\n👂 En attente du mot de réveil 'Assistant'...")
                
            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé")
                self.speak_safe("Assistant vocal arrêté. Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                time.sleep(1)

def main():
    assistant = AssistantVocalOptimise()
    assistant.run()

if __name__ == "__main__":
    main()
