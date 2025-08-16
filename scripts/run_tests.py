#!/usr/bin/env python3
"""
Script de lancement des tests automatisés pour Aegis Bot
Lance tous les tests avec couverture de code et rapport détaillé
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description, capture_output=False):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    print(f"Commande: {' '.join(command)}")
    print("-" * 50)
    
    try:
        if capture_output:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        else:
            result = subprocess.run(command, check=False)
            
        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
        else:
            print(f"❌ {description} - ÉCHEC (code: {result.returncode})")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False


def check_dependencies():
    """Vérifie que les dépendances de test sont installées"""
    print("[CHECK] Verification des dependances...")
    
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-mock",
        "pytest-cov"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"[OK] {package} - installe")
        except ImportError:
            print(f"[ERROR] {package} - MANQUANT")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[WARNING] Packages manquants: {', '.join(missing_packages)}")
        print("[INFO] Pour installer les dependances manquantes:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Lance les tests avec différentes options"""
    parser = argparse.ArgumentParser(description="Lance les tests Aegis Bot")
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Lance les tests avec couverture de code"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Mode verbose pour plus de détails"
    )
    parser.add_argument(
        "--specific", "-s",
        type=str,
        help="Lance un test spécifique (ex: tests/test_all_commands.py::TestAgisCommand)"
    )
    parser.add_argument(
        "--html-report", "-html",
        action="store_true",
        help="Génère un rapport HTML de couverture"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Mode interactif pour choisir les tests"
    )
    
    args = parser.parse_args()
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("bot.py").exists():
        print("[ERROR] Ce script doit etre lance depuis le repertoire racine du bot.")
        print("   Repertoire actuel:", os.getcwd())
        sys.exit(1)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n[ERROR] Dependances manquantes. Installation requise.")
        sys.exit(1)
    
    print("AEGIS BOT - Systeme de Tests Automatises")
    print("=" * 50)
    print()
    
    # Mode interactif
    if args.interactive or len(sys.argv) == 1:
        return interactive_mode()
    
    # Mode ligne de commande
    return command_line_mode(args)


def interactive_mode():
    """Mode interactif pour choisir les tests"""
    test_options = {
        "1": {
            "name": "Tests de base (simples et rapides)",
            "command": [sys.executable, "-m", "pytest", "tests/test_simple.py", "-v"]
        },
        "2": {
            "name": "Tests des utilitaires de sécurité",
            "command": [sys.executable, "-m", "pytest", "tests/test_utils.py", "-v"]
        },
        "3": {
            "name": "Tests fonctionnels (base + utilitaires)",
            "command": [sys.executable, "-m", "pytest", "tests/test_simple.py", "tests/test_utils.py", "-v"]
        },
        "4": {
            "name": "Tests avec couverture de code (fonctionnels seulement)",
            "command": [sys.executable, "-m", "pytest", "tests/test_simple.py", "tests/test_utils.py", "--cov=.", "--cov-report=term-missing", "-v"]
        },
        "5": {
            "name": "Test spécifique (à choisir ensuite)",
            "command": None  # Sera défini après choix
        }
    }
    
    print("[MENU] Choisissez le type de tests a executer:")
    for key, option in test_options.items():
        print(f"  {key}. {option['name']}")
    print("  0. Quitter")
    
    choice = input("\nVotre choix (0-5): ").strip()
    
    if choice == "0":
        print("[EXIT] A bientot!")
        return 0
    
    if choice not in test_options:
        print("[ERROR] Choix invalide.")
        return 1
    
    # Cas spécial pour les tests spécifiques
    if choice == "5":
        print("\n[INFO] Tests disponibles:")
        print("  - tests/test_simple.py (6 tests de base)")
        print("  - tests/test_utils.py (13 tests utilitaires)")
        
        specific_choice = input("\nEntrez le nom du fichier à tester: ").strip()
        if not specific_choice.startswith("tests/"):
            specific_choice = f"tests/{specific_choice}"
        
        command = [sys.executable, "-m", "pytest", specific_choice, "-v"]
        print(f"\n[RUN] Lancement: Test spécifique - {specific_choice}")
        success = run_command(command, "Exécution du test spécifique")
        return show_results(success, False)
    
    selected_option = test_options[choice]
    print(f"\n[RUN] Lancement: {selected_option['name']}")
    success = run_command(selected_option["command"], "Exécution des tests")
    
    return show_results(success, choice == "4")


def command_line_mode(args):
    """Mode ligne de commande avec arguments"""
    # Construire la commande pytest
    cmd = [sys.executable, "-m", "pytest"]
    
    if args.specific:
        cmd.append(args.specific)
        print(f"[TARGET] Test specifique: {args.specific}")
    else:
        cmd.extend(["tests/", "--tb=short"])
        print("[INFO] Lancement de tous les tests...")
    
    if args.verbose:
        cmd.append("-v")
        print("[INFO] Mode verbose active")
    
    if args.coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=term-missing"
        ])
        print("[INFO] Couverture de code activee")
        
        if args.html_report:
            cmd.append("--cov-report=html:htmlcov")
            print("[INFO] Rapport HTML active (dossier htmlcov/)")
    
    print()
    print("[RUN] Commande executee:", " ".join(cmd))
    print("-" * 50)
    print()
    
    # Lancer les tests
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return show_results(result.returncode == 0, args.coverage and args.html_report)
        
    except KeyboardInterrupt:
        print("\n[STOP] Tests interrompus par l'utilisateur.")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Erreur lors du lancement des tests: {e}")
        return 1


def show_results(success, has_html_report):
    """Affiche les résultats finaux"""
    print()
    print("-" * 50)
    
    if success:
        print("[SUCCESS] TOUS LES TESTS ONT REUSSI!")
        print("[INFO] Le bot Aegis fonctionne correctement.")
        if has_html_report:
            print("[INFO] Rapport HTML disponible dans: htmlcov/index.html")
    else:
        print("[ERROR] CERTAINS TESTS ONT ECHOUE")
        print("[INFO] Verifiez les messages d'erreur ci-dessus.")
        print("[TIPS] Conseils de debogage:")
        print("   - Relancez avec -v pour plus de details")
        print("   - Verifiez les variables d'environnement (.env)")
        print("   - Testez un module specifique avec -s")
    
    print("\n[DOCS] Documentation des tests:")
    print("   - Configuration: pytest.ini")
    print("   - Fixtures: tests/conftest.py")
    print("   - Mocks Discord: tests/discord_mocks.py")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())