"""
Assistant Vocal PC avec Ollama Mistral
=====================================

Dépendances requises:
- speech_recognition : pour la reconnaissance vocale
- pyttsx3 : pour la synthèse vocale (text-to-speech)
- pyaudio : pour l'audio (microphone)
- requests : pour les appels API
- pygame : alternative pour l'audio si nécessaire

Installation:
pip install speech_recognition pyttsx3 pyaudio requests pygame
"""

import speech_recognition as sr
import pyttsx3
import requests
import json
import threading
import time
import sys
import os
import subprocess
from datetime import datetime

# Import Coqui TTS avec gestion d'erreur
try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False

class AssistantVocal:
    def __init__(self):
        # Configuration Ollama
        self.ollama_url = "http://127.0.0.1:11434"
        self.model_name = "mistral:instruct"
        
        # Configuration de la reconnaissance vocale
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configuration optimisée pour éviter les coupures de parole
        self.recognizer.energy_threshold = 4000  # Seuil d'énergie plus élevé
        self.recognizer.dynamic_energy_threshold = True  # Ajustement automatique
        self.recognizer.pause_threshold = 1.5  # Attendre 1.5 secondes de silence avant de s'arrêter
        self.recognizer.phrase_time_limit = None  # Pas de limite de temps pour une phrase
        self.recognizer.non_speaking_duration = 0.8  # Durée de silence pour considérer que la phrase est finie
        
        # Configuration de la synthèse vocale
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Configuration Coqui TTS (voix naturelle)
        self.coqui_engine = None
        self.current_tts_method = "auto"  # auto, coqui, sapi
        self.setup_coqui_tts()
        
        # État de l'assistant
        self.listening = False
        self.active = True
        
        print("🤖 Assistant Vocal initialisé")
        self.speak("Bonjour ! Je suis votre assistant vocal. Dites 'Assistant' pour me réveiller.")
    
    def setup_tts(self):
        """Configure les paramètres de synthèse vocale avec gestion robuste"""
        try:
            # Test de l'engine principal
            if self.tts_engine:
                voices = self.tts_engine.getProperty('voices')
                
                # Afficher toutes les voix disponibles pour debug
                print("🗣️  Voix disponibles:")
                french_voice_found = False
                
                if voices:
                    for i, voice in enumerate(voices):
                        if voice:
                            print(f"   {i}: {voice.name}")
                            # Chercher une voix française (priorité à Hortense)
                            if 'hortense' in voice.name.lower():
                                self.tts_engine.setProperty('voice', voice.id)
                                print(f"✅ Voix française sélectionnée: {voice.name}")
                                french_voice_found = True
                                break
                            elif 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                                self.tts_engine.setProperty('voice', voice.id)
                                print(f"✅ Voix française sélectionnée: {voice.name}")
                                french_voice_found = True
                                # Continue pour chercher Hortense si possible
                
                if not french_voice_found:
                    print("⚠️  Aucune voix française trouvée, utilisation de la voix par défaut")
                
                # Configuration optimisée
                self.tts_engine.setProperty('rate', 160)  # Vitesse claire
                self.tts_engine.setProperty('volume', 1.0)  # Volume maximum
                
                print("✅ Synthèse vocale configurée")
            else:
                print("❌ Moteur TTS non initialisé")
                
        except Exception as e:
            print(f"❌ Erreur configuration TTS: {e}")
            print("🔧 L'assistant utilisera des méthodes de fallback")
    
    def setup_coqui_tts(self):
        """Configure Coqui TTS pour des voix naturelles"""
        if not COQUI_AVAILABLE:
            print("⚠️ Coqui TTS non disponible - utilisation de Windows SAPI")
            self.current_tts_method = "sapi"
            return
        
        try:
            print("🎤 Initialisation Coqui TTS...")
            # Utiliser le modèle anglais qui fonctionne bien
            self.coqui_engine = TTS(
                model_name="tts_models/en/ljspeech/tacotron2-DDC", 
                progress_bar=False, 
                gpu=False
            )
            # Utiliser SAPI par défaut car plus stable
            self.current_tts_method = "sapi"
            print("✅ Coqui TTS disponible en option - Voix SAPI française par défaut")
            
        except Exception as e:
            print(f"⚠️ Coqui TTS non disponible: {e}")
            print("🔧 Utilisation de Windows SAPI")
            self.current_tts_method = "sapi"
    
    def speak(self, text):
        """Synthèse vocale intelligente - Coqui TTS puis SAPI"""
        if not text or not text.strip():
            return False
        
        print(f"🔊 Assistant: {text}")
        
        # Méthode 1: Coqui TTS (voix naturelle)
        if self.current_tts_method in ["auto", "coqui"] and self.coqui_engine:
            if self.speak_coqui(text):
                return True
            else:
                print("🔄 Basculement vers SAPI...")
                self.current_tts_method = "sapi"
        
        # Méthode 2: Windows SAPI (fallback)
        return self.speak_sapi(text)
    
    def speak_coqui(self, text):
        """Synthèse avec Coqui TTS (voix naturelle)"""
        try:
            # Fichier temporaire
            output_file = "temp_coqui_tts.wav"
            
            # Générer l'audio avec Coqui
            start_time = time.time()
            self.coqui_engine.tts_to_file(text=text, file_path=output_file)
            duration = time.time() - start_time
            
            # Lire avec PowerShell (plus stable)
            result = subprocess.run(
                ['powershell', '-Command', f"(New-Object Media.SoundPlayer '{output_file}').PlaySync()"],
                capture_output=True,
                text=True,
                timeout=15  # Timeout étendu à 15 secondes
            )
            
            # Nettoyer
            try:
                os.remove(output_file)
            except:
                pass
            
            if result.returncode == 0:
                print(f"✅ Coqui TTS réussi ({duration:.2f}s)")
                return True
            else:
                print(f"⚠️ Erreur lecture audio: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"⚠️ Erreur Coqui TTS: {e}")
            return False
    
    def speak_sapi(self, text):
        """Synthèse avec Windows SAPI (voix française optimisée)"""
        try:
            # Nettoyer le texte pour PowerShell - éliminer tous les caractères problématiques
            safe_text = text.replace('"', "").replace("'", "").replace('\\', '').replace('`', '')
            safe_text = safe_text.replace('\n', ' ').replace('\r', ' ')
            safe_text = safe_text.replace(':', ' ').replace(';', ' ')
            
            # Limiter la longueur
            if len(safe_text) > 400:
                safe_text = safe_text[:397] + "..."
            
            # Commande PowerShell SAPI simplifiée et robuste
            cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SetOutputToDefaultAudioDevice(); $s.Rate = 1; $s.Volume = 100; $s.Speak(\\"{safe_text}\\"); $s.Dispose()"'
            
            start_time = time.time()
            result = os.system(cmd)
            duration = time.time() - start_time
            
            if result == 0:
                print(f"✅ SAPI réussi ({duration:.2f}s)")
                return True
            else:
                print(f"❌ Erreur SAPI: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur SAPI: {e}")
            return False
    
    def listen_for_wake_word(self):
        """Écoute le mot de réveil 'Assistant'"""
        print("👂 En attente du mot de réveil 'Assistant'...")
        
        with self.microphone as source:
            print("🔧 Calibration du microphone pour le bruit ambiant...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"✅ Seuil d'énergie ajusté à: {self.recognizer.energy_threshold}")
        
        while self.active:
            try:
                with self.microphone as source:
                    # Écoute passive pour le mot de réveil avec timeout plus court
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=4)
                
                try:
                    text = self.recognizer.recognize_google(audio, language='fr-FR').lower()
                    print(f"🎤 Détecté: {text}")
                    
                    if 'assistant' in text:
                        self.speak("Présent ! Je vous écoute.")
                        # Entrer en mode conversation continue
                        self.conversation_mode()
                
                except sr.UnknownValueError:
                    pass  # Rien compris, continuer l'écoute
                
            except sr.WaitTimeoutError:
                pass  # Timeout normal, continuer
            except Exception as e:
                print(f"❌ Erreur d'écoute: {e}")
                time.sleep(1)
    
    def conversation_mode(self):
        """Mode conversation continue après le mot de réveil"""
        print("💬 Mode conversation activé - Parlez naturellement ou dites 'fini' pour arrêter")
        print("⏱️  Configuration: Pause de 1.5s avant traitement, pas de limite de temps")
        
        while self.active:
            try:
                with self.microphone as source:
                    print("🎤 Parlez maintenant... (Prenez votre temps, je vous laisse finir)")
                    # Paramètres optimisés pour laisser le temps de parler
                    audio = self.recognizer.listen(
                        source, 
                        timeout=15,  # Timeout plus long pour commencer à parler
                        phrase_time_limit=30  # Limite de 30 secondes pour une phrase complète
                    )
                
                try:
                    print("🔄 Traitement de votre parole... (cela peut prendre quelques secondes)")
                    command = self.recognizer.recognize_google(audio, language='fr-FR')
                    print(f"🎤 Commande reçue: {command}")
                    
                    # Vérifier les commandes de sortie de conversation
                    command_lower = command.lower()
                    if any(word in command_lower for word in ['fini', 'terminé', 'stop conversation', 'pause']):
                        self.speak("Conversation terminée. Redites 'Assistant' pour me réveiller.")
                        print("👂 Retour au mode d'écoute du mot de réveil...")
                        break
                    
                    # FEEDBACK : Confirmer qu'on a compris et qu'on commence
                    self.speak(f"Compris ! Je traite votre demande : {command}")
                    
                    # Traiter la commande
                    self.process_command(command)
                    
                    # Si l'assistant doit s'arrêter complètement, sortir
                    if not self.active:
                        break
                    
                    # Confirmer que la tâche est terminée
                    self.speak("Tâche terminée ! Que puis-je faire d'autre pour vous ?")
                    print("💬 Continuez la conversation ou dites 'fini'...")
                    
                except sr.UnknownValueError:
                    print("❌ Parole non comprise")
                    self.speak("Désolé, je n'ai pas compris votre parole. Pouvez-vous répéter plus clairement ?")
                except sr.RequestError as e:
                    print(f"❌ Erreur de reconnaissance: {e}")
                    self.speak(f"Erreur de reconnaissance vocale détectée : {str(e)}. Veuillez réessayer.")
                    
            except sr.WaitTimeoutError:
                print("⏰ Timeout - retour au mode d'écoute")
                self.speak("Je n'ai rien entendu pendant 15 secondes. Je retourne en mode veille. Redites 'Assistant' pour me réveiller.")
                break
    
    def listen_for_command(self):
        """Écoute une commande après le mot de réveil"""
        print("👂 En attente de votre commande...")
        
        try:
            with self.microphone as source:
                # Écoute active pour la commande avec plus de patience
                print("🎤 Parlez maintenant... (Prenez votre temps)")
                audio = self.recognizer.listen(
                    source, 
                    timeout=12,  # Plus de temps pour commencer
                    phrase_time_limit=25  # Plus de temps pour finir
                )
            
            try:
                print("🔄 Traitement de votre parole...")
                command = self.recognizer.recognize_google(audio, language='fr-FR')
                print(f"🎤 Commande reçue: {command}")
                
                # FEEDBACK IMPORTANT : Confirmer qu'on a compris
                self.speak(f"J'ai compris: {command}. Je traite votre demande.")
                
                # Traiter la commande
                self.process_command(command)
                
            except sr.UnknownValueError:
                print("❌ Parole non comprise")
                self.speak("Désolé, je n'ai pas compris votre demande. Pouvez-vous répéter plus clairement ?")
            except sr.RequestError as e:
                print(f"❌ Erreur de reconnaissance: {e}")
                self.speak("Erreur de reconnaissance vocale. Veuillez réessayer.")
                
        except sr.WaitTimeoutError:
            print("⏰ Timeout - rien entendu")
            self.speak("Je n'ai rien entendu. Redites 'Assistant' pour me réveiller.")
    
    def process_command(self, command):
        """Traite une commande vocale avec feedback détaillé"""
        command_lower = command.lower()
        
        # Commandes spéciales de fermeture complète
        if any(word in command_lower for word in ['arrêt', 'stop', 'au revoir', 'fermer', 'arrête toi']):
            self.speak("Commande d'arrêt reçue. Au revoir ! À bientôt.")
            self.active = False
            return
        
        if any(word in command_lower for word in ['silence', 'tais-toi', 'chut']):
            self.speak("Commande de silence reçue. D'accord, je me tais.")
            return
        
        if any(word in command_lower for word in ['test voix', 'test audio']):
            self.speak("Test de la synthèse vocale en cours.")
            time.sleep(0.5)
            if self.current_tts_method == "coqui":
                self.speak("Vous entendez actuellement la voix naturelle Coqui TTS. Elle sonne beaucoup plus naturelle que les voix Windows.")
            else:
                self.speak("Vous entendez actuellement la voix Windows SAPI. Dites 'voix naturelle' pour utiliser Coqui TTS.")
            return
        
        if any(word in command_lower for word in ['voix naturelle', 'coqui', 'meilleure voix']):
            if COQUI_AVAILABLE and self.coqui_engine:
                self.current_tts_method = "coqui"
                self.speak("Basculement vers la voix naturelle Coqui TTS. Cette voix est beaucoup plus agréable à écouter.")
            else:
                self.speak("La voix naturelle Coqui TTS n'est pas disponible. Installation nécessaire.")
            return
        
        if any(word in command_lower for word in ['voix windows', 'voix classique', 'sapi']):
            self.current_tts_method = "sapi"
            self.speak("Basculement vers la voix Windows SAPI classique.")
            return
        
        # Commandes système avec feedback détaillé
        if any(word in command_lower for word in ['démarre chrome', 'ouvre chrome', 'lance chrome']):
            self.speak("Désolé, je ne peux pas démarrer des applications système pour des raisons de sécurité. Mais je peux vous aider avec d'autres questions.")
            return
        
        if any(word in command_lower for word in ['ouvre', 'lance', 'démarre']):
            self.speak("Je ne peux pas lancer d'applications, mais je peux vous donner des informations ou répondre à vos questions.")
            return
        
        # Envoi à Mistral avec feedback complet
        self.speak("Connexion à Mistral en cours. Je traite votre demande...")
        
        try:
            response = self.query_mistral(command)
            
            if response and response.strip():
                print(f"📝 Réponse Mistral: {response}")
                self.speak("Réponse reçue de Mistral avec succès.")
                time.sleep(0.3)
                self.speak(response)
                self.speak("Traitement terminé avec succès !")
            else:
                error_msg = "Mistral n'a pas pu générer de réponse. Cela peut être dû à un problème de connexion ou de compréhension de la demande."
                print(f"❌ {error_msg}")
                self.speak(error_msg)
                
        except Exception as e:
            error_details = str(e)
            error_msg = f"Erreur technique détectée : {error_details}"
            print(f"❌ {error_msg}")
            self.speak(f"Une erreur technique s'est produite. Détails : {error_details}")
            self.speak("Veuillez réessayer votre demande.")
    
    def query_mistral(self, prompt):
        """Envoie une requête à l'API Ollama Mistral avec feedback détaillé"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": f"Réponds en français de manière concise et naturelle à cette question ou demande : {prompt}",
            "stream": False
        }
        
        try:
            print(f"🤖 Envoi à Mistral: {prompt}")
            start_time = time.time()
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = response.json()
            response_text = result.get('response', '').strip()
            
            # Feedback de succès avec détails
            print(f"✅ Réponse reçue en {duration:.2f}s")
            if result.get('eval_count'):
                print(f"📊 {result.get('eval_count')} tokens générés")
            
            return response_text
            
        except requests.exceptions.Timeout:
            error_msg = "Timeout : Mistral met trop de temps à répondre"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Erreur de connexion : Impossible de joindre Ollama. Vérifiez que le serveur est démarré"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Erreur API Ollama : {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def test_components(self):
        """Teste les composants de l'assistant"""
        print("🧪 Test des composants...")
        
        # Test TTS avec feedback détaillé
        print("🔊 Test de la synthèse vocale...")
        test_phrase = "Test de la synthèse vocale. Vous devez entendre cette phrase à voix haute."
        self.speak(test_phrase)
        
        # Demander confirmation à l'utilisateur
        audio_ok = input("Avez-vous entendu la synthèse vocale ? (o/n): ").lower()
        if audio_ok not in ['o', 'oui', 'y', 'yes']:
            print("⚠️  Problème audio détecté - vérifiez vos haut-parleurs")
        
        # Test microphone
        print("🎤 Test du microphone - dites 'test microphone'...")
        try:
            with self.microphone as source:
                print("🔧 Ajustement du bruit ambiant...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("👂 En écoute... (vous avez 8 secondes, prenez votre temps)")
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=20)
                
            print("🔄 Traitement de l'audio...")
            text = self.recognizer.recognize_google(audio, language='fr-FR')
            print(f"✅ Microphone OK - Détecté: {text}")
            self.speak(f"Parfait ! J'ai bien entendu: {text}")
            
        except sr.WaitTimeoutError:
            print("⏰ Rien entendu dans les 8 secondes")
            self.speak("Je n'ai rien entendu. Vérifiez votre microphone.")
        except Exception as e:
            print(f"❌ Erreur microphone: {e}")
            self.speak("Erreur de microphone détectée.")
        
        # Test API Mistral
        print("🤖 Test de l'API Mistral...")
        response = self.query_mistral("Réponds simplement 'Test API réussi'")
        if response:
            print(f"✅ API Mistral OK - Réponse: {response}")
            self.speak(f"Excellent ! Mistral répond: {response}")
        else:
            print("❌ Erreur API Mistral")
            self.speak("Problème de connexion avec Mistral.")
        
        print("\n🎯 Tests terminés. L'assistant est prêt !")
    
    def run(self):
        """Lance l'assistant vocal"""
        print("🚀 Démarrage de l'assistant vocal...")
        print("💡 Dites 'Assistant' pour me réveiller")
        print("💡 Une fois en conversation, parlez naturellement")
        print("💡 Dites 'fini' pour revenir au mode veille")
        print("💡 Dites 'au revoir' pour m'arrêter complètement")
        print("-" * 50)
        
        try:
            self.listen_for_wake_word()
        except KeyboardInterrupt:
            print("\n👋 Arrêt de l'assistant...")
            self.active = False
            self.speak("Au revoir !")

def main():
    print("🤖 Assistant Vocal PC avec Ollama Mistral")
    print("=" * 50)
    
    try:
        assistant = AssistantVocal()
        
        # Demander si on veut faire des tests
        choice = input("\nVoulez-vous tester les composants d'abord ? (o/n): ").lower()
        if choice in ['o', 'oui', 'y', 'yes']:
            assistant.test_components()
            input("\nAppuyez sur Entrée pour continuer...")
        
        # Lancer l'assistant
        assistant.run()
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()
