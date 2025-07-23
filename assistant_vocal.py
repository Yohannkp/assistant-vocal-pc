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
import os
import subprocess
import re
import time
import sys
import os
import subprocess
import re
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
        
        # Système de fonctions d'actions
        self.setup_action_system()
        
        print("🤖 Assistant Vocal initialisé")
        self.speak("Bonjour ! Je suis votre assistant vocal. Dites 'Assistant' pour me réveiller.")
    
    def setup_action_system(self):
        """Configure le système de fonctions d'actions"""
        # Dictionnaire des fonctions d'actions disponibles
        self.action_functions = {
            "ouvrir_application": self.action_ouvrir_application,
            "fermer_application": self.action_fermer_application,
            "lister_applications": self.action_lister_applications,
            "ouvrir_fichier": self.action_ouvrir_fichier,
            "rechercher_web": self.action_rechercher_web
        }
        
        # Mots-clés pour identifier les actions vs questions
        self.action_keywords = {
            "ouvrir": ["ouvre", "ouvrir", "lance", "lancer", "démarre", "démarrer", "exécute", "exécuter"],
            "fermer": ["ferme", "fermer", "quitte", "quitter", "arrête", "arrêter", "termine", "terminer"],
            "lister": ["liste", "lister", "montre", "montrer", "affiche", "afficher", "applications"],
            "rechercher": ["recherche", "cherche", "trouve", "google", "bing"],
            "naviguer": ["va sur", "navigue", "visite", "site"]
        }
        
        # Charger les applications scannées
        self.load_scanned_applications()
        
        # Si pas d'applications scannées, utiliser la liste de base
        if not hasattr(self, 'applications') or not self.applications:
            self.setup_default_applications()
    
    def load_scanned_applications(self):
        """Charge les applications depuis le fichier scanné"""
        try:
            applications_file = os.path.join(os.path.dirname(__file__), "applications_assistant.json")
            if os.path.exists(applications_file):
                with open(applications_file, 'r', encoding='utf-8') as f:
                    scanned_apps = json.load(f)
                
                print(f"📱 {len(scanned_apps)} applications chargées depuis le scan")
                
                # Convertir au format interne
                self.applications = {}
                self.app_commands_map = {}  # Mapping commandes vocales -> app key
                
                for app_key, app_data in scanned_apps.items():
                    self.applications[app_key] = {
                        "nom": app_data["nom"],
                        "chemin": app_data["chemin"],
                        "processus": app_data["processus"]
                    }
                    
                    # Créer le mapping des commandes vocales
                    for command in app_data.get("commandes", []):
                        self.app_commands_map[command.lower()] = app_key
                
                print(f"🎯 {len(self.app_commands_map)} commandes vocales mappées")
                return True
                
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des applications: {e}")
            return False
    
    def setup_default_applications(self):
        """Configuration des applications de base (fallback)"""
        print("📱 Utilisation de la liste d'applications par défaut")
        
        # Applications connues avec leurs chemins
        self.applications = {
            "chrome": {
                "nom": "Google Chrome",
                "chemin": "chrome",
                "processus": "chrome.exe"
            },
            "firefox": {
                "nom": "Mozilla Firefox",
                "chemin": "firefox",
                "processus": "firefox.exe"
            },
            "notepad": {
                "nom": "Bloc-notes",
                "chemin": "notepad",
                "processus": "notepad.exe"
            },
            "calculatrice": {
                "nom": "Calculatrice",
                "chemin": "calc",
                "processus": "calc.exe"
            },
            "word": {
                "nom": "Microsoft Word",
                "chemin": "winword",
                "processus": "winword.exe"
            },
            "excel": {
                "nom": "Microsoft Excel",
                "chemin": "excel",
                "processus": "excel.exe"
            },
            "vscode": {
                "nom": "Visual Studio Code",
                "chemin": "code",
                "processus": "code.exe"
            }
        }
        
        # Mapping simple pour les applications par défaut
        self.app_commands_map = {}
        for app_key, app_data in self.applications.items():
            self.app_commands_map[app_key] = app_key
            # Ajouter des variations du nom
            name_words = app_data["nom"].lower().split()
            for word in name_words:
                if len(word) > 2:
                    self.app_commands_map[word] = app_key
    
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
    
    # ========================================
    # SYSTÈME DE FONCTIONS D'ACTIONS
    # ========================================
    
    def categorize_request(self, command):
        """Catégorise une demande : ACTION ou QUESTION"""
        command_lower = command.lower()
        
        # Vérifier les mots-clés d'action
        for category, keywords in self.action_keywords.items():
            for keyword in keywords:
                if keyword in command_lower:
                    return "ACTION", category, command
        
        # Si aucun mot-clé d'action trouvé, c'est une question
        return "QUESTION", None, command
    
    def analyze_action_request(self, command, action_type):
        """Analyse une demande d'action et détermine la fonction à exécuter"""
        command_lower = command.lower()
        
        if action_type == "ouvrir":
            # Chercher quelle application ouvrir avec la fonction améliorée
            app_key, app_data = self.find_application(command)
            if app_key:
                return "ouvrir_application", {"application": app_key}
            
            # Si aucune application spécifique trouvée
            return "ouvrir_application", {"application": "inconnue", "command": command}
        
        elif action_type == "lister":
            # Commande de listage des applications
            return "lister_applications", {}
        
        elif action_type == "fermer":
            # Chercher quelle application fermer
            for app_key, app_info in self.applications.items():
                if app_key in command_lower or app_info["nom"].lower() in command_lower:
                    return "fermer_application", {"application": app_key}
            
            return "fermer_application", {"application": "inconnue", "command": command}
        
        elif action_type == "rechercher":
            # Extraire ce qu'il faut rechercher
            patterns = [
                r"recherche\s+(.+)",
                r"cherche\s+(.+)",
                r"trouve\s+(.+)",
                r"google\s+(.+)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, command_lower)
                if match:
                    return "rechercher_web", {"query": match.group(1).strip()}
            
            return "rechercher_web", {"query": "inconnue", "command": command}
        
        return None, None
    
    def find_application(self, query):
        """Trouve une application correspondant à la requête avec IA directe intelligente"""
        query = query.lower().strip()
        
        print(f"🔍 Recherche d'application pour: '{query}'")
        
        # 🤖 NOUVELLE APPROCHE: Demander directement à l'IA ce que l'utilisateur veut
        print("🤖 Analyse IA directe de la demande...")
        ai_result = self.ai_smart_app_search("", query)  # Pas d'extraction, analyse directe
        if ai_result:
            return ai_result
        
        # ======================================================================
        # FALLBACK: Méthodes classiques seulement si l'IA échoue
        # ======================================================================
        
        # Extraire le nom de l'application avec plusieurs patterns (fallback uniquement)
        app_name = query
        
        # Pattern 1: "ouvre/lance [l'application] <nom>"
        patterns = [
            r"(?:je veux que tu|je voudrais que tu)\s+(?:ouvres?|lances?|démarres?)\s+(.+)",
            r"(?:ouvre|ouvrir|lance|lancer|démarre|démarrer|exécute|exécuter)\s+(?:l'application\s+)?(.+)",
            r"(?:ouvre|ouvrir|lance|lancer|démarre|démarrer|exécute|exécuter)\s+(.+)",
            r"(?:je veux|j'aimerais|besoin de)\s+(?:regarder|voir|écouter|utiliser)\s+(?:un|une|le|la|des)?\s*(.+)",
            r"(.+)"  # Fallback : prendre tout
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                app_name = match.group(1).strip()
                # Enlever les mots parasites
                app_name = re.sub(r'\b(?:l\'application|application|le|la|les|un|une|de|pour|à)\b', '', app_name).strip()
                # Si le nom est trop court ou vide après nettoyage, ignorer ce pattern
                if len(app_name.strip()) < 3:
                    continue
                break
        
        print(f"🎯 Nom d'application extrait (fallback): '{app_name}'")
        
        # Recherche 1: Dans les commandes vocales mappées (recherche exacte d'abord)
        if hasattr(self, 'app_commands_map'):
            # Recherche exacte
            if app_name in self.app_commands_map:
                app_key = self.app_commands_map[app_name]
                print(f"✅ Trouvé via commande exacte: '{app_name}' → {app_key}")
                return app_key, self.applications[app_key]
            
            # Recherche contient avec critères stricts
            for command, app_key in self.app_commands_map.items():
                # Éviter les matches trop courts et mots courants pour réduire faux positifs
                excluded_words = {'de', 'le', 'la', 'un', 'une', 'me', 'ai', 'et', 'ou', 'du'}
                if len(app_name) > 4 and app_name.lower() not in excluded_words and (app_name in command or command in app_name):
                    print(f"✅ Trouvé via commande: '{command}' → {app_key}")
                    return app_key, self.applications[app_key]
        
        # Recherche 2: Recherche spécifique pour applications populaires
        specific_mappings = {
            "netflix": ["netflix", "4df9e0f8.netflix"],
            "chrome": ["chrome", "google chrome"],
            "firefox": ["firefox", "mozilla firefox"],
            "word": ["word", "microsoft word", "winword"],
            "excel": ["excel", "microsoft excel"],
            "powerpoint": ["powerpoint", "microsoft powerpoint"],
            "outlook": ["outlook", "microsoft outlook"],
            "notepad": ["notepad", "bloc-notes", "bloc notes"],
            "calculator": ["calc", "calculatrice"],
            "paint": ["paint", "peinture"],
            "skype": ["skype"],
            "discord": ["discord"],
            "spotify": ["spotify"],
            "vlc": ["vlc", "vlc media player"],
            "steam": ["steam"],
            "adobe": ["adobe"],
            "photoshop": ["photoshop"]
        }
        
        for app_type, keywords in specific_mappings.items():
            for keyword in keywords:
                if keyword in app_name or app_name in keyword:
                    # Priorité aux correspondances exactes
                    exact_matches = []
                    partial_matches = []
                    
                    for app_key, app_data in self.applications.items():
                        app_key_lower = app_key.lower()
                        app_nom_lower = app_data["nom"].lower()
                        
                        # Correspondance exacte prioritaire
                        if (keyword == app_key_lower or 
                            keyword in app_key_lower.split() or 
                            app_type in app_key_lower):
                            exact_matches.append((app_key, app_data))
                        # Correspondance partielle
                        elif keyword in app_key_lower or keyword in app_nom_lower:
                            partial_matches.append((app_key, app_data))
                    
                    # Prioriser les correspondances exactes
                    best_matches = exact_matches if exact_matches else partial_matches
                    
                    if best_matches:
                        app_key, app_data = best_matches[0]  # Prendre la première
                        print(f"✅ Trouvé via mapping spécifique: '{keyword}' → {app_key}")
                        return app_key, app_data
        
        # Recherche 3: Dans les noms d'applications (recherche contient)
        # Recherche 3: Dans les noms d'applications (recherche contient)
        for app_key, app_data in self.applications.items():
            nom_lower = app_data["nom"].lower()
            app_key_lower = app_key.lower()
            
            # Recherche bidirectionnelle - mais éviter les correspondances trop courtes
            if len(app_name) > 3:  # Éviter les matches sur "de", "le", etc.
                if (app_name in nom_lower or nom_lower in app_name or 
                    app_name in app_key_lower or app_key_lower in app_name):
                    print(f"✅ Trouvé via nom: '{app_data['nom']}' (clé: {app_key})")
                    return app_key, app_data
        
        # Recherche 4: Recherche partielle dans les mots du nom (plus stricte)
        for app_key, app_data in self.applications.items():
            nom_mots = app_data["nom"].lower().split()
            for mot in nom_mots:
                if len(mot) > 3 and len(app_name) > 3:  # Mots plus longs uniquement
                    if (app_name in mot or mot in app_name) and abs(len(app_name) - len(mot)) <= 3:
                        print(f"✅ Trouvé via mot: '{mot}' dans '{app_data['nom']}'")
                        return app_key, app_data
        
        # Recherche 5: Recherche fuzzy pour les noms similaires (plus stricte)
        for app_key, app_data in self.applications.items():
            nom_clean = ''.join(c for c in app_data["nom"].lower() if c.isalnum())
            app_name_clean = ''.join(c for c in app_name if c.isalnum())
            
            if len(app_name_clean) > 3 and len(nom_clean) > 3:
                if app_name_clean in nom_clean or nom_clean in app_name_clean:
                    # Vérifier que c'est une correspondance raisonnable (pas trop de différence de taille)
                    if abs(len(app_name_clean) - len(nom_clean)) <= max(len(app_name_clean), len(nom_clean)) // 2:
                        print(f"✅ Trouvé via recherche fuzzy: '{app_data['nom']}'")
                        return app_key, app_data
        
        print(f"❌ Aucune application trouvée pour: '{app_name}'")
        
        # 🤖 NOUVELLE FONCTIONNALITÉ IA : Recherche intelligente avec Mistral
        print("🤖 Activation de la recherche IA intelligente...")
        ai_result = self.ai_smart_app_search(app_name, query)
        if ai_result:
            return ai_result
        
        return None, None
    
    def generate_uwp_variants(self, base_id, app_key):
        """Génère des variantes d'ID UWP pour maximiser les chances d'ouverture"""
        variants = []
        
        # Variante 1: ID de base (tel qu'il est dans le fichier)
        variants.append(base_id)
        
        # Variante 2: Avec PackageFamilyName complet
        if not "_mcm4njqhnhss8" in base_id and "netflix" in app_key.lower():
            variants.append(f"{base_id}_mcm4njqhnhss8")
        
        # Variante 3: Avec Application ID complet (format !App)
        if not "!" in base_id:
            if "netflix" in app_key.lower():
                variants.append(f"{base_id}_mcm4njqhnhss8!Netflix.App")
            else:
                # Format générique pour autres apps
                variants.append(f"{base_id}!App")
        
        # Variante 4: Si l'ID contient déjà le PackageFamilyName, ajouter !App
        if "_mcm4njqhnhss8" in base_id and "!" not in base_id:
            if "netflix" in app_key.lower():
                variants.append(f"{base_id}!Netflix.App")
            else:
                variants.append(f"{base_id}!App")
        
        # Variante 5: ID simplifié (juste le nom de package)
        if "." in base_id:
            package_name = base_id.split(".")[0] + "." + base_id.split(".")[1]
            if package_name not in variants:
                variants.append(package_name)
        
        # Enlever les doublons tout en préservant l'ordre
        unique_variants = []
        for v in variants:
            if v not in unique_variants:
                unique_variants.append(v)
        
        print(f"🧬 Générés {len(unique_variants)} variants UWP pour {app_key}")
        for i, variant in enumerate(unique_variants, 1):
            print(f"   {i}. {variant}")
        
        return unique_variants

    def ai_smart_app_search(self, app_name, original_query):
        """Utilise l'IA pour une recherche intelligente directe d'applications"""
        try:
            # Créer une liste des applications disponibles pour l'IA avec les plus importantes en premier
            important_apps = []
            other_apps = []
            
            for app_key, app_data in self.applications.items():
                app_line = f"- {app_data['nom']} (clé: {app_key})"
                
                # Prioriser les applications importantes
                if any(keyword in app_key.lower() for keyword in ['netflix', 'chrome', 'firefox', 'edge', 'vlc', 'spotify', 'word', 'excel']):
                    important_apps.append(app_line)
                else:
                    other_apps.append(app_line)
            
            # Limiter la liste pour éviter une requête trop longue
            selected_apps = important_apps[:20] + other_apps[:40]
            apps_list = "\n".join(selected_apps)
            
            # 🤖 REQUÊTE IA AMÉLIORÉE avec exemples concrets
            ai_prompt = f"""
ANALYSE DIRECTE DE LA DEMANDE UTILISATEUR:

PHRASE COMPLÈTE: "{original_query}"

APPLICATIONS DISPONIBLES:
{apps_list}

INSTRUCTIONS PRÉCISES:
1. Analyse la phrase complète de l'utilisateur
2. Identifie EXACTEMENT quelle application il veut ouvrir
3. EXEMPLES CONCRETS:
   - "je veux que tu ouvres Netflix" → cherche "netflix" dans la liste → réponse: "4df9e0f8.netflix"
   - "lance le navigateur" → cherche "chrome" ou "firefox" ou "edge" → réponse: "google chrome" ou "firefox"
   - "je veux regarder un film" → cherche "netflix" ou "vlc" → réponse: "4df9e0f8.netflix" ou "vlc media player"
   - "ouvre Word" → cherche "word" → réponse: "microsoft word"

4. Réponds UNIQUEMENT avec la clé exacte de l'application (ce qui est entre parenthèses)
5. Si aucune correspondance évidente, réponds "AUCUNE"
6. Ne te laisse pas tromper par des mots parasites

RÉPONSE (clé exacte uniquement):"""
            
            print("🤖 Consultation IA directe...")
            ai_response = self.query_mistral(ai_prompt)
            
            if ai_response and ai_response.strip().lower() != "aucune":
                # Nettoyer la réponse IA
                ai_key = ai_response.strip().lower()
                
                # Vérifier si la clé existe
                if ai_key in self.applications:
                    print(f"✅ IA a identifié directement: '{ai_key}' → {self.applications[ai_key]['nom']}")
                    return ai_key, self.applications[ai_key]
                
                # Recherche fuzzy sur la réponse IA
                for app_key, app_data in self.applications.items():
                    if ai_key in app_key.lower() or app_key.lower() in ai_key:
                        print(f"✅ IA a suggéré (correspondance): '{app_key}' → {app_data['nom']}")
                        return app_key, app_data
                        
            print("🤖 L'IA n'a pas identifié d'application correspondante")
            return None
            
        except Exception as e:
            print(f"❌ Erreur recherche IA: {e}")
            return None
    
    def ai_suggest_alternatives(self, failed_app_name):
        """L'IA suggère des applications alternatives"""
        try:
            # Prendre un échantillon d'applications populaires
            popular_apps = []
            for app_key, app_data in list(self.applications.items())[:30]:
                popular_apps.append(f"- {app_data['nom']}")
            
            apps_list = "\n".join(popular_apps)
            
            ai_prompt = f"""
L'utilisateur a demandé "{failed_app_name}" mais cette application n'a pas été trouvée.

APPLICATIONS DISPONIBLES:
{apps_list}

Suggère 3 applications similaires ou alternatives qui pourraient l'intéresser.
Réponds de manière concise et naturelle en français.
Format: "Voici quelques alternatives : [app1], [app2], [app3]"
"""
            
            response = self.query_mistral(ai_prompt)
            return response if response else "Je n'ai pas pu trouver d'alternatives appropriées."
            
        except Exception as e:
            print(f"❌ Erreur suggestions IA: {e}")
            return "Erreur lors de la génération de suggestions."
    
    def ai_help_context(self, user_query):
        """L'IA génère de l'aide contextuelle"""
        try:
            ai_prompt = f"""
L'utilisateur a dit: "{user_query}"

Tu es un assistant vocal PC. Fournis une aide courte et pratique en français.
Explique ce que l'utilisateur peut faire ou comment reformuler sa demande.
Sois concis (max 2 phrases).
"""
            
            response = self.query_mistral(ai_prompt)
            return response if response else "Je peux vous aider avec l'ouverture d'applications, des recherches web, ou répondre à vos questions."
            
        except Exception as e:
            print(f"❌ Erreur aide IA: {e}")
            return "Aide non disponible pour le moment."
    
    def ai_analyze_command(self, command):
        """L'IA analyse une commande ambiguë pour mieux la catégoriser"""
        try:
            ai_prompt = f"""
Analyse cette commande utilisateur: "{command}"

CATÉGORIES POSSIBLES:
- ACTION_OUVRIR: ouvrir/lancer une application
- ACTION_FERMER: fermer une application
- ACTION_LISTER: lister les applications
- ACTION_RECHERCHER: recherche web
- QUESTION: question générale

Réponds UNIQUEMENT avec une des catégories ci-dessus.
Si c'est ambigü, choisis la catégorie la plus probable.

RÉPONSE:"""
            
            response = self.query_mistral(ai_prompt)
            return response.strip() if response else "QUESTION"
            
        except Exception as e:
            print(f"❌ Erreur analyse IA: {e}")
            return "QUESTION"

    def action_ouvrir_application(self, params):
        """Ouvre une application avec gestion spéciale pour les apps UWP"""
        app_name = params.get("application", "inconnue")
        
        if app_name == "inconnue":
            return False, "Je n'ai pas compris quelle application vous voulez ouvrir. Essayez : 'Ouvre Chrome' ou 'Lance le bloc-notes'"
        
        # Utiliser la nouvelle fonction de recherche améliorée
        app_key, app_data = self.find_application(app_name)
        
        if not app_key or not app_data:
            # 🤖 AMÉLIORATION IA : Suggestions intelligentes d'alternatives
            print("🤖 Génération de suggestions IA...")
            ai_suggestions = self.ai_suggest_alternatives(app_name)
            
            # Retourner le message avec suggestions IA
            return False, f"L'application '{app_name}' n'a pas été trouvée. {ai_suggestions}"
        
        try:
            print(f"🚀 Tentative d'ouverture de {app_data['nom']}...")
            chemin = app_data["chemin"]
            
            # Détecter si c'est une application UWP (Windows Store)
            if "shell:appsfolder" in chemin or "start shell:appsfolder" in chemin:
                print("📱 Application UWP détectée")
                
                # Extraire l'ID de l'application UWP
                if "start shell:appsfolder\\" in chemin:
                    app_id = chemin.replace("start shell:appsfolder\\", "")
                elif "shell:appsfolder\\" in chemin:
                    app_id = chemin.replace("shell:appsfolder\\", "")
                else:
                    app_id = chemin
                
                print(f"🔍 ID UWP initial: {app_id}")
                
                # Optimisation intelligente pour UWP : tester plusieurs variantes d'ID
                uwp_variants = self.generate_uwp_variants(app_id, app_key)
                
                for i, variant in enumerate(uwp_variants, 1):
                    print(f"🧪 Test UWP variant {i}: {variant}")
                    
                    # Priorité à PowerShell qui fonctionne le mieux pour UWP
                    try:
                        cmd = f'powershell -Command "Start-Process \\"shell:appsfolder\\{variant}\\""'
                        print(f"🔧 Commande PowerShell: {cmd}")
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
                        if result.returncode == 0:
                            print(f"✅ Succès avec PowerShell ! Variant: {variant}")
                            return True, f"✅ {app_data['nom']} a été ouvert avec succès !"
                        else:
                            print(f"❌ PowerShell variant {i} échoué")
                    except Exception as e:
                        print(f"❌ Exception PowerShell variant {i}: {e}")
                    
                    # Si PowerShell échoue, tester Explorer
                    try:
                        cmd = f'explorer "shell:appsfolder\\{variant}"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=6)
                        if result.returncode == 0:
                            print(f"✅ Succès avec Explorer ! Variant: {variant}")
                            return True, f"✅ {app_data['nom']} a été ouvert avec succès !"
                    except Exception as e:
                        print(f"❌ Exception Explorer variant {i}: {e}")
                
                return False, f"❌ Impossible d'ouvrir l'application UWP {app_data['nom']}. Tous les variants testés ont échoué."
            
            else:
                # Application classique (non-UWP) - Le chemin est déjà correct grâce au scanner avancé
                print("🖥️ Application classique détectée")
                
                # Méthode 1: Chemin direct
                try:
                    print(f"🔧 Ouverture avec chemin scanné: {chemin}")
                    subprocess.Popen(chemin, shell=True)
                    return True, f"✅ {app_data['nom']} a été ouvert avec succès !"
                    
                except Exception as e1:
                    print(f"❌ Méthode directe échouée: {e1}")
                    
                    # Méthode 2: Avec start
                    try:
                        cmd = f'start "" "{chemin}"'
                        print(f"🔧 Tentative avec start: {cmd}")
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            return True, f"✅ {app_data['nom']} est en cours d'ouverture..."
                        else:
                            print(f"❌ Start command failed with code {result.returncode}")
                            print(f"❌ Stderr: {result.stderr}")
                            return False, f"❌ Impossible d'ouvrir {app_data['nom']}. Vérifiez que l'application est toujours installée."
                    except Exception as e2:
                        print(f"❌ Méthode start échouée: {e2}")
                        return False, f"❌ Impossible d'ouvrir {app_data['nom']}. Application peut-être non accessible."
                    
        except Exception as e:
            return False, f"❌ Erreur lors de l'ouverture de {app_data['nom']} : {str(e)}"
    
    def action_lister_applications(self, params=None):
        """Liste les applications disponibles"""
        try:
            total_apps = len(self.applications)
            
            # Prendre les 20 premières applications pour ne pas surcharger
            apps_sample = list(self.applications.items())[:20]
            apps_names = [app_data["nom"] for _, app_data in apps_sample]
            
            message = f"J'ai {total_apps} applications disponibles. Voici les principales : {', '.join(apps_names[:10])}"
            
            if total_apps > 10:
                message += f" et {total_apps - 10} autres."
            
            return True, message
            
        except Exception as e:
            return False, f"Erreur lors de la liste des applications : {str(e)}"

    def action_fermer_application(self, params):
        """Ferme une application"""
        app_name = params.get("application", "inconnue")
        
        if app_name == "inconnue":
            return False, "Je n'ai pas compris quelle application vous voulez fermer."
        
        if app_name not in self.applications:
            return False, f"L'application '{app_name}' n'est pas dans ma liste d'applications connues."
        
        app_info = self.applications[app_name]
        
        try:
            # Utiliser taskkill pour fermer l'application
            result = subprocess.run(f'taskkill /F /IM "{app_info["processus"]}"', shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"✅ {app_info['nom']} a été fermé avec succès !"
            else:
                return False, f"❌ {app_info['nom']} n'est pas en cours d'exécution ou impossible à fermer."
                
        except Exception as e:
            return False, f"❌ Erreur lors de la fermeture de {app_info['nom']} : {str(e)}"
    
    def action_ouvrir_fichier(self, params):
        """Ouvre un fichier (à implémenter)"""
        return False, "La fonction d'ouverture de fichiers n'est pas encore implémentée."
    
    def action_rechercher_web(self, params):
        """Effectue une recherche web"""
        query = params.get("query", "inconnue")
        
        if query == "inconnue":
            return False, "Je n'ai pas compris ce que vous voulez rechercher."
        
        try:
            # Créer l'URL de recherche Google
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            # Ouvrir dans le navigateur par défaut
            result = subprocess.run(f'start "" "{search_url}"', shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return True, f"✅ Recherche lancée pour : {query}"
            else:
                return False, f"❌ Impossible de lancer la recherche pour : {query}"
                
        except Exception as e:
            return False, f"❌ Erreur lors de la recherche : {str(e)}"
    
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
        """Traite une commande vocale avec système de catégorisation intelligent"""
        command_lower = command.lower()
        
        # Commandes spéciales de contrôle de l'assistant (priorité absolue)
        if any(word in command_lower for word in ['arrêt', 'stop', 'au revoir', 'fermer assistant', 'arrête toi']):
            self.speak("Commande d'arrêt reçue. Au revoir ! À bientôt.")
            self.active = False
            return
        
        if any(word in command_lower for word in ['silence', 'tais-toi', 'chut']):
            self.speak("Commande de silence reçue. D'accord, je me tais.")
            return
        
        # Commandes de test et configuration voix
        if any(word in command_lower for word in ['test voix', 'test audio']):
            self.speak("Test de la synthèse vocale en cours.")
            time.sleep(0.5)
            if self.current_tts_method == "coqui":
                self.speak("Vous entendez actuellement la voix Coqui TTS.")
            else:
                self.speak("Vous entendez actuellement la voix française Hortense Windows. Dites 'voix naturelle' pour essayer Coqui TTS si disponible.")
            return
        
        if any(word in command_lower for word in ['voix naturelle', 'coqui', 'meilleure voix']):
            if COQUI_AVAILABLE and self.coqui_engine:
                self.current_tts_method = "coqui"
                self.speak("Basculement vers la voix Coqui TTS. Attention, cette voix peut avoir un léger accent anglais.")
            else:
                self.speak("La voix Coqui TTS n'est pas disponible. Utilisation de la voix française Windows.")
            return
        
        if any(word in command_lower for word in ['voix française', 'voix windows', 'voix classique', 'sapi', 'hortense']):
            self.current_tts_method = "sapi"
            self.speak("Basculement vers la voix française Windows Hortense.")
            return
        
        # 🤖 NOUVELLE COMMANDE IA : Aide contextuelle
        if any(word in command_lower for word in ['aide', 'help', 'comment', 'que puis-je', 'guide']):
            print("🤖 Génération d'aide contextuelle par l'IA...")
            ai_help = self.ai_help_context(command)
            self.speak(ai_help)
            return
        
        # ========================================
        # NOUVEAU SYSTÈME DE CATÉGORISATION + IA
        # ========================================
        
        print(f"🔍 Analyse de la demande : {command}")
        
        # Étape 1: Catégoriser la demande
        request_type, action_type, original_command = self.categorize_request(command)
        
        print(f"📊 Type de demande : {request_type}")
        if action_type:
            print(f"🎯 Type d'action : {action_type}")
        
        # 🤖 AMÉLIORATION IA : Si la catégorisation échoue, demander à l'IA
        if request_type == "QUESTION" and not action_type:
            ai_analysis = self.ai_analyze_command(command)
            if ai_analysis and ai_analysis != "QUESTION":
                print(f"🤖 L'IA a recatégorisé en: {ai_analysis}")
                if ai_analysis in ["ACTION_OUVRIR", "ACTION_FERMER", "ACTION_LISTER"]:
                    request_type = "ACTION"
                    action_type = ai_analysis.replace("ACTION_", "").lower()
        
        if request_type == "ACTION":
            # C'est une action à exécuter
            self.speak(f"Action détectée : {action_type}. Je traite votre demande.")
            
            # Analyser les détails de l'action
            function_name, params = self.analyze_action_request(command, action_type)
            
            if function_name and function_name in self.action_functions:
                print(f"🔧 Exécution de la fonction : {function_name}")
                print(f"📋 Paramètres : {params}")
                
                # Exécuter la fonction d'action
                try:
                    success, message = self.action_functions[function_name](params)
                    
                    if success:
                        print(f"✅ Action réussie : {message}")
                        self.speak(message)
                    else:
                        print(f"❌ Action échouée : {message}")
                        self.speak(message)
                        
                except Exception as e:
                    error_msg = f"Erreur lors de l'exécution de l'action : {str(e)}"
                    print(f"❌ {error_msg}")
                    self.speak(error_msg)
            else:
                # Action non supportée
                unsupported_msg = f"Je ne peux pas effectuer cette action pour le moment. Action demandée : {action_type}"
                print(f"⚠️ {unsupported_msg}")
                self.speak(unsupported_msg)
                
        elif request_type == "QUESTION":
            # C'est une question - envoyer à Mistral
            print("❓ Question détectée - Envoi à Mistral")
            self.speak("Question détectée. Je consulte Mistral pour vous répondre.")
            
            try:
                response = self.query_mistral(command)
                
                if response and response.strip():
                    print(f"📝 Réponse Mistral: {response}")
                    self.speak("Réponse reçue de Mistral avec succès.")
                    time.sleep(0.3)
                    self.speak(response)
                else:
                    error_msg = "Mistral n'a pas pu générer de réponse."
                    print(f"❌ {error_msg}")
                    self.speak(error_msg)
                    
            except Exception as e:
                error_details = str(e)
                error_msg = f"Erreur lors de la consultation de Mistral : {error_details}"
                print(f"❌ {error_msg}")
                self.speak("Une erreur s'est produite lors de la consultation de Mistral.")
        
        # Confirmation de fin de traitement
        self.speak("Traitement terminé avec succès !")
    
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
