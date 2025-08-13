# CLAUDE.md

Ce fichier fournit des conseils à Claude Code (claude.ai/code) lors du travail sur le code de ce dépôt.

## Commandes de Développement

### Lancement du Bot
```bash
# Point d'entrée principal
python main.py

# Alternative (legacy, si main.py n'existe pas)
python bot.py
```

### Tests Automatisés
```bash
# Script principal de tests (recommandé)
python scripts/run_tests.py

# Mode interactif pour choisir les tests
python scripts/run_tests.py -i

# Avec couverture de code
python scripts/run_tests.py -c

# Test spécifique
python scripts/run_tests.py -s tests/test_simple.py

# Tests de base seulement (rapide)
python -m pytest tests/test_simple.py tests/test_utils.py -v

# Sur Windows avec script batch
scripts/run_tests.bat
```

### Installation et Configuration
```bash
# Installer les dépendances
pip install -r requirements.txt

# Configuration initiale
cp .env.example .env
# Éditer .env avec DISCORD_TOKEN
```

## Architecture du Bot

### Structure Modulaire
Le bot utilise une architecture par couches avec séparation claire des responsabilités :

**Core (`core/`)** : Classe principale AegisBot héritant de `commands.Bot` avec gestion centralisée des services
- `core/bot.py:44` : Méthode `setup()` initialise tous les services et charge les cogs
- `core/bot.py:92` : `_load_cogs()` charge dynamiquement les extensions

**Cogs (`cogs/`)** : Extensions Discord avec commandes slash
- `cogs/reports.py` : Commandes `/agis`, `/categories` 
- `cogs/admin.py` : Commandes `/stats`, `/check`, `/validate`, `/purge`
- `cogs/setup.py` : Commande `/setup` pour configuration serveur
- `cogs/debug.py` : Commandes debug (chargé seulement si `DEBUG_ENABLED=true`)

**Services (`services/`)** : Logique métier découplée
- `services/report_service.py` : Gestion des signalements avec validation et rate limiting
- `services/guild_service.py` : Configuration par serveur (fichiers JSON individuels)

**UI (`ui/`)** : Composants d'interface Discord
- `ui/modals/` : Modals de saisie utilisateur
- `ui/views/` : Views avec boutons et interactions

### Base de Données Supabase (Optionnelle)
- **Configuration** : `SUPABASE_ENABLED=true` dans `.env` pour activer
- **Client** : `database/supabase_client.py` avec système de flags multi-niveaux
- **Intégration** : Injectée dans ReportService via `core/bot.py:58-75`
- **Migration** : Schéma dans `database/supabase_schema.sql`

### Configuration Type-Safe
- **Centralisée** : `config/bot_config.py` avec classe `BotSettings` et dataclass
- **Variables d'environnement** : Auto-chargement avec `dotenv` dans `BotSettings.__post_init__()`
- **Catégories** : Dictionnaire `REPORT_CATEGORIES` avec sévérité et labels

### Internationalisation
- **Système** : `locales/translation_manager.py` avec classe `TranslationManager` singleton
- **Langues** : `locales/fr.json` et `locales/en.json` 
- **Utilisation** : `translator.t(key, guild_id, **kwargs)` détecte automatiquement la langue du serveur

### Sécurité et Validation
- **Validation** : `utils/security.py` classe `SecurityValidator` 
- **Rate Limiting** : `utils/rate_limiter.py` classe `RateLimiter`
- **Intégration** : Services injectés dans ReportService via constructeur

## Patterns de Développement

### Tests
- **Framework** : pytest avec pytest-asyncio pour code Discord
- **Mocks** : `tests/discord_mocks.py` simule objets Discord
- **Organisation** : Tests isolés par composant (commands, ui, utils, etc.)
- **Coverage** : pytest-cov pour mesurer couverture de code

### Logging
- **Configuration** : `config/logging_config.py` avec rotation automatique
- **Usage** : `logger = get_logger('module_name')` dans chaque module
- **Niveau** : Configurable via `LOG_LEVEL` dans `.env`

### Gestion d'Erreurs
- **Commandes Slash** : `core/bot.py:148` gestionnaire global dans `on_app_command_error`
- **Async** : Gestion propre des erreurs asynchrones avec logging détaillé
- **Ressources** : Nettoyage automatique dans `bot.close()`

### Configuration par Serveur
- **Format** : Fichiers JSON individuels dans `guild_configs/`
- **Migration** : Auto-migration depuis l'ancien fichier unique `guild_configs.json`
- **Validation** : Validation automatique avec valeurs par défaut

## Variables d'Environnement Importantes

```bash
# Obligatoire
DISCORD_TOKEN=your_bot_token

# Base de données (optionnel)
SUPABASE_ENABLED=true
SUPABASE_URL=your_supabase_url  
SUPABASE_KEY=your_supabase_key

# Développement
TEST_MODE_ENABLED=false  # Commandes debug
DEBUG_ENABLED=false      # Logs détaillés et cog debug
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
```

## Conseils de Développement

### Nouveau Cog
1. Créer fichier dans `cogs/`
2. Hériter de `commands.Cog`
3. Ajouter à la liste `cogs_to_load` dans `core/bot.py:94`

### Nouvelle Commande
Utiliser les app_commands pour slash commands :
```python
@app_commands.command(name="ma_commande")
async def ma_commande(self, interaction: discord.Interaction):
    await interaction.response.send_message("Réponse", ephemeral=True)
```

### Nouveau Service
1. Créer dans `services/`
2. Initialiser dans `core/bot.py:setup()`
3. Injecter via constructeur pour testabilité

### Tests
- **Toujours** tester les nouvelles fonctionnalités
- Utiliser les mocks Discord existants
- Lancer `python scripts/run_tests.py -c` avant commit

### Python Path
Le projet ajoute automatiquement sa racine au PYTHONPATH dans `main.py:11-12` pour les imports relatifs.