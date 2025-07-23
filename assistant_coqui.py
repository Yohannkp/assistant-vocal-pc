"""
Assistant Vocal avec Coqui TTS - Version Simplifiée
====================================================
Utilise des modèles TTS plus récents et compatibles
"""

import speech_recognition as sr
import requests
import json
import time
import os
import sys
from datetime import datetime

# Import TTS avec gestion d'erreur
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    print("⚠️ Coqui TTS non disponible")

class AssistantVocalCoqui:
    def __init__(self):
        # Configuration Ollama
        self.ollama_url = "http://127.0.0.1:11434"
        self.model_name = "mistral:instruct"
        
        # Configuration reconnaissance vocale
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configuration optimisée
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5
        
        # Configuration TTS
        self.tts_engine = None
        self.current_tts_method = "fallback"
        
        # État
        self.active = True
        
        print("🤖 Assistant Vocal avec Coqui TTS")
        self.setup_tts()
        self.speak("Bonjour ! Je suis votre assistant vocal avec une voix naturelle.")
    
    def setup_tts(self):
        """Configure le meilleur moteur TTS disponible"""
        if not COQUI_AVAILABLE:
            print("❌ Coqui TTS non disponible, utilisation du fallback SAPI")
            self.current_tts_method = "sapi"
            return
        
        try:
            # Tester différents modèles par ordre de préférence
            models_to_try = [
                ("tts_models/en/ljspeech/vits", "anglais-vits"),
                ("tts_models/en/ljspeech/tacotron2-DDC", "anglais-tacotron"),
                ("tts_models/en/jenny/jenny", "jenny")
            ]
            
            for model_name, description in models_to_try:
                try:
                    print(f"🧪 Test du modèle {description}...")
                    self.tts_engine = TTS(model_name=model_name, progress_bar=False, gpu=False)
                    self.current_tts_method = "coqui"
                    print(f"✅ Modèle {description} initialisé avec succès")
                    return
                except Exception as e:
                    print(f"⚠️ Échec {description}: {e}")
                    continue
            
            print("❌ Aucun modèle Coqui compatible, utilisation SAPI")
            self.current_tts_method = "sapi"
            
        except Exception as e:
            print(f"❌ Erreur Coqui TTS: {e}")
            self.current_tts_method = "sapi"
    
    def speak(self, text):
        """Synthèse vocale avec méthode optimale"""
        if not text or not text.strip():
            return False
        
        print(f"🔊 Assistant: {text}")
        
        if self.current_tts_method == "coqui" and self.tts_engine:
            return self.speak_coqui(text)
        else:
            return self.speak_sapi(text)
    
    def speak_coqui(self, text):
        """Synthèse avec Coqui TTS"""
        try:
            # Fichier temporaire
            output_file = "temp_tts.wav"
            
            # Générer l'audio
            start_time = time.time()
            self.tts_engine.tts_to_file(text=text, file_path=output_file)
            duration = time.time() - start_time
            
            # Lire l'audio avec Windows
            import subprocess
            subprocess.run([
                "powershell", "-Command", 
                f"(New-Object Media.SoundPlayer '{output_file}').PlaySync()"
            ], capture_output=True)
            
            # Nettoyer
            try:
                os.remove(output_file)
            except:
                pass
            
            print(f"✅ Coqui TTS réussi ({duration:.2f}s)")
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur Coqui TTS: {e}")
            print("🔄 Basculement vers SAPI...")
            self.current_tts_method = "sapi"
            return self.speak_sapi(text)
    
    def speak_sapi(self, text):
        """Synthèse avec Windows SAPI (fallback)"""
        try:
            # Nettoyer le texte
            safe_text = text.replace('"', "'").replace('\\', '')
            if len(safe_text) > 500:
                safe_text = safe_text[:497] + "..."
            
            # Commande PowerShell SAPI
            cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SetOutputToDefaultAudioDevice(); $s.Speak(\\"{safe_text}\\"); $s.Dispose()"'
            
            result = os.system(cmd)
            if result == 0:
                print("✅ SAPI TTS réussi")
                return True
            else:
                print(f"❌ Erreur SAPI: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur SAPI: {e}")
            return False
    
    def speak_quick(self, text):
        """Version rapide pour les confirmations"""
        return self.speak(text)
    
    def listen_for_wake_word(self):
        """Écoute le mot de réveil"""
        print("👂 En attente du mot de réveil 'Assistant'...")
        
        with self.microphone as source:
            print("🔧 Calibration microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"✅ Seuil: {self.recognizer.energy_threshold}")
        
        while self.active:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=4)
                
                try:
                    text = self.recognizer.recognize_google(audio, language='fr-FR').lower()
                    print(f"🎤 Détecté: {text}")
                    
                    if 'assistant' in text:
                        self.speak_quick("Présent ! Je vous écoute.")
                        self.conversation_mode()
                
                except sr.UnknownValueError:
                    pass
                
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"❌ Erreur: {e}")
                time.sleep(1)
    
    def conversation_mode(self):
        """Mode conversation"""
        print("💬 Mode conversation activé")
        
        while self.active:
            try:
                with self.microphone as source:
                    print("🎤 Parlez...")
                    audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=30)
                
                try:
                    command = self.recognizer.recognize_google(audio, language='fr-FR')
                    print(f"🎤 Commande: {command}")
                    
                    # Commandes de sortie
                    if any(word in command.lower() for word in ['fini', 'terminé', 'pause']):
                        self.speak("Conversation terminée. Redites 'Assistant'.")
                        break
                    
                    # Traitement
                    self.speak_quick("Compris ! Je traite votre demande.")
                    self.process_command(command)
                    
                    if not self.active:
                        break
                    
                    self.speak_quick("Terminé ! Autre chose ?")
                    
                except sr.UnknownValueError:
                    self.speak_quick("Désolé, je n'ai pas compris.")
                    
            except sr.WaitTimeoutError:
                self.speak("Je retourne en veille.")
                break
    
    def process_command(self, command):
        """Traite une commande"""
        command_lower = command.lower()
        
        # Commandes spéciales
        if any(word in command_lower for word in ['arrêt', 'au revoir']):
            self.speak("Au revoir !")
            self.active = False
            return
        
        if 'test voix' in command_lower:
            self.speak("Test de synthèse vocale. Cette voix vous plaît-elle ?")
            return
        
        if 'change voix' in command_lower:
            self.speak("Changement de méthode de synthèse vocale.")
            if self.current_tts_method == "coqui":
                self.current_tts_method = "sapi"
                self.speak("Basculement vers la voix Windows.")
            else:
                if COQUI_AVAILABLE:
                    self.setup_tts()
                    self.speak("Tentative de basculement vers Coqui TTS.")
                else:
                    self.speak("Coqui TTS non disponible.")
            return
        
        # Envoi à Mistral
        self.speak_quick("Connexion à Mistral...")
        
        try:
            response = self.query_mistral(command)
            if response and response.strip():
                print(f"📝 Réponse: {response}")
                self.speak(response)
            else:
                self.speak("Mistral n'a pas pu répondre.")
        except Exception as e:
            self.speak("Erreur lors de la connexion à Mistral.")
    
    def query_mistral(self, prompt):
        """Requête Mistral"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": f"Réponds en français de manière concise : {prompt}",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            raise Exception(str(e))
    
    def run(self):
        """Lance l'assistant"""
        print("🚀 Assistant vocal prêt")
        print("💡 Dites 'Assistant' pour commencer")
        print("💡 Dites 'test voix' pour tester la synthèse")
        print("💡 Dites 'change voix' pour changer de méthode TTS")
        print("-" * 50)
        
        try:
            self.listen_for_wake_word()
        except KeyboardInterrupt:
            print("\n👋 Arrêt...")
            self.speak("Au revoir !")

def main():
    print("🎤 Assistant Vocal Coqui TTS")
    print("=" * 50)
    
    if not COQUI_AVAILABLE:
        print("⚠️ Pour installer Coqui TTS: pip install TTS")
    
    try:
        assistant = AssistantVocalCoqui()
        assistant.run()
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
