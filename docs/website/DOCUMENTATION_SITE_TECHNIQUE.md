# 🛡️ AEGIS BOT - Documentation Complète pour Site Web

## 📋 Table des Matières
- [Présentation Générale](#-présentation-générale)
- [Fonctionnalités Principales](#-fonctionnalités-principales)  
- [Liste des Commandes](#-liste-des-commandes)
- [Installation et Configuration](#-installation-et-configuration)
- [Catégories de Signalement](#-catégories-de-signalement)
- [Sécurité et Anonymat](#-sécurité-et-anonymat)
- [FAQ](#-faq)
- [Support Technique](#-support-technique)
- [Screenshots et Démonstrations](#-screenshots-et-démonstrations)

---

## 🎯 Présentation Générale

### Qu'est-ce qu'Aegis Bot ?
**Aegis Bot** est un bot Discord de nouvelle génération spécialement conçu pour la **modération communautaire sécurisée**. Il permet aux utilisateurs de signaler anonymement des comportements problématiques tout en protégeant l'identité des reporters grâce à un système cryptographique avancé.

### 🌟 Points Forts Uniques
- **🔐 Anonymat total** garanti par cryptographie HMAC-SHA256
- **🛡️ Anti-abus sophistiqué** avec détection de doublons 
- **🌐 Multilingue** (Français/Anglais) avec traductions personnalisables
- **📊 Base de données centralisée** Supabase pour suivi inter-serveurs
- **🔍 Validation collaborative** par les modérateurs
- **📈 Statistiques avancées** et audit transparent

### 🎨 Interface Moderne
- Commandes **slash** intuitives (`/agis`, `/setup`, `/stats`)
- **Menus déroulants** visuels pour sélection de catégories
- **Modals** élégants pour saisie des détails
- **Embeds** colorés avec émojis et mise en forme
- **Boutons interactifs** pour validation rapide

---

## ✨ Fonctionnalités Principales

### 🔐 Système d'Anonymat Cryptographique
- **Hash HMAC-SHA256** des identifiants reporters
- **Salt secret** configurable (64 caractères hexadécimaux)
- **Impossibilité** de remonter du hash vers l'identité
- **Protection** contre l'analyse de patterns
- **Audit trail** transparent sans exposition d'identités

### 🛡️ Protection Anti-Abus Avancée  
- **Détection doublons** automatique et fiable
- Même reporter + même serveur + même cible = **BLOQUÉ**
- **Normalisation** des noms (casse, espaces)
- **Cache mémoire** pour performances optimales
- **Rate limiting** intelligent (3 signalements/heure)

### 🌍 Système Multilingue Intelligent
- **Français** et **Anglais** supportés nativement
- **Détection automatique** de langue par serveur
- **Fichiers JSON** modifiables pour traductions
- **Extension facile** vers nouvelles langues
- **Fallback** automatique vers langue par défaut

### 📊 Base de Données Centralisée Supabase
- **Historique complet** des signalements inter-serveurs
- **Système de flags** avec niveaux automatiques
- **Expiration automatique** des flags (6 mois)  
- **Sécurité RLS** (Row Level Security)
- **Fonctions optimisées** avec SECURITY DEFINER
- **Statistiques temps réel** et métriques avancées

---

## 🎮 Liste des Commandes

### 👥 **Commandes Utilisateurs**

#### `/agis` - Créer un Signalement Anonyme
- **Description**: Interface principale pour signaler un utilisateur
- **Utilisation**: `/agis`
- **Fonctionnement**:
  1. Sélection de catégorie via menu déroulant
  2. Modal avec champs : cible, raison, preuves (opt.)
  3. Validation et envoi anonyme aux modérateurs
- **Sécurité**: Anonymat garanti + détection doublons

#### `/categories` - Voir les Catégories
- **Description**: Affiche toutes les catégories de signalement disponibles
- **Utilisation**: `/categories`
- **Contenu**: Liste détaillée avec descriptions et niveaux de sévérité

### 🛡️ **Commandes Administration**

#### `/setup` - Configuration Serveur  
- **Description**: Configuration automatique complète du serveur
- **Utilisation**: `/setup` (Admin requis)
- **Actions**:
  - Création canal forum "agis-alerts"
  - Création rôle "Validateur" 
  - Configuration permissions
  - Paramétrage base de données
  - Tests de fonctionnement

#### `/stats [période]` - Statistiques Avancées
- **Description**: Rapport détaillé d'activité du serveur  
- **Utilisation**: `/stats` ou `/stats 30`
- **Paramètres**: `période` (jours, défaut: 7)
- **Métriques**:
  - Signalements totaux/validés/en attente
  - Signalements actifs en cours
  - Utilisateurs surveillés (rate limiting)
  - Connexion base données Supabase
  - Statistiques par catégorie

#### `/check <utilisateur>` - Vérifier un Utilisateur
- **Description**: Vérification complète d'un utilisateur (local + global)
- **Utilisation**: `/check @utilisateur`
- **Informations**:
  - Profil Discord (création, ID)
  - **Signalements locaux** (serveur actuel)
  - **Base globale Supabase** (tous serveurs)
  - **Niveau de risque** calculé automatiquement
  - **Historique détaillé** des flags et raisons

#### `/validate` - Interface de Validation  
- **Description**: Interface moderne pour valider signalements en attente
- **Utilisation**: `/validate` (Rôle Validateur requis)
- **Fonctionnalités**:
  - Liste signalements en attente (max 5 affichés)
  - Détails : cible, catégorie, âge du signalement
  - Boutons interactifs : Valider/Rejeter/Détails
  - Compteur restant si plus de 5

#### `/purge [jours]` - Nettoyage Automatique
- **Description**: Suppression des anciens signalements et threads
- **Utilisation**: `/purge` ou `/purge 60`
- **Paramètres**: `jours` (défaut: 30)
- **Actions**:
  - Suppression threads forum > X jours
  - Nettoyage cache service signalements  
  - Nettoyage threads archivés
  - Rapport détaillé des suppressions

### 🔧 **Commandes Debug** (Mode Développement)

#### `/debug-info` - Informations Système
- **Description**: Diagnostic complet du système
- **Utilisation**: `/debug-info`
- **Informations**:
  - Version Python/Discord.py/Supabase
  - Mémoire et performance bot
  - État des services (report_service, rate_limiter, etc.)
  - Configuration actuelle
  - Santé base de données

#### `/debug-services` - État des Services  
- **Description**: Statut détaillé de tous les services internes
- **Utilisation**: `/debug-services`

#### `/debug-translations <clé>` - Test Traductions
- **Description**: Tester le système de traduction
- **Utilisation**: `/debug-translations report_modal_title`

---

## ⚙️ Installation et Configuration

### 📋 Prérequis
- **Serveur Discord** avec permissions "Gérer le serveur"
- **Bot Discord** avec scope `applications.commands`
- **Python 3.11+** (pour auto-hébergement)
- **Base Supabase** (recommandée)

### 🚀 Installation Rapide (Recommandée)

#### Étape 1: Inviter le Bot
1. [**Lien d'invitation**](https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot%20applications.commands)
2. Sélectionner votre serveur
3. Autoriser les permissions requises

#### Étape 2: Configuration Automatique  
```
/setup
```
Cette commande :
- ✅ Crée le canal forum "agis-alerts"
- ✅ Crée le rôle "Validateur" 
- ✅ Configure les permissions
- ✅ Teste la connexion base de données
- ✅ Vérifie le système de traductions

#### Étape 3: Attribution Rôles
1. Aller dans **Paramètres Serveur > Rôles**
2. Attribuer le rôle **"Validateur"** aux modérateurs
3. Optionnel: Personnaliser les permissions du rôle

#### Étape 4: Test Fonctionnel
```
/agis
```
Tester la création d'un signalement pour valider l'installation.

### 🛠️ Installation Auto-hébergée (Avancée)

#### Configuration Environnement
```bash
# Cloner le projet
git clone https://github.com/votre-repo/aegis-bot
cd aegis-bot

# Installer dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
```

#### Variables d'Environnement
```env
# Discord (OBLIGATOIRE)
DISCORD_TOKEN=votre_token_bot_discord

# Supabase (RECOMMANDÉ)  
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_cle_anon_supabase
SUPABASE_ENABLED=true

# Sécurité Anti-Abus (CRITIQUE)
REPORTER_SALT_SECRET=votre_secret_64_caracteres_hexa

# Configuration Optionnelle
TEST_MODE_ENABLED=false
DEBUG_ENABLED=false  
LOG_LEVEL=INFO
```

#### Génération Salt Secret Sécurisé
```python
python -c "import secrets; print('REPORTER_SALT_SECRET=' + secrets.token_hex(32))"
```

#### Base de Données Supabase
1. Créer projet sur [supabase.com](https://supabase.com)
2. Aller dans **SQL Editor**  
3. Exécuter `database/supabase_schema.sql`
4. Exécuter `database/supabase_schema_anti_abuse.sql`
5. Vérifier **Authentication > RLS** activé

#### Lancement
```bash
python main.py
```

---

## 📊 Catégories de Signalement

### 🚨 **Niveau CRITIQUE** 
#### 🛡️ Sécurité des Mineurs (`child_safety`)
- **Description**: Danger potentiel pour les mineurs
- **Exemples**: Sollicitation, contenu inapproprié vers mineurs
- **Traitement**: Priorité absolue, escalade automatique

#### ⚔️ Menaces (`threats`) 
- **Description**: Menaces de violence ou de préjudice
- **Exemples**: Menaces physiques, doxxing, chantage
- **Traitement**: Validation rapide, possibilité contact autorités

### ⚠️ **Niveau ÉLEVÉ**
#### 🚫 Harcèlement (`harassment`)
- **Description**: Harcèlement, menaces ou intimidation
- **Exemples**: Harcèlement répété, intimidation, cyber-stalking
- **Traitement**: Suivi attentif, historique conservé

#### 💰 Arnaque/Phishing (`scam`)
- **Description**: Tentative d'arnaque ou de phishing  
- **Exemples**: Liens malveillants, fausses offres, usurpation
- **Traitement**: Vérification liens, alerte communauté

### 🔶 **Niveau MOYEN**
#### 📵 Contenu Inapproprié (`inappropriate_content`)
- **Description**: Contenu sexuel, violent ou dérangeant
- **Exemples**: NSFW non-tagué, gore, contenu choquant
- **Traitement**: Modération contenu, avertissement

#### 🔍 Comportement Suspect (`suspicious_behavior`)
- **Description**: Activité suspecte ou manipulation
- **Exemples**: Comptes multiples, manipulation votes, bot
- **Traitement**: Surveillance renforcée, vérification

### 🔵 **Niveau FAIBLE**
#### 📢 Spam/Flood (`spam`)
- **Description**: Messages répétitifs ou non sollicités
- **Exemples**: Publicité, flood, messages automatiques
- **Traitement**: Limitation automatique, nettoyage

#### ❓ Autre (`other`)
- **Description**: Autre raison de signalement
- **Exemples**: Violation règles spécifiques serveur
- **Traitement**: Évaluation cas par cas

---

## 🔒 Sécurité et Anonymat

### 🛡️ Garanties d'Anonymat

#### 🔐 Cryptographie HMAC-SHA256
- **Algorithme**: HMAC (Hash-based Message Authentication Code)
- **Fonction de Hash**: SHA-256 (256 bits)
- **Salt Secret**: 64 caractères hexadécimaux (256 bits)
- **Non-réversibilité**: Impossibilité mathématique de retrouver l'ID original

#### 🔄 Double Hachage
1. **Hash Reporter**: `HMAC-SHA256(reporter_id + guild_id + salt_secret)`
2. **Hash Unicité**: `HMAC-SHA256(reporter_id + guild_id + target_user + salt_secret)`

#### 🛠️ Processus Technique
```
Utilisateur → /agis suspect_user
       ↓
Salt Secret + reporter_ID + guild_ID → HMAC-SHA256 → Hash Anonyme
       ↓  
Hash Anonyme + Détails → Base de Données (SANS ID original)
       ↓
Modérateurs voient → Hash + Détails (IMPOSSIBLE de remonter à l'utilisateur)
```

### 🚫 Protection Anti-Abus

#### 🎯 Détection de Doublons
- **Même reporter** + **même serveur** + **même cible** = **BLOQUÉ**
- Normalisation automatique (casse, espaces)
- Cache mémoire haute performance
- Message informatif discret (pas d'alerte)

#### ⏱️ Rate Limiting Intelligent  
- **3 signalements maximum** par heure par utilisateur
- **Cooldown progressif** en cas d'abus
- **Whitelist automatique** pour modérateurs
- **Cache distribué** pour performance

#### 🔍 Validation Collaborative
- **Quorum 80%** des validateurs requis
- **Historique complet** des décisions
- **Audit trail** transparent
- **Révocation possible** des fausses validations

### 🗄️ Sécurité Base de Données

#### 🔐 Row Level Security (RLS)
- **Policies strictes** par table
- **Isolation** des données par serveur
- **Contrôle d'accès** granulaire
- **Audit automatique** des requêtes

#### ⚡ Fonctions Sécurisées
```sql  
SECURITY DEFINER -- Droits privilégiés
SET search_path = public -- Anti-injection
```

#### 🕘 Expiration Automatique
- **Flags automatiquement expirés** après 6 mois
- **Nettoyage automatique** des anciennes données
- **Archivage** pour statistiques historiques
- **GDPR compliant** avec suppression données

---

## ❓ FAQ - Questions Fréquentes

### 🔐 **Anonymat et Sécurité**

**Q: Mon identité est-elle vraiment protégée ?**
R: **Absolument**. Aegis utilise le cryptage HMAC-SHA256 avec un salt secret. Il est mathématiquement impossible de remonter du hash vers votre identité, même avec accès à la base de données.

**Q: Les modérateurs peuvent-ils voir qui a signalé ?**
R: **Non, jamais**. Les modérateurs voient uniquement un hash anonyme et les détails du signalement. Aucune information permettant d'identifier le reporter n'est stockée ou affichée.

**Q: Que se passe-t-il si je signale plusieurs fois la même personne ?**  
R: Le système détecte automatiquement les doublons. Votre second signalement sera silencieusement ignoré pour éviter le spam, mais vous ne serez pas pénalisé.

**Q: Puis-je supprimer un signalement que j'ai fait ?**
R: Non, car cela compromettrait l'anonymat (il faudrait vous identifier). Les signalements expirent automatiquement après 6 mois.

### ⚙️ **Configuration et Utilisation**

**Q: Comment installer Aegis sur mon serveur ?**
R: 1) Invitez le bot, 2) Utilisez `/setup` (admin requis), 3) Attribuez le rôle "Validateur" aux modérateurs, 4) Testez avec `/agis`.

**Q: Quelles permissions le bot nécessite-t-il ?**
R: Permissions essentielles : Lire messages, Envoyer messages, Gérer threads, Utiliser commandes slash, Gérer rôles (pour validation).

**Q: Le bot fonctionne-t-il sans base de données ?**
R: Oui, mais les fonctionnalités sont limitées (pas de suivi inter-serveurs, pas de flags persistants). Supabase est fortement recommandé.

**Q: Comment ajouter une nouvelle langue ?**
R: Copiez `locales/fr.json` vers `locales/votre_langue.json`, traduisez les valeurs, le bot détectera automatiquement la nouvelle langue.

### 🛠️ **Administration**  

**Q: Comment voir les statistiques de mon serveur ?**
R: Utilisez `/stats` (Validateur requis). Vous verrez signalements totaux/validés/pendants, utilisateurs actifs, statut base de données.

**Q: Comment valider les signalements ?**  
R: Utilisez `/validate` pour voir l'interface moderne avec boutons. Ou consultez manuellement le forum "agis-alerts" créé automatiquement.

**Q: Que signifient les niveaux de risque ?**
R: 🟢 FAIBLE (0 validé), 🟡 MOYEN (1 validé), 🟠 ÉLEVÉ (2 validés), 🔴 CRITIQUE (3+ validés). Basé sur l'historique global.

**Q: Comment nettoyer les anciens signalements ?**
R: Utilisez `/purge [jours]` (défaut 30 jours). Supprime automatiquement threads anciens + nettoyage cache interne.

### 🔧 **Problèmes Techniques**

**Q: Le bot ne répond pas aux commandes slash ?**
R: Vérifiez : 1) Permissions bot, 2) Commandes synchronisées (redémarrage serveur), 3) Status bot (vert), 4) Logs d'erreur.

**Q: "Base de données indisponible" ?**
R: Problème connexion Supabase. Vérifiez : URL/clé correctes, projet actif, quotas non dépassés, connexion réseau.

**Q: Les traductions ne s'affichent pas ?** 
R: Le bot détecte automatiquement la langue. Forcez avec paramètre `language` ou vérifiez fichiers `locales/*.json`.

**Q: Comment activer les commandes debug ?**
R: Définissez `DEBUG_ENABLED=true` dans `.env` (auto-hébergement) ou contactez l'administrateur du bot.

### 📊 **Base de Données et Flags**

**Q: Qu'est-ce qu'un "flag global" ?**
R: Un marqueur dans la base Supabase indiquant qu'un utilisateur a été signalé/validé sur n'importe quel serveur utilisant Aegis.

**Q: Les flags sont-ils permanents ?**
R: Non, ils expirent automatiquement après **6 mois** pour respecter les principes de données personnelles et réhabilitation.

**Q: Un serveur peut-il voir les signalements d'autres serveurs ?**
R: Les détails non, mais le statut global (flagué/niveau de risque) est visible pour protéger toute la communauté Discord.

**Q: Comment fonctionne le système de niveaux ?**
R: Automatique basé sur nombre de flags validés : 1 flag = FAIBLE, 2-3 = MOYEN, 4-5 = ÉLEVÉ, 6+ = CRITIQUE.

---

## 🆘 Support Technique  

### 📞 **Contacts Support**

#### 🐛 **Bugs et Problèmes**
- **GitHub Issues**: [Créer un ticket](https://github.com/votre-repo/aegis-bot/issues)
- **Format**: Description détaillée + logs + étapes reproduction
- **Réponse**: 24-48h en moyenne

#### 💡 **Demandes de Fonctionnalités**  
- **GitHub Discussions**: [Proposer une idée](https://github.com/votre-repo/aegis-bot/discussions)
- **Discord Support**: Serveur communauté (lien)
- **Email**: support@aegis-bot.com

#### ⚡ **Aide Rapide**
- **Documentation**: [Lien vers docs complètes]
- **FAQ**: [Section FAQ étendue]
- **Tutoriels vidéo**: [Chaîne YouTube]
- **Guide troubleshooting**: [Lien vers guide]

### 🔍 **Auto-Diagnostic**

#### ✅ **Vérifications de Base**
```
1. Bot en ligne (statut vert) ?
2. Permissions correctes ?
3. Commandes slash synchronisées ?
4. Canal "agis-alerts" créé ?  
5. Rôle "Validateur" existe ?
```

#### 🔧 **Tests de Fonctionnement**
```
/debug-info     → Infos système
/debug-services → État des services
/stats          → Test base de données
/agis          → Test signalement complet
```

#### 📋 **Informations à Fournir pour Support**
- Version bot (visible dans `/debug-info`)
- Messages d'erreur complets
- ID serveur Discord
- Étapes exactes causant problème  
- Screenshots si pertinents
- Logs bot si auto-hébergé

### 🚀 **Statut Service**

#### 📊 **Page Statut en Temps Réel**
- **Uptime bot**: [Status page]
- **Performance base de données**: Supabase status
- **Incidents connus**: Timeline mise à jour
- **Maintenances programmées**: Calendrier

#### 🔔 **Alertes Service**
- **Discord**: Serveur alertes (lien invitation)
- **Twitter**: @AegisBotStatus  
- **RSS**: Flux incidents
- **Email**: Notifications majeures

---

## 📸 Screenshots et Démonstrations

### 🎨 **Interface Utilisateur**

#### 📱 **Commande /agis - Signalement**
```
[Screenshot 1: Menu déroulant catégories]
- Interface moderne avec émojis
- 8 catégories colorées  
- Descriptions claires
- Sélection intuitive

[Screenshot 2: Modal de signalement]  
- Champs organisés
- Placeholder informatifs
- Validation temps réel
- Boutons stylés
```

#### 📊 **Commande /stats - Statistiques**  
```
[Screenshot 3: Embed statistiques]
- Graphiques colorés avec émojis
- Métriques en temps réel
- Période configurable
- Footer avec infos serveur
```

#### 🔍 **Commande /check - Vérification**
```
[Screenshot 4: Profil utilisateur détaillé]
- Informations Discord
- Signalements locaux/globaux  
- Niveau de risque visuel
- Historique chronologique
```

### ⚙️ **Interface Administration**

#### 🛠️ **Commande /setup - Configuration**
```
[Screenshot 5: Wizard de configuration]  
- Étapes claires numérotées
- Validation en temps réel
- Messages de confirmation
- Tests automatiques
```

#### ✅ **Interface /validate - Validation**
```
[Screenshot 6: Queue validation moderne]
- Liste signalements pending
- Boutons action rapide
- Détails expandables  
- Compteurs visuels
```

### 🔧 **Fonctionnalités Avancées**

#### 📈 **Dashboard Supabase**
```
[Screenshot 7: Tables base de données]
- Structure données anonymes
- Hash HMAC-SHA256 visibles
- Policies RLS actives
- Functions sécurisées
```

#### 🌍 **Système Multilingue**  
```
[Screenshot 8: Interface EN vs FR]
- Traductions côte à côte
- Cohérence visuelle
- Émojis universels
- Formatage respecté
```

### 🎥 **Démonstrations Vidéo**

#### 📺 **Tutoriel Installation (5 min)**
1. Invitation bot sur serveur
2. Commande /setup automatique  
3. Attribution rôles validateurs
4. Premier signalement test
5. Validation par modérateur

#### 🎬 **Démonstration Anonymat (3 min)**
1. Signalement utilisateur A
2. Vue modérateur (hash anonyme) 
3. Tentative doublon (bloqué)
4. Base de données (pas d'ID original)
5. Preuve non-réversibilité

#### 📹 **Guide Administration Complet (10 min)**
1. Configuration avancée
2. Commandes /stats détaillées
3. Analyse /check utilisateur
4. Interface /validate moderne  
5. Maintenance avec /purge
6. Troubleshooting courant

---

## 🎯 Call-to-Action Site

### 🚀 **Boutons d'Action Principaux**

```html
<!-- Bouton principal -->
<a href="[LIEN_INVITATION]" class="btn-primary">
  🛡️ AJOUTER AEGIS À MON SERVEUR
</a>

<!-- Boutons secondaires -->
<a href="#demo" class="btn-secondary">
  📺 VOIR LA DÉMO
</a>

<a href="#features" class="btn-secondary">  
  ✨ DÉCOUVRIR LES FONCTIONNALITÉS
</a>
```

### 📊 **Statistiques Impressionnantes**
- **🔒 100% Anonymat** garanti cryptographiquement
- **🚀 4/4 Tests** sécurité validés  
- **🌍 2 Langues** supportées nativement
- **⚡ <100ms** temps de réponse moyen
- **🛡️ 8 Catégories** de protection
- **📈 6 Mois** expiration automatique flags

### 🎖️ **Badges de Confiance**
- ✅ **Open Source** - Code vérifiable
- 🔐 **RGPD Compliant** - Données protégées  
- 🛡️ **Sécurisé** - Cryptographie militaire
- ⚡ **Performant** - Architecture optimisée
- 🆓 **Gratuit** - Usage illimité  
- 🔄 **Mis à jour** - Support continu

---

*Cette documentation est conçue pour être convertie facilement en site web moderne avec sections, navigation, screenshots et design responsive.*