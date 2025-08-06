# 🧪 Système de Tests Automatisés - Aegis Bot

## 📋 Vue d'ensemble

Cette suite de tests automatisés permet de vérifier que toutes les fonctionnalités du bot Aegis fonctionnent correctment sans avoir besoin d'une connexion Discord réelle. Le système utilise des mocks personnalisés pour simuler toutes les interactions.

## 🏗️ Structure des tests

```
tests/
├── __init__.py                     # Package tests
├── conftest.py                     # Configuration pytest et fixtures partagées
├── discord_mocks.py                # Mocks personnalisés pour Discord API
├── test_simple.py                  # Tests de base pour vérifier le fonctionnement
├── test_all_commands.py            # Tests complets de toutes les commandes slash
├── test_all_ui_components.py       # Tests de tous les composants UI (modals, boutons)
├── test_commands.py                # Tests simples des commandes (legacy)
├── test_ui_interactions.py         # Tests d'interactions UI (legacy)
├── test_utils.py                   # Tests des utilitaires et sécurité
├── test_integration.py             # Tests d'intégration avec mocks
└── README.md                       # Cette documentation
```

## 🚀 Lancement des tests

### 🖥️ Windows (Recommandé)
```bash
# Mode interactif (recommandé pour choisir le type de tests)
run_tests.bat

# Avec couverture de code
run_tests.bat -c

# Mode verbose avec détails
run_tests.bat -v

# Test spécifique
run_tests.bat -s tests/test_simple.py
```

### 🐍 Python (Multiplateforme)
```bash
# Mode interactif avec menu
python run_tests.py

# Tests rapides (commandes essentielles)
python run_tests.py -s tests/test_all_commands.py -v

# Tous les tests avec couverture HTML
python run_tests.py -c -html

# Test spécifique d'une classe
python run_tests.py -s "tests/test_all_commands.py::TestAgisCommand" -v
```

### ⚡ Commandes pytest directes

```bash
# Tests rapides (unitaires seulement)
python -m pytest tests/ -v -m "not integration and not slow"

# Tests complets
python -m pytest tests/ -v

# Tests avec couverture de code
python -m pytest tests/ -v --cov=. --cov-report=html

# Test d'un fichier spécifique
python -m pytest tests/test_commands.py -v

# Tests en mode verbose avec détails
python -m pytest tests/ -vvv -s
```

## 📁 Détail des fichiers de test

### `test_commands.py` - Tests des commandes slash

**Commandes testées:**
- `/agis` - Interface de signalement
  - ✅ Serveur non configuré
  - ✅ Serveur configuré avec forum et rôle
- `/check` - Vérification utilisateur
  - ✅ Sans permissions
  - ✅ Avec Supabase désactivé
  - ✅ Utilisateur non flagué
- `/validate` - Validation de signalements
  - ✅ Sans rôle validateur
  - ✅ Avec rôle validateur
- `/categories` - Affichage des catégories
- `/anonymiser` - Gestion d'anonymat
  - ✅ Sans permissions
  - ✅ Sans signalements actifs

### `test_ui_interactions.py` - Tests des interactions

**Composants testés:**
- `CategorySelectView` - Sélecteur de catégorie
- `ProofSelectView` - Sélecteur de preuves
- `AgisReportModal` - Modal de signalement
  - ✅ Username invalide
  - ✅ Rate limiting
- `ValidationView` - Boutons de validation
  - ✅ Sans rôle validateur
  - ✅ Signalement déjà finalisé
  - ✅ Validation/rejet avec succès
- `LanguageButtonView` - Boutons de langue
  - ✅ Changement vers français
  - ✅ Changement vers anglais

### `test_utils.py` - Tests des utilitaires

**Systèmes testés:**
- `SecurityValidator` - Validation et sanitisation
  - ✅ Texte normal, vide, trop long
  - ✅ Tentatives d'injection (XSS, scripts)
  - ✅ Sanitisation HTML
- `RateLimiter` - Limitation de taux
  - ✅ Première requête autorisée
  - ✅ Requêtes multiples dans la limite
  - ✅ Dépassement de limite
  - ✅ Utilisateurs séparés
- `ReportTracker` - Détection de doublons
  - ✅ Premier signalement
  - ✅ Détection de doublon
  - ✅ Utilisateurs différents
- `AuditLogger` - Journalisation
- `validate_username` - Validation des noms d'utilisateur
  - ✅ Noms normaux, avec caractères spéciaux, Unicode
  - ✅ Caractères interdits (contrôle)
- `create_secure_embed` - Création d'embeds sécurisés

### `test_integration.py` - Tests d'intégration

**Intégrations testées:**
- **Supabase** (avec mocks)
  - ✅ Connexion réussie/échouée
  - ✅ Vérification utilisateur flagué/non flagué
  - ✅ Ajout de signalement validé
  - ✅ Récupération des statistiques
- **Configuration des guildes**
  - ✅ Guildes inexistantes/nouvelles/existantes
  - ✅ Liste des guildes configurées
- **Flux complets**
  - ✅ Signalement de bout en bout
  - ✅ Validation avec centralisation
- **Gestion d'erreurs**
  - ✅ Erreurs de connexion Supabase
  - ✅ Exceptions dans les modals

## 🎭 Système de mocks

### Fixtures disponibles (`conftest.py`)

- `mock_guild` - Guilde Discord mockée
- `mock_user` - Utilisateur Discord mocké  
- `mock_channel` - Canal Discord mocké
- `mock_interaction` - Interaction Discord mockée
- `mock_bot` - Bot Discord mocké
- `mock_supabase_client` - Client Supabase mocké
- `mock_validator_role` - Rôle validateur mocké
- `mock_alerts_forum` - Forum d'alertes mocké
- `configured_guild` - Guilde entièrement configurée
- `clean_guild_config` - Nettoyage config après tests

### Mocks Supabase

Le client Supabase est entièrement mocké pour les tests :

```python
mock_supabase_client.is_connected = True
mock_supabase_client.check_user_flag.return_value = None  # Pas flagué
mock_supabase_client.add_validated_report.return_value = True  # Succès
```

## 🏷️ Marqueurs de tests

```bash
# Tests rapides seulement
pytest -m "not integration and not slow"

# Tests d'intégration seulement  
pytest -m integration

# Tests unitaires seulement
pytest -m unit

# Tests Discord seulement
pytest -m discord
```

## 📊 Couverture de code

Pour générer un rapport de couverture :

```bash
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

Le rapport HTML sera généré dans `htmlcov/index.html`.

## 🐛 Débogage des tests

### Tests qui échouent

1. **Vérifiez les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

2. **Mode verbose** pour plus de détails :
   ```bash
   python -m pytest tests/ -vvv -s
   ```

3. **Test d'un seul fichier** :
   ```bash
   python -m pytest tests/test_commands.py::TestAgisCommand::test_agis_command_configured -vvv -s
   ```

### Erreurs communes

- **Import errors** : Vérifiez que le bot n'est pas en cours d'exécution
- **Mock errors** : Vérifiez que les fixtures sont bien importées
- **Async errors** : Vérifiez la configuration `pytest-asyncio`

## 🎯 Bonnes pratiques

### Écriture de nouveaux tests

1. **Utilisez les fixtures** existantes dans `conftest.py`
2. **Nommage** : `test_function_name_scenario`
3. **Markers** : Ajoutez `@pytest.mark.asyncio` pour les tests async
4. **Assertions** : Utilisez des assertions descriptives
5. **Mocks** : Mockez tous les services externes

### Structure d'un test

```python
@pytest.mark.asyncio
async def test_command_scenario(self, mock_interaction, configured_guild):
    """Test description"""
    # Arrange
    mock_interaction.guild = configured_guild
    
    # Act
    await command_function(mock_interaction)
    
    # Assert
    mock_interaction.response.send_message.assert_called_once()
    # Vérifications supplémentaires...
```

## 🔄 CI/CD et automatisation

Ces tests sont conçus pour être intégrés dans un pipeline CI/CD :

```yaml
# Exemple GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    python -m pytest tests/ -v --cov=. --cov-report=xml
```

## 📈 Métriques de tests

**Objectifs de couverture :**
- Code coverage : > 80%
- Tests par commande : ≥ 3 scénarios
- Tests par composant UI : ≥ 2 scénarios
- Tests d'intégration : 1 par flux principal

**Temps d'exécution cibles :**
- Tests unitaires : < 30 secondes
- Tests complets : < 2 minutes
- Tests avec couverture : < 3 minutes