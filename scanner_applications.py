"""
Scanneur d'Applications Windows - Version Avancée
=================================================

Ce script scanne l'ordinateur pour trouver toutes les applications installées
avec leurs VRAIS chemins d'exécution, sans aucune configuration manuelle.

Nouvelles fonctionnalités :
- Détection automatique des vrais chemins d'exécution
- Scan approfondi des registres Windows
- Résolution intelligente des raccourcis
- Détection des variables d'environnement
- Validation des chemins trouvés
- Gestion optimisée des applications UWP/Store
"""

import os
import winreg
import json
import subprocess
import re
import shutil
from pathlib import Path
import glob

class AdvancedApplicationScanner:
    def __init__(self):
        self.applications = {}
        self.found_executables = {}
        
        # Méthodes de scan prioritaires
        self.scan_methods = [
            self.scan_registry_uninstall,
            self.scan_registry_app_paths,
            self.scan_start_menu_shortcuts,
            self.scan_program_directories,
            self.scan_uwp_applications,
            self.scan_environment_path,
            self.scan_known_locations
        ]
        
        # Locations importantes à scanner
        self.scan_locations = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expanduser(r"~\AppData\Local"),
            os.path.expanduser(r"~\AppData\Roaming"),
            r"C:\Windows\System32",
            r"C:\Windows\SysWOW64"
        ]
        
    def scan_registry_uninstall(self):
        """Scan approfondi du registre des programmes installés"""
        print("🔍 Scan approfondi du registre Windows...")
        
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for hkey, subkey_path in registry_keys:
            try:
                with winreg.OpenKey(hkey, subkey_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                self._extract_app_from_registry(subkey)
                        except Exception:
                            continue
            except Exception as e:
                print(f"⚠️ Erreur registre {subkey_path}: {e}")
    
    def scan_registry_app_paths(self):
        """Scan des chemins d'applications dans le registre"""
        print("🔍 Scan des chemins d'applications du registre...")
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        app_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, app_name) as app_key:
                            try:
                                path = winreg.QueryValueEx(app_key, "")[0]
                                if path and os.path.exists(path):
                                    clean_name = self.clean_app_name(app_name.replace('.exe', ''))
                                    if clean_name:
                                        self._add_application(clean_name, {
                                            "nom": clean_name,
                                            "chemin": path,
                                            "processus": app_name,
                                            "source": "registre_app_paths"
                                        })
                            except FileNotFoundError:
                                pass
                    except Exception:
                        continue
        except Exception as e:
            print(f"⚠️ Erreur App Paths: {e}")
    
    def scan_start_menu_shortcuts(self):
        """Scan intelligent des raccourcis du menu Démarrer"""
        print("🔍 Scan intelligent des raccourcis...")
        
        start_menu_paths = [
            os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        ]
        
        for start_path in start_menu_paths:
            if os.path.exists(start_path):
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if file.endswith('.lnk'):
                            shortcut_path = os.path.join(root, file)
                            self._process_shortcut(shortcut_path)
    
    def scan_program_directories(self):
        """Scan intelligent des dossiers de programmes"""
        print("🔍 Scan intelligent des dossiers de programmes...")
        
        for location in self.scan_locations:
            if os.path.exists(location):
                try:
                    for item in os.listdir(location):
                        item_path = os.path.join(location, item)
                        if os.path.isdir(item_path):
                            self._scan_directory_for_apps(item_path, item)
                except PermissionError:
                    continue
                except Exception:
                    continue
    
    def scan_uwp_applications(self):
        """Scan avancé des applications UWP/Store"""
        print("🔍 Scan avancé des applications UWP...")
        
        try:
            # Commande PowerShell améliorée pour UWP
            ps_command = """
            Get-AppxPackage | Where-Object {
                $_.Name -ne $null -and 
                $_.InstallLocation -ne $null -and
                $_.Name -notlike "*Microsoft.Windows*" -and
                $_.Name -notlike "*windows.immersivecontrolpanel*"
            } | ForEach-Object {
                [PSCustomObject]@{
                    Name = $_.Name
                    PackageFullName = $_.PackageFullName
                    InstallLocation = $_.InstallLocation
                    DisplayName = (Get-AppxPackageManifest $_).Package.Properties.DisplayName
                }
            } | ConvertTo-Json
            """
            
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    apps_data = json.loads(result.stdout)
                    if not isinstance(apps_data, list):
                        apps_data = [apps_data]
                    
                    for app in apps_data:
                        if app and app.get('Name'):
                            self._process_uwp_app(app)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"⚠️ Erreur scan UWP: {e}")
    
    def scan_environment_path(self):
        """Scan des applications dans le PATH système"""
        print("🔍 Scan du PATH système...")
        
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for path_dir in path_dirs:
            if os.path.exists(path_dir):
                try:
                    for file in os.listdir(path_dir):
                        if file.endswith('.exe'):
                            full_path = os.path.join(path_dir, file)
                            clean_name = self.clean_app_name(file.replace('.exe', ''))
                            if clean_name and self._is_valid_application(clean_name):
                                self._add_application(clean_name, {
                                    "nom": clean_name,
                                    "chemin": full_path,
                                    "processus": file,
                                    "source": "path_system"
                                })
                except (PermissionError, OSError):
                    continue
    
    def scan_known_locations(self):
        """Scan des locations connues pour applications populaires"""
        print("🔍 Scan des locations connues...")
        
        known_apps = {
            "Google Chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ],
            "Mozilla Firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            "Microsoft Edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ],
            "VLC Media Player": [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            ],
            "Notepad++": [
                r"C:\Program Files\Notepad++\notepad++.exe",
                r"C:\Program Files (x86)\Notepad++\notepad++.exe"
            ],
            "Visual Studio Code": [
                r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
                r"C:\Program Files\Microsoft VS Code\Code.exe"
            ]
        }
        
        for app_name, paths in known_apps.items():
            for path in paths:
                if os.path.exists(path):
                    clean_name = self.clean_app_name(app_name)
                    self._add_application(clean_name, {
                        "nom": app_name,
                        "chemin": path,
                        "processus": os.path.basename(path),
                        "source": "location_connue"
                    })
                    break  # Prendre le premier chemin valide trouvé
    
    def _extract_app_from_registry(self, subkey):
        """Extrait les informations d'une application depuis le registre"""
        try:
            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
            
            # Récupérer toutes les informations disponibles
            install_location = self._safe_registry_read(subkey, "InstallLocation")
            uninstall_string = self._safe_registry_read(subkey, "UninstallString")
            display_icon = self._safe_registry_read(subkey, "DisplayIcon")
            
            # Nettoyer le nom
            clean_name = self.clean_app_name(display_name)
            if not clean_name or len(clean_name) < 2:
                return
            
            # Trouver le vrai chemin d'exécution
            executable_path = self._find_executable_from_registry_data(
                install_location, uninstall_string, display_icon, clean_name
            )
            
            if executable_path:
                self._add_application(clean_name, {
                    "nom": display_name,
                    "chemin": executable_path,
                    "processus": os.path.basename(executable_path),
                    "source": "registre_uninstall",
                    "install_location": install_location
                })
                
        except FileNotFoundError:
            pass
        except Exception:
            pass
    
    def _safe_registry_read(self, key, value_name):
        """Lecture sécurisée d'une valeur de registre"""
        try:
            return winreg.QueryValueEx(key, value_name)[0]
        except FileNotFoundError:
            return ""
        except Exception:
            return ""
    
    def _find_executable_from_registry_data(self, install_location, uninstall_string, display_icon, app_name):
        """Trouve le vrai exécutable à partir des données du registre"""
        
        # Méthode 1: Utiliser l'icône d'affichage si c'est un .exe
        if display_icon and display_icon.endswith('.exe') and os.path.exists(display_icon):
            return display_icon
        
        # Méthode 2: Chercher dans le dossier d'installation
        if install_location and os.path.exists(install_location):
            main_exe = self._find_main_executable_in_directory(install_location, app_name)
            if main_exe:
                return main_exe
        
        # Méthode 3: Analyser la chaîne de désinstallation
        if uninstall_string:
            exe_from_uninstall = self._extract_exe_from_uninstall_string(uninstall_string)
            if exe_from_uninstall and os.path.exists(exe_from_uninstall):
                return exe_from_uninstall
        
        return None
    
    def _find_main_executable_in_directory(self, directory, app_name):
        """Trouve l'exécutable principal dans un dossier"""
        if not os.path.exists(directory):
            return None
        
        # Patterns de noms prioritaires
        app_name_clean = re.sub(r'[^a-zA-Z0-9]', '', app_name.lower())
        priority_patterns = [
            f"{app_name_clean}.exe",
            f"{app_name.lower().replace(' ', '')}.exe",
            f"{app_name.split()[0].lower()}.exe"
        ]
        
        # Chercher d'abord les executables prioritaires
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.exe'):
                    file_lower = file.lower()
                    # Vérifier les patterns prioritaires
                    for pattern in priority_patterns:
                        if file_lower == pattern:
                            return os.path.join(root, file)
        
        # Si pas trouvé, chercher le premier exécutable principal
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.exe'):
                    # Éviter les outils et installeurs
                    if not any(skip in file.lower() for skip in 
                             ['uninstall', 'setup', 'installer', 'updater', 'launcher', 'helper']):
                        return os.path.join(root, file)
        
        return None
    
    def _extract_exe_from_uninstall_string(self, uninstall_string):
        """Extrait le chemin d'un .exe depuis une chaîne de désinstallation"""
        # Patterns pour extraire le chemin d'un exe
        patterns = [
            r'"([^"]+\.exe)"',  # Exe entre guillemets
            r'(\S+\.exe)',      # Exe sans guillemets
        ]
        
        for pattern in patterns:
            match = re.search(pattern, uninstall_string)
            if match:
                potential_exe = match.group(1)
                # Chercher dans le même dossier pour l'exe principal
                if os.path.exists(potential_exe):
                    directory = os.path.dirname(potential_exe)
                    main_exe = self._find_main_executable_in_directory(directory, "")
                    return main_exe if main_exe else potential_exe
        
        return None
    
    def _process_shortcut(self, shortcut_path):
        """Traite un raccourci .lnk"""
        try:
            app_name = os.path.splitext(os.path.basename(shortcut_path))[0]
            clean_name = self.clean_app_name(app_name)
            
            if not clean_name or len(clean_name) < 2:
                return
            
            # Résoudre le raccourci
            target = self._resolve_shortcut_target(shortcut_path)
            if target and os.path.exists(target) and target.endswith('.exe'):
                self._add_application(clean_name, {
                    "nom": app_name,
                    "chemin": target,
                    "processus": os.path.basename(target),
                    "source": "raccourci_menu",
                    "shortcut_path": shortcut_path
                })
        except Exception:
            pass
    
    def _resolve_shortcut_target(self, shortcut_path):
        """Résout la cible d'un raccourci .lnk"""
        try:
            # Méthode 1: Utiliser win32com si disponible
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(shortcut_path)
                return shortcut.TargetPath
            except ImportError:
                pass
            
            # Méthode 2: Utiliser PowerShell
            try:
                ps_command = f"""
                $sh = New-Object -ComObject WScript.Shell
                $shortcut = $sh.CreateShortcut('{shortcut_path}')
                $shortcut.TargetPath
                """
                result = subprocess.run([
                    "powershell", "-Command", ps_command
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass
                
        except Exception:
            pass
        
        return None
    
    def _scan_directory_for_apps(self, directory, folder_name):
        """Scan un dossier pour des applications"""
        try:
            main_exe = self._find_main_executable_in_directory(directory, folder_name)
            if main_exe:
                clean_name = self.clean_app_name(folder_name)
                if clean_name and len(clean_name) > 2:
                    self._add_application(clean_name, {
                        "nom": folder_name,
                        "chemin": main_exe,
                        "processus": os.path.basename(main_exe),
                        "source": "scan_dossier",
                        "install_directory": directory
                    })
        except Exception:
            pass
    
    def _process_uwp_app(self, app_data):
        """Traite une application UWP"""
        try:
            package_name = app_data.get('Name', '')
            display_name = app_data.get('DisplayName', package_name)
            package_full_name = app_data.get('PackageFullName', package_name)
            
            # Nettoyer le nom d'affichage
            clean_name = self.clean_app_name(display_name if display_name else package_name)
            if not clean_name:
                return
            
            # Créer la commande d'ouverture UWP
            uwp_command = f"shell:appsfolder\\{package_full_name}!App"
            
            self._add_application(clean_name, {
                "nom": display_name if display_name else clean_name,
                "chemin": uwp_command,
                "processus": package_name,
                "source": "uwp_store",
                "type": "uwp",
                "package_name": package_name
            })
            
        except Exception:
            pass
    
    def _add_application(self, clean_name, app_data):
        """Ajoute une application à la liste avec gestion des doublons"""
        key = clean_name.lower()
        
        # Si l'application existe déjà, prioriser certaines sources
        if key in self.applications:
            existing_source = self.applications[key].get("source", "")
            new_source = app_data.get("source", "")
            
            # Ordre de priorité des sources
            source_priority = {
                "location_connue": 5,
                "registre_app_paths": 4,
                "raccourci_menu": 3,
                "registre_uninstall": 2,
                "scan_dossier": 1,
                "path_system": 1,
                "uwp_store": 3
            }
            
            existing_priority = source_priority.get(existing_source, 0)
            new_priority = source_priority.get(new_source, 0)
            
            # Remplacer seulement si la nouvelle source est plus prioritaire
            if new_priority <= existing_priority:
                return
        
        # Valider que le chemin existe (sauf pour UWP)
        if app_data.get("type") != "uwp":
            if not os.path.exists(app_data["chemin"]):
                return
        
        # Ajouter les commandes vocales
        app_data["commandes"] = self._generate_voice_commands(clean_name)
        
        self.applications[key] = app_data
    
    def _generate_voice_commands(self, app_name):
        """Génère des commandes vocales intelligentes pour une application"""
        commands = set()
        name_lower = app_name.lower()
        
        # Nom complet
        commands.add(name_lower)
        
        # Mots individuels (plus de 2 caractères)
        words = re.findall(r'\b\w{3,}\b', name_lower)
        commands.update(words)
        
        # Acronymes pour noms composés
        if len(words) > 1:
            acronym = ''.join(word[0] for word in words)
            if len(acronym) >= 2:
                commands.add(acronym)
        
        # Noms alternatifs courants
        name_mappings = {
            'google chrome': ['chrome', 'navigateur google'],
            'mozilla firefox': ['firefox', 'navigateur mozilla'],
            'microsoft edge': ['edge', 'navigateur microsoft'],
            'vlc media player': ['vlc', 'lecteur video'],
            'visual studio code': ['vscode', 'vs code'],
            'notepad++': ['notepad plus plus', 'editeur texte'],
            'microsoft word': ['word', 'traitement texte'],
            'microsoft excel': ['excel', 'tableur'],
            'microsoft powerpoint': ['powerpoint', 'presentation']
        }
        
        for app_pattern, alternatives in name_mappings.items():
            if app_pattern in name_lower:
                commands.update(alternatives)
        
        return list(commands)
    
    def _is_valid_application(self, app_name):
        """Vérifie si un nom d'application est valide"""
        if not app_name or len(app_name) < 2:
            return False
        
        # Filtrer les applications système/utilitaires
        invalid_patterns = [
            'uninstall', 'setup', 'installer', 'updater', 'helper',
            'service', 'driver', 'runtime', 'redistributable',
            'microsoft visual c++', 'vcredist', '.net framework'
        ]
        
        app_lower = app_name.lower()
        return not any(pattern in app_lower for pattern in invalid_patterns)
    
    def clean_app_name(self, name):
        """Nettoie et normalise le nom d'une application"""
        if not name:
            return ""
        
        # Supprimer les éléments indésirables
        cleaned = re.sub(r'\s*\([^)]*\)', '', name)  # Parenthèses
        cleaned = re.sub(r'\s*\[[^\]]*\]', '', cleaned)  # Crochets
        cleaned = re.sub(r'\s+v?\d+(\.\d+)*(\.\d+)*', '', cleaned)  # Versions
        cleaned = re.sub(r'\s+(x64|x86|32-bit|64-bit|win32|win64)', '', cleaned, re.IGNORECASE)
        cleaned = re.sub(r'\s+(update|hotfix|patch)', '', cleaned, re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normaliser espaces
        
        # Cas spéciaux
        if 'google chrome' in cleaned.lower():
            return 'Google Chrome'
        elif 'mozilla firefox' in cleaned.lower():
            return 'Mozilla Firefox'
        elif 'microsoft edge' in cleaned.lower():
            return 'Microsoft Edge'
        
        return cleaned if self._is_valid_application(cleaned) else ""
    
    def run_full_scan(self):
        """Exécute un scan complet avec toutes les méthodes"""
        print("🚀 Démarrage du scan complet avancé...")
        
        for method in self.scan_methods:
            try:
                method()
            except Exception as e:
                print(f"⚠️ Erreur dans {method.__name__}: {e}")
        
        # Post-traitement: vérification et nettoyage
        self._post_process_applications()
        
        print(f"✅ Scan terminé ! {len(self.applications)} applications trouvées.")
        return self.applications
    
    def _post_process_applications(self):
        """Post-traitement des applications trouvées"""
        print("🔧 Post-traitement des applications...")
        
        # Supprimer les applications avec des chemins invalides
        to_remove = []
        for key, app_data in self.applications.items():
            if app_data.get("type") != "uwp":
                if not os.path.exists(app_data["chemin"]):
                    to_remove.append(key)
        
        for key in to_remove:
            del self.applications[key]
        
        print(f"🧹 {len(to_remove)} applications avec chemins invalides supprimées")
    
    def save_to_assistant_format(self, filename="applications_assistant.json"):
        """Sauvegarde directement au format assistant vocal"""
        assistant_apps = {}
        
        for key, app_data in self.applications.items():
            assistant_apps[key] = {
                "nom": app_data["nom"],
                "chemin": app_data["chemin"],
                "processus": app_data["processus"],
                "commandes": app_data["commandes"],
                "source": app_data["source"]
            }
        
        output_file = os.path.join(os.path.dirname(__file__), filename)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(assistant_apps, f, indent=2, ensure_ascii=False)
        
        print(f"💾 {len(assistant_apps)} applications sauvegardées dans: {output_file}")
        return output_file
    
    def print_scan_summary(self):
        """Affiche un résumé du scan"""
        print("\n" + "="*60)
        print("📋 RÉSUMÉ DU SCAN D'APPLICATIONS")
        print("="*60)
        
        # Statistiques par source
        sources = {}
        for app_data in self.applications.values():
            source = app_data.get("source", "inconnue")
            sources[source] = sources.get(source, 0) + 1
        
        print("\n📊 Applications par source:")
        for source, count in sorted(sources.items()):
            print(f"   • {source}: {count} applications")
        
        # Exemples d'applications trouvées
        print(f"\n🎯 Exemples d'applications trouvées ({min(10, len(self.applications))}):")
        for i, (key, app_data) in enumerate(list(self.applications.items())[:10]):
            commands_preview = ", ".join(app_data["commandes"][:3])
            if len(app_data["commandes"]) > 3:
                commands_preview += "..."
            print(f"   {i+1:2d}. {app_data['nom']}")
            print(f"       Commandes: {commands_preview}")
            print(f"       Chemin: {app_data['chemin'][:50]}...")
        
        print(f"\n✅ TOTAL: {len(self.applications)} applications prêtes pour l'assistant vocal")

def main():
    print("🔍 Scanner d'Applications Windows - Version Avancée")
    print("=" * 60)
    
    scanner = AdvancedApplicationScanner()
    
    # Exécuter le scan complet
    applications = scanner.run_full_scan()
    
    # Sauvegarder au format assistant
    output_file = scanner.save_to_assistant_format()
    
    # Afficher le résumé
    scanner.print_scan_summary()
    
    print(f"\n🎉 Scan terminé avec succès!")
    print(f"📁 Fichier généré: {output_file}")
    print(f"🤖 {len(applications)} applications prêtes pour l'assistant vocal")

if __name__ == "__main__":
    main()
