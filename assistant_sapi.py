"""
Assistant Vocal avec TTS Windows SAPI Exclusif
==============================================
Version corrigée pour éviter les conflits audio
"""

import speech_recognition as sr
import requests
import json
import time
import os
import sys
from datetime import datetime

class AssistantVocalSAPI:
    def __init__(self):
        # Configuration Ollama
        self.ollama_url = "http://127.0.0.1:11434"
        self.model_name = "mistral:instruct"
        
        # Configuration reconnaissance vocale
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configuration optimisée pour éviter les coupures de parole
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5
        self.recognizer.phrase_time_limit = None
        self.recognizer.non_speaking_duration = 0.8
        
        # État de l'assistant
        self.listening = False
        self.active = True
        
        print("🤖 Assistant Vocal SAPI initialisé")
        self.speak("Bonjour ! Je suis votre assistant vocal. Dites 'Assistant' pour me réveiller.")
    
    def speak(self, text):
        """Synthèse vocale avec Windows SAPI exclusivement"""
        if not text or not text.strip():
            return False
        
        print(f"🔊 Assistant: {text}")
        
        try:
            # Nettoyer le texte pour éviter les problèmes PowerShell
            safe_text = text.replace('"', "'").replace('\\', '').replace('`', "'")
            safe_text = safe_text.replace('\n', ' ').replace('\r', ' ')
            
            # Limiter la longueur pour éviter les timeouts
            if len(safe_text) > 500:
                safe_text = safe_text[:497] + "..."
            
            # Commande PowerShell pour Windows SAPI
            cmd = f"""powershell -Command "
            Add-Type -AssemblyName System.Speech;
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
            $synth.SetOutputToDefaultAudioDevice();
            $synth.Rate = 0;
            $synth.Volume = 100;
            $voices = $synth.GetInstalledVoices();
            foreach($voice in $voices) {{
                if($voice.VoiceInfo.Name -like '*Hortense*') {{
                    $synth.SelectVoice($voice.VoiceInfo.Name);
                    break;
                }}
            }}
            $synth.Speak('{safe_text}');
            $synth.Dispose();"
            """
            
            # Exécution avec timeout
            start_time = time.time()
            result = os.system(cmd)
            duration = time.time() - start_time
            
            if result == 0:
                print(f"✅ Synthèse SAPI réussie ({duration:.2f}s)")
                return True
            else:
                print(f"⚠️ Code retour SAPI: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur synthèse SAPI: {e}")
            return False
    
    def speak_quick(self, text):
        """Version rapide pour les confirmations courtes"""
        if not text or not text.strip():
            return False
        
        print(f"🔊 Assistant: {text}")
        
        try:
            safe_text = text.replace('"', "'").replace('\\', '')
            
            # Version simplifiée pour les phrases courtes
            cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SetOutputToDefaultAudioDevice(); $s.Speak(\\"{safe_text}\\"); $s.Dispose()"'
            
            result = os.system(cmd)
            if result == 0:
                print("✅ Synthèse rapide réussie")
                return True
            else:
                print(f"⚠️ Erreur synthèse rapide: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur synthèse rapide: {e}")
            return False
    
    def listen_for_wake_word(self):
        """Écoute le mot de réveil 'Assistant'"""
        print("👂 En attente du mot de réveil 'Assistant'...")
        
        with self.microphone as source:
            print("🔧 Calibration du microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"✅ Seuil d'énergie: {self.recognizer.energy_threshold}")
        
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
                print(f"❌ Erreur d'écoute: {e}")
                time.sleep(1)
    
    def conversation_mode(self):
        """Mode conversation continue"""
        print("💬 Mode conversation activé")
        print("⏱️ Pause: 1.5s, Timeout: 15s/30s")
        
        while self.active:
            try:
                with self.microphone as source:
                    print("🎤 Parlez... (Prenez votre temps)")
                    audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=30)
                
                try:
                    print("🔄 Reconnaissance en cours...")
                    command = self.recognizer.recognize_google(audio, language='fr-FR')
                    print(f"🎤 Commande: {command}")
                    
                    # Vérifier commandes de sortie
                    command_lower = command.lower()
                    if any(word in command_lower for word in ['fini', 'terminé', 'pause', 'stop conversation']):
                        self.speak_quick("Conversation terminée. Redites 'Assistant' pour me réveiller.")
                        print("👂 Retour au mode d'écoute...")
                        break
                    
                    # Confirmer réception
                    self.speak_quick("Compris ! Je traite votre demande.")
                    
                    # Traiter la commande
                    self.process_command(command)
                    
                    if not self.active:
                        break
                    
                    # Confirmer fin de tâche
                    self.speak_quick("Terminé ! Autre chose ?")
                    print("💬 Continuez ou dites 'fini'...")
                    
                except sr.UnknownValueError:
                    print("❌ Parole non comprise")
                    self.speak_quick("Désolé, je n'ai pas compris. Répétez plus clairement ?")
                except sr.RequestError as e:
                    print(f"❌ Erreur reconnaissance: {e}")
                    self.speak_quick("Erreur de reconnaissance vocale.")
                    
            except sr.WaitTimeoutError:
                print("⏰ Timeout - retour écoute")
                self.speak_quick("Je retourne en veille. Redites 'Assistant'.")
                break
    
    def process_command(self, command):
        """Traite une commande vocale"""
        command_lower = command.lower()
        
        # Commandes de fermeture
        if any(word in command_lower for word in ['arrêt', 'stop', 'au revoir', 'fermer', 'arrête toi']):
            self.speak("Au revoir ! À bientôt.")
            self.active = False
            return
        
        # Commandes spéciales
        if any(word in command_lower for word in ['silence', 'tais-toi', 'chut']):
            self.speak_quick("D'accord, je me tais.")
            return
        
        if any(word in command_lower for word in ['test voix', 'test audio']):
            self.speak("Test de synthèse vocale en cours. Si vous entendez cette phrase, l'audio fonctionne parfaitement.")
            return
        
        # Commandes système
        if any(word in command_lower for word in ['ouvre', 'lance', 'démarre']):
            self.speak("Je ne peux pas lancer d'applications, mais je peux répondre à vos questions.")
            return
        
        # Envoi à Mistral
        self.speak_quick("Connexion à Mistral...")
        
        try:
            response = self.query_mistral(command)
            
            if response and response.strip():
                print(f"📝 Réponse: {response}")
                self.speak_quick("Réponse reçue.")
                time.sleep(0.2)
                self.speak(response)
            else:
                self.speak("Mistral n'a pas pu répondre.")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            self.speak("Une erreur s'est produite. Réessayez.")
    
    def query_mistral(self, prompt):
        """Envoie une requête à Mistral"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": f"Réponds en français de manière concise et naturelle : {prompt}",
            "stream": False
        }
        
        try:
            print(f"🤖 Envoi: {prompt}")
            start_time = time.time()
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            duration = time.time() - start_time
            result = response.json()
            response_text = result.get('response', '').strip()
            
            print(f"✅ Réponse en {duration:.2f}s")
            if result.get('eval_count'):
                print(f"📊 {result.get('eval_count')} tokens")
            
            return response_text
            
        except Exception as e:
            print(f"❌ Erreur Mistral: {e}")
            raise Exception(str(e))
    
    def run(self):
        """Lance l'assistant"""
        print("🚀 Démarrage assistant SAPI...")
        print("💡 Dites 'Assistant' pour me réveiller")
        print("💡 Dites 'fini' pour retourner en veille")
        print("💡 Dites 'au revoir' pour arrêter")
        print("-" * 50)
        
        try:
            self.listen_for_wake_word()
        except KeyboardInterrupt:
            print("\n👋 Arrêt demandé...")
            self.active = False
            self.speak_quick("Au revoir !")

def main():
    print("🤖 Assistant Vocal SAPI")
    print("=" * 50)
    
    try:
        assistant = AssistantVocalSAPI()
        assistant.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()
