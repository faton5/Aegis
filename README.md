# 🛡️ Aegis Bot - Système de Signalement Anti-Abus Anonyme

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Enabled-green.svg)](https://supabase.com)
[![Security](https://img.shields.io/badge/Security-HMAC%20SHA256-red.svg)]()
[![Tests](https://img.shields.io/badge/Tests-4%2F4%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Aegis** est un bot Discord moderne de nouvelle génération pour la gestion sécurisée de signalements communautaires avec **anonymat cryptographique complet**, système anti-abus sophistiqué et base de données centralisée.

## ✨ **Fonctionnalités Principales**

### 🔐 **Anonymat Cryptographique Total**
- **Hash HMAC-SHA256** non-réversible des reporters
- **Aucun stockage** d'identifiants de reporters en base
- **Salt secret** configurable pour sécurité maximale
- **Protection** contre l'analyse de patterns

### 🛡️ **Système Anti-Abus Avancé**
- **Détection de doublons** automatique et fiable
- **Prévention** des signalements en masse par même utilisateur
- **Rate limiting** intelligent avec cache mémoire
- **Validation** des entrées utilisateur renforcée

### 📊 **Signalements Intelligents**
- **Interface moderne** via `/agis` avec sélection visuelle
- **8 catégories** spécialisées (harcèlement, contenu inapproprié, etc.)
- **Validation collaborative** par modérateurs
- **Audit transparent** sans fuite d'identité

### 🌐 **Système Multilingue Avancé**
- **Français** et **Anglais** supportés nativement
- **Traductions externalisées** en JSON modifiables
- **Détection automatique** de langue par serveur
- **Configuration flexible** par communauté

### 🔧 **Administration Professionnelle**
- **Configuration automatique** via `/setup` avec création de canaux
- **Statistiques avancées** via `/stats` avec métriques Supabase
- **Vérification utilisateurs** via `/check` avec historique flags
- **Interface validation** via `/validate` avec audit trail
- **Nettoyage automatique** via `/purge` avec expiration 6 mois
- **Logs d'audit** transparents sans exposition d'identités

### 🏗️ **Architecture Enterprise**
- **Structure modulaire** avancée (Cogs, Services, UI, Utils)
- **Tests automatisés** complets avec mocks Discord
- **Base de données Supabase** avec sécurité RLS
- **Logging centralisé** avec rotation automatique
- **Configuration type-safe** avec validation
- **Services cryptographiques** sécurisés
- **Gestion d'erreurs** robuste

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

# Configuration Supabase (RECOMMANDÉ)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_ENABLED=true

# Sécurité Anti-Abus (CRITIQUE)
REPORTER_SALT_SECRET=your_64_character_hex_secret

# Modes de développement
TEST_MODE_ENABLED=false
DEBUG_ENABLED=false
LOG_LEVEL=INFO
```

> ⚠️ **IMPORTANT**: Le `REPORTER_SALT_SECRET` est critique pour l'anonymat. Générez-le avec `python -c "import secrets; print(secrets.token_hex(32))"`

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
├── 📄 main.py                  # Point d'entrée principal
├── ⚙️ config/                  # Configuration centralisée
│   ├── bot_config.py          # Config principale type-safe
│   └── logging_config.py      # Logging avec rotation
├── 🤖 core/                    # Cœur du bot
│   └── bot.py                 # Classe AegisBot principale
├── 🧩 cogs/                    # Commandes Discord (6 cogs)
│   ├── reports.py             # Signalements (/agis, /categories)
│   ├── admin.py               # Administration (/stats, /check, /validate, /purge)
│   ├── setup.py               # Configuration (/setup)
│   ├── debug.py               # Debug (/debug-*)
│   ├── dm_handler.py          # Gestion messages privés
│   └── config.py              # Configuration serveur
├── 🎨 ui/                      # Interface utilisateur moderne
│   ├── views/                 # Vues avec boutons interactifs
│   └── modals/                # Modals de saisie élégants
├── 🛠️ services/                # Logique métier découplée
│   ├── report_service.py      # Service signalements avec anti-abus
│   └── guild_service.py       # Service serveurs (JSON individuels)
├── 🔧 utils/                   # Utilitaires Sécurisés
│   ├── security.py            # Validation renforcée
│   ├── rate_limiter.py        # Rate limiting intelligent
│   ├── anonymous_hasher.py    # Hash HMAC-SHA256 anonyme
│   └── audit_logger.py        # Audit transparent JSONL
├── 🌍 locales/                 # Système multilingue
│   ├── fr.json + en.json      # Traductions externalisées
│   └── translation_manager.py # Gestionnaire auto-détection
├── 🗃️ database/                # Base de données sécurisée
│   ├── models/                # Modèles avec hash anonymes  
│   ├── supabase_client.py     # Client avancé flags multi-niveaux
│   └── *.sql                  # Schémas sécurisés (RLS + functions)
├── 📜 scripts/                 # Scripts utilitaires organisés
│   ├── tests/                 # Tests système anti-abus
│   └── database/              # Scripts maintenance BDD
├── 🧪 tests/                   # Tests automatisés complets
└── 📚 docs/                    # Documentation professionnelle
    ├── website/               # Site web complet
    ├── deployment/            # Guides production
    └── development/           # Docs techniques
```

## 🧪 **Tests**

```bash
# Lancer tous les tests
python scripts/run_tests.py

# Tests spécifiques
python -m pytest tests/test_simple.py -v

# Avec couverture
python scripts/run_tests.py -c

# Test système anti-abus
python scripts/tests/test_anti_abuse_simple.py
```

**Résultats actuels :** ✅ Tests système complet + ✅ 4/4 tests anti-abus cryptographique passent

## 📊 **Statistiques Projet**

- **~8,000+ lignes** de code professionnel bien organisées
- **50+ fichiers** modulaires avec séparation claire
- **6 cogs** Discord (Reports, Admin, Setup, Debug, DM Handler, Config)
- **8+ services** métier spécialisés
- **4 utilitaires** sécurisés (Security, Rate Limiter, Hasher, Audit)
- **2 langues** supportées (extensible)
- **Tests complets** avec validation cryptographique
- **Base de données** sécurisée avec RLS et fonctions optimisées

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

### 🌐 **Site Web** 
- **[Documentation Site Complète](docs/website/DOCUMENTATION_SITE.md)** - Tout pour créer un site professionnel

### 🚀 **Déploiement**
- **[Guide Anti-Abus Production](docs/deployment/DEPLOIEMENT_ANTI_ABUS.md)** - Déploiement sécurisé complet

### 🔧 **Développement**  
- **[Documentation Technique](docs/development/TECHNICAL_DOCUMENTATION.md)** - Architecture détaillée
- **[Rapport Refactorisation](docs/development/REFACTORING_REPORT.md)** - Évolution du code
- **[Rapport Tests](docs/development/TESTS_REPORT.md)** - Résultats tests automatisés

### 📋 **Navigation Documentation**
👉 **[docs/README.md](docs/README.md)** - Index complet de toute la documentation

## 🔒 **Sécurité Enterprise**

### **Anonymat Cryptographique**
- ✅ **HMAC-SHA256** avec salt secret pour hash reporters
- ✅ **Aucun stockage** d'identifiants personnels en base
- ✅ **Non-réversibilité** cryptographiquement garantie
- ✅ **Protection** contre attaques par analyse de patterns

### **Sécurité Opérationnelle**
- ✅ **Validation stricte** de toutes entrées utilisateur
- ✅ **Rate limiting** intelligent avec cache mémoire
- ✅ **Sanitisation** complète des contenus Discord
- ✅ **Permissions** vérifiées à chaque commande
- ✅ **Audit transparent** sans fuite d'identité
- ✅ **Base de données** sécurisée (RLS, search_path, SECURITY DEFINER)
- ✅ **Expiration automatique** des flags (6 mois)

## 🤝 **Contribution**

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/ma-feature`)
3. Commit les changements (`git commit -am 'Add ma feature'`)
4. Pousser la branche (`git push origin feature/ma-feature`)
5. Créer une Pull Request

## 📝 **License**

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🚀 **Déploiement Production**

### **Prérequis Sécurisés**
1. **Générer salt secret** : `python -c "import secrets; print(secrets.token_hex(32))"`
2. **Configurer Supabase** avec les schémas SQL fournis
3. **Vérifier permissions** Discord avec scope `applications.commands`
4. **Tester système** : `python test_anti_abuse_simple.py`

### **Métriques de Santé**
- ✅ **Aucun doublon** créé (même reporter/serveur/cible)
- ✅ **Anonymat préservé** (hash non-réversibles)
- ✅ **Audit complet** sans fuite d'identité
- ✅ **Performance maintenue** (cache hit rate > 90%)

## 🆘 **Support**

Pour toute question ou problème :
- **Issues GitHub** : Créer une issue détaillée
- **Documentation** : Consulter `/docs` et `DEPLOIEMENT_ANTI_ABUS.md`
- **Logs système** : Vérifier `aegis_bot.log`
- **Tests sécurité** : Lancer `test_anti_abuse_simple.py`

---

**🛡️ Développé avec sécurité maximale pour protéger les communautés Discord**

> **Note**: Ce système garantit un **anonymat cryptographique complet** tout en maintenant une **protection anti-abus efficace**. Testé et validé pour usage en production.