# 🤖 Aegis Bot - Système de Signalement Communautaire

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Aegis** est un bot Discord moderne pour la gestion de signalements communautaires avec un système de validation collaborative et une base de données centralisée.

## ✨ **Fonctionnalités**

### 🛡️ **Signalements Sécurisés**
- **Signalements anonymes** via `/agis`
- **8 catégories** de signalements (harcèlement, contenu inapproprié, etc.)
- **Validation sécurisée** des entrées utilisateur
- **Rate limiting** automatique

### 🌐 **Multilingue**
- **Français** et **Anglais** supportés
- **Traductions externalisées** en JSON
- **Configuration par serveur**

### 🔧 **Administration**
- **Configuration automatique** via `/setup`
- **Statistiques** détaillées via `/stats`
- **Vérification utilisateurs** via `/check`
- **Validation collaborative** via `/validate`
- **Nettoyage automatique** via `/purge`

### 🏗️ **Architecture Moderne**
- **Structure modulaire** (Cogs, Services, UI)
- **Tests automatisés** (31 tests)
- **Logging centralisé**
- **Configuration type-safe**

## 🚀 **Installation**

### **Prérequis**
- Python 3.11+
- Token Discord Bot
- (Optionnel) Base de données Supabase

### **Installation Rapide**

```bash
# Cloner le projet
git clone <repo_url>
cd aegis

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec votre token Discord

# Lancer le bot
python main.py
```

### **Configuration .env**

```env
# Configuration Discord (REQUIS)
DISCORD_TOKEN=your_discord_bot_token

# Configuration Supabase (OPTIONNEL)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_ENABLED=true

# Modes de développement
TEST_MODE_ENABLED=false
DEBUG_ENABLED=false
```

## 📋 **Utilisation**

### **Configuration Serveur**
1. **Inviter le bot** avec permissions Administrator
2. **Lancer** `/setup` pour configuration automatique
3. **Attribuer** le rôle "Validateur" aux modérateurs
4. **Tester** avec `/agis`

### **Commandes Utilisateurs**
- `/agis` - Créer un signalement anonyme
- `/categories` - Voir les catégories de signalement

### **Commandes Administration**
- `/setup` - Configuration du serveur
- `/stats` - Statistiques détaillées  
- `/check <utilisateur>` - Vérifier un utilisateur
- `/validate` - Interface de validation
- `/purge [jours]` - Nettoyer anciens signalements

### **Commandes Debug** *(mode développement)*
- `/debug-info` - Informations système
- `/debug-services` - État des services
- `/debug-translations <clé>` - Test traductions

## 🏗️ **Architecture**

```
aegis/
├── main.py                     # Point d'entrée
├── config/                     # Configuration centralisée
│   ├── bot_config.py          # Config principale
│   └── logging_config.py      # Configuration logging
├── core/                       # Cœur du bot
│   └── bot.py                 # Classe principale
├── cogs/                       # Commandes Discord
│   ├── reports.py             # Signalements
│   ├── admin.py               # Administration
│   ├── setup.py               # Configuration
│   └── debug.py               # Debug
├── ui/                         # Interface utilisateur
│   ├── views/                 # Vues Discord
│   └── modals/                # Modals Discord
├── services/                   # Logique métier
│   ├── report_service.py      # Service signalements
│   └── guild_service.py       # Service serveurs
├── utils/                      # Utilitaires
│   ├── security.py            # Validation sécurisée
│   └── rate_limiter.py        # Limitation taux
├── locales/                    # Traductions
│   ├── fr.json                # Français
│   ├── en.json                # Anglais
│   └── translation_manager.py # Gestionnaire
├── database/                   # Base de données
│   ├── models/                # Modèles de données
│   └── supabase_client.py     # Client Supabase
└── tests/                      # Tests automatisés
```

## 🧪 **Tests**

```bash
# Lancer tous les tests
python scripts/run_tests.py

# Tests spécifiques
python -m pytest tests/test_simple.py -v

# Avec couverture
python scripts/run_tests.py -c
```

**Résultats actuels :** ✅ 31 tests passent

## 📊 **Statistiques Projet**

- **~6,000 lignes** de code bien organisées
- **40+ fichiers** modulaires (< 200 lignes chacun)
- **4 cogs** Discord
- **6 services** métier
- **2 langues** supportées
- **31 tests** automatisés

## 🛠️ **Développement**

### **Ajouter une Nouvelle Langue**

```bash
# 1. Créer le fichier de traduction
cp locales/fr.json locales/es.json

# 2. Traduire les clés dans es.json
# 3. Le gestionnaire de traductions l'utilisera automatiquement
```

### **Ajouter une Nouvelle Commande**

```python
# Dans cogs/reports.py ou autre cog
@app_commands.command(name="ma_commande", description="Description")
async def ma_commande(self, interaction: discord.Interaction):
    await interaction.response.send_message("Hello !", ephemeral=True)
```

### **Ajouter un Nouveau Service**

```python
# Dans services/mon_service.py
class MonService:
    def __init__(self):
        self.logger = get_logger('mon_service')
    
    def ma_methode(self):
        return "Résultat"

# Dans core/bot.py, dans setup()
self.mon_service = MonService()
```

## 📚 **Documentation**

- **[Rapport de Refactorisation](docs/reports/REFACTORING_REPORT.md)** - Détails de l'architecture
- **[Rapport de Tests](docs/reports/TESTS_REPORT.md)** - Résultats des tests

## 🔒 **Sécurité**

- ✅ **Validation** de toutes les entrées utilisateur
- ✅ **Rate limiting** automatique 
- ✅ **Sanitisation** des contenus Discord
- ✅ **Permissions** vérifiées pour chaque commande
- ✅ **Logs d'audit** pour traçabilité

## 🤝 **Contribution**

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/ma-feature`)
3. Commit les changements (`git commit -am 'Add ma feature'`)
4. Pousser la branche (`git push origin feature/ma-feature`)
5. Créer une Pull Request

## 📝 **License**

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 **Support**

Pour toute question ou problème :
- **Issues GitHub** : Créer une issue
- **Documentation** : Consulter `/docs`
- **Logs** : Vérifier `aegis_bot.log`

---

**Développé avec ❤️ pour la communauté Discord**