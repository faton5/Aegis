# 🛡️ Bot Discord Aegis - Documentation complète

## 📋 Vue d'ensemble

**Aegis** est un bot Discord de signalement défensif conçu pour la protection communautaire, l'éducation et la veille sécuritaire. Il permet aux utilisateurs de signaler anonymement des comportements à risque et offre un système de validation par la communauté.

## 🎯 Objectifs du projet

### 🛡️ **Protection communautaire**
- Signalement anonyme de comportements dangereux
- Base de données centralisée des utilisateurs à risque
- Partage d'informations entre serveurs Discord

### 📚 **Éducation et prévention**
- Sensibilisation aux risques en ligne
- Formation des modérateurs
- Documentation des types de menaces

### 👥 **Collaboration inter-serveurs**
- Réseau de serveurs partenaires
- Validation communautaire des signalements
- Partage sécurisé d'informations

## ⚙️ Fonctionnalités principales

### 🔔 **Système de signalement**

#### `/agis` - Signalement anonyme
1. **Sélection de catégorie** via menu déroulant :
   - 🚨 Harcèlement
   - 🔞 Contenu inapproprié  
   - 👁️ Comportement suspect
   - 🛡️ Sécurité des mineurs
   - 📢 Spam
   - 💰 Arnaque
   - ⚔️ Menaces
   - ❓ Autre

2. **Sélection "Avez-vous des preuves ?"** :
   - ✅ Oui (avec preuves)
   - ❌ Non (sans preuve directe)

3. **Modal de saisie** :
   - Nom d'utilisateur à signaler
   - Motif détaillé du signalement
   - Liens et preuves supplémentaires (optionnel)

4. **Collecte de preuves par DM** :
   - DM automatique après signalement
   - Transfert anonyme des preuves vers le thread
   - Support texte, images, fichiers (max 8MB)
   - Expiration automatique après 24h

### 🔍 **Système de validation**

#### Validation par quorum communautaire
- **Rôle requis** : `@Validateur`
- **Seuil par défaut** : 80% des validateurs
- **Délai** : 48h pour valider
- **Actions** : ✅ Valider ou ❌ Rejeter

#### Centralisation automatique
- Signalements validés → Base Supabase
- Partage entre serveurs partenaires
- Niveaux de risque : `critical`, `high`, `medium`

#### ⚔️ Actions automatiques (FONCTIONNEL)
**Système de protection automatique basé sur les niveaux de risque :**

- **Critical** 🚫 : Ban automatique + alerte admins
- **High** 👢 : Kick automatique + surveillance renforcée  
- **Medium** ⚠️ : Alerte uniquement + monitoring
- **Low** ℹ️ : Log silencieux

**Configuration via `/setup` → Actions automatiques :**
- Seuils personnalisables par serveur
- Validation requise (minimum 2 serveurs par défaut)
- Logs complets des actions exécutées
- Interface de gestion avancée

**Vérification automatique nouveaux membres :**
- Scan automatique contre la base centralisée
- Actions préventives selon le niveau de risque
- Notifications aux modérateurs

### 👑 **Commandes administrateur**

#### `/setup` - Configuration initiale
- Crée le forum `#agis-alerts`
- Crée le rôle `@Validateur`
- Configure les permissions
- Mode avancé avec interface interactive

#### `/export` - Export de données
- Format JSON ou CSV
- Filtrage par période/catégorie
- Données anonymisées

#### `/purge` - Nettoyage
- Suppression des anciens signalements
- Respect des délais RGPD
- Logs de traçabilité

### 🔧 **Commandes de modération**

#### `/validate` - Validation manuelle
- Interface pour valider/rejeter
- Historique des actions
- Statistiques de validation

#### `/check` - Vérification utilisateur
- Recherche dans la base centralisée
- Historique des signalements
- Niveau de risque

### 📊 **Commandes d'information**

#### `/categories` - Liste des catégories
- Affichage des types de signalement
- Descriptions détaillées
- Exemples d'utilisation

#### `/stats` - Statistiques
- Nombre de signalements par période
- Taux de validation
- Activité des validateurs

### 🛠️ **Commandes de debug**

#### `/debug` - Diagnostics système
- État général du bot
- Connexion Supabase
- Structure du serveur
- Permissions

#### `/test-supabase` - Test base de données
- Vérification connexion
- Test des fonctions SQL
- Statistiques serveur

## 🏗️ Architecture technique

### 🧱 **Composants principaux**

#### **Client Discord**
- Intents : `guilds`, `members`, `message_content`, `dm_messages`
- Gestion des événements et interactions
- Commandes slash synchronisées

#### **Système de sécurité**
- `SecurityValidator` : Sanitisation des entrées
- `RateLimiter` : Protection anti-spam (3 signalements/heure)
- `ReportTracker` : Détection de doublons
- `AuditLogger` : Logs de sécurité

#### **Collecteur de preuves (RGPD-compliant)**
- `EvidenceCollector` : Mapping temporaire utilisateur/thread
- Stockage en mémoire uniquement (24h max)
- Nettoyage automatique
- Anonymisation complète

#### **Base de données Supabase**
- Table `flagged_users` : Utilisateurs signalés
- Table `audit_logs` : Logs d'audit
- Table `query_logs` : Historique des requêtes
- Fonctions SQL pour la logique métier

### 🔐 **Sécurité et conformité**

#### **RGPD et vie privée**
- Anonymat des rapporteurs préservé
- Stockage temporaire des mappings (24h)
- Droit à l'oubli respecté
- Logs de traçabilité

#### **Validation des données**
- Sanitisation de toutes les entrées utilisateur
- Taille limitée des contenus
- Validation des formats
- Protection contre l'injection

#### **Rate limiting**
- 3 signalements max par utilisateur/heure
- Détection de comportements suspects
- Blocage temporaire des abus

### 📡 **Intégrations**

#### **Supabase (Base de données)**
- PostgreSQL hébergé
- API REST automatique
- Fonctions edge pour la logique
- Sécurité RLS (Row Level Security)

#### **Discord API**
- Slash commands
- Modals et Views interactives
- Threads dans forums
- Messages privés (DM)

## 🚀 Installation et configuration

### 📋 **Prérequis**
- Python 3.11+
- Compte Discord Developer
- Projet Supabase
- Serveur Discord avec permissions admin

### ⚙️ **Variables d'environnement**
```env
DISCORD_TOKEN=your_bot_token_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
LOG_LEVEL=INFO
```

### 🔧 **Installation**
```bash
cd Aegis-bot
pip install -r requirements.txt
python bot.py
```

### 🎛️ **Configuration Discord**
1. Inviter le bot avec les permissions requises
2. Exécuter `/setup` en tant qu'administrateur
3. Attribuer le rôle `@Validateur` aux modérateurs
4. Tester avec `/agis`

## 📊 **Métriques et surveillance**

### 📈 **KPIs suivis**
- Nombre de signalements par jour/semaine
- Taux de validation des signalements
- Temps moyen de validation
- Activité des validateurs
- Détections d'utilisateurs à risque

### 🔍 **Logs et audit**
- Tous les signalements sont tracés
- Actions de validation enregistrées
- Logs de sécurité structurés
- Respect des délais de rétention

### ⚠️ **Alertes et monitoring**
- Forum non trouvé → Alerte configuration
- Erreurs Supabase → Logs d'erreur
- Rate limiting dépassé → Logs sécurité
- Validation expirée → Timeout automatique

## 🤝 **Utilisation recommandée**

### 👥 **Pour les utilisateurs**
1. Utiliser `/agis` pour signaler des comportements suspects
2. Fournir des preuves détaillées et factuelles
3. Respecter l'anonymat des autres
4. Ne pas abuser du système

### 🛡️ **Pour les modérateurs**
1. Valider les signalements rapidement et objectivement
2. Rechercher les utilisateurs avec `/check`
3. Suivre les statistiques avec `/stats`
4. Maintenir la qualité des validations

### 👑 **Pour les administrateurs**
1. Configurer le bot avec `/setup`
2. Exporter régulièrement les données
3. Surveiller les métriques
4. Former les validateurs

## 🛣️ **Roadmap et évolutions**

### 🔜 **Prochaines fonctionnalités**
- [ ] Interface web de gestion
- [ ] API REST pour intégrations
- [ ] Webhooks pour notifications externes
- [ ] Machine learning pour détection automatique
- [ ] App mobile companion

### 🎯 **Améliorations techniques**
- [ ] Réorganisation modulaire du code
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring avancé avec Prometheus
- [ ] Cache Redis pour les performances

## 📞 **Support et contribution**

### 🆘 **Support**
- Documentation : Ce fichier
- Debug : Commande `/debug`
- Logs : Fichier `aegis_bot.log`
- Issues : GitHub repository

### 🤲 **Contribution**
- Code : Respecter la structure existante
- Tests : Ajouter des tests pour nouvelles fonctionnalités
- Documentation : Mettre à jour cette documentation
- Sécurité : Signaler les vulnérabilités de manière responsable

---

## 📝 **Résumé exécutif**

**Aegis** est un bot Discord mature et sécurisé qui permet de créer un réseau de protection communautaire efficace. Avec ses fonctionnalités de signalement anonyme, validation par quorum, et base de données centralisée, il offre une solution complète pour la sécurité des communautés Discord.

**Points forts** :
- ✅ Anonymat préservé
- ✅ Validation communautaire
- ✅ Conformité RGPD
- ✅ Base centralisée
- ✅ Interface intuitive
- ✅ Système de preuves
- ✅ Logs d'audit complets

**Prêt pour la production** avec surveillance et maintenance appropriées.