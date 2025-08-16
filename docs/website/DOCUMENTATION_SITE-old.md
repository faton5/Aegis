# 🛡️ AEGIS BOT - Documentation Complète pour Site Web

## 🎯 Qu'est-ce qu'Aegis Bot ?

**Aegis Bot** est un système de signalement communautaire **anonyme et sécurisé** pour Discord. Il permet à vos membres de signaler discrètement les comportements problématiques tout en protégeant totalement l'identité des reporters.

### ⭐ Ce qui rend Aegis unique

- **🔐 Anonymat mathématiquement garanti** - Impossible de retrouver qui a signalé
- **🛡️ Détection anti-doublons** - Empêche le spam de signalements  
- **📊 Base de données inter-serveurs** - Suivi des récidivistes entre communautés
- **⚡ Rate limiting intelligent** - Maximum 3 signalements par heure
- **🌍 Interface multilingue** - Français et anglais avec détection automatique
- **🎨 Design moderne** - Menus déroulants, modals élégants, embeds colorés

---

## 🎮 Comment fonctionne Aegis ?

### 🚨 **Processus de signalement (côté utilisateur)**

1. **Commande `/agis`** - Lance l'interface de signalement
2. **Menu déroulant** - Choix parmi 8 catégories prédéfinies  
3. **Modal de saisie** - 2 champs obligatoires :
   - **Cible** : Nom d'utilisateur, @mention ou ID Discord
   - **Raison** : Description du problème (500 caractères max)
4. **Validation instantanée** - Vérification sécurité + anti-doublons
5. **Anonymisation** - Votre identité devient un code indéchiffrable
6. **Envoi aux modérateurs** - Thread privé créé automatiquement

### 👮 **Gestion modérateur (côté administration)**

1. **Réception** - Nouveau thread dans canal "agis-alerts"
2. **Informations disponibles** :
   - Détails du signalement (cible, raison, catégorie)
   - Code anonyme du reporter (impossible à décrypter)
   - Horodatage précis
   - Niveau de priorité selon la catégorie
3. **Actions possibles** :
   - `/validate` - Interface avec boutons Valider/Rejeter
   - `/check @utilisateur` - Historique complet local + global
   - `/stats` - Statistiques détaillées du serveur

---

## 📝 Les 8 Catégories de Signalement 

### 🚨 **Priorité CRITIQUE (traitement immédiat)**

**🛡️ Sécurité des mineurs** (`child_safety`)
- **Situations** : Contenu inapproprié vers mineurs, sollicitation
- **Action** : Validation prioritaire, possible escalade externe

**⚔️ Menaces graves** (`threats`)
- **Situations** : Menaces physiques, chantage, doxxing
- **Action** : Traitement rapide, documentation complète

### ⚠️ **Priorité ÉLEVÉE (surveillance renforcée)**

**🚫 Harcèlement** (`harassment`)  
- **Situations** : Messages répétés non désirés, intimidation systématique
- **Action** : Historique conservé, patterns détectés automatiquement

**💰 Arnaques** (`scam`)
- **Situations** : Liens malveillants, fausses offres, phishing
- **Action** : Vérification liens, alerte communauté si confirmé

### 🔶 **Priorité MOYENNE (modération standard)**

**📵 Contenu inapproprié** (`inappropriate_content`)
- **Situations** : NSFW non signalé, violence graphique, contenu choquant  
- **Action** : Modération contenu, rappel règles serveur

**🔍 Activité suspecte** (`suspicious_behavior`)
- **Situations** : Comportements de bot, comptes multiples, manipulation
- **Action** : Surveillance technique, analyse patterns

### 🔵 **Priorité FAIBLE (gestion automatisée)**

**📢 Spam/Flood** (`spam`)
- **Situations** : Messages publicitaires répétitifs, flood intentionnel
- **Action** : Rate limiting automatique, nettoyage en lot

**❓ Autres problèmes** (`other`)
- **Situations** : Violations règles spécifiques à votre serveur
- **Action** : Évaluation personnalisée selon vos critères

---

## 🎮 Commandes Complètes du Bot

### 👥 **Commandes Publiques (tous les membres)**

#### `/agis` - Créer un signalement anonyme
- **Fonctionnement** :
  1. Affiche menu déroulant avec 8 catégories
  2. Ouvre modal avec champs Cible + Raison
  3. Valide les données (longueur, contenu, sécurité)
  4. Vérifie anti-doublons (même reporter + cible + serveur)
  5. Applique rate limiting (3 max/heure)
  6. Anonymise l'identité (hash HMAC impossible à décrypter)
  7. Crée thread privé pour modérateurs
  8. Confirme envoi sans révéler l'identité

#### `/categories` - Voir tous les types de signalement
- **Affichage** : Liste complète des 8 catégories avec descriptions et niveaux de priorité
- **Langues** : Traductions automatiques selon la langue du serveur

### 🛡️ **Commandes Modération (rôle "Validateur" requis)**

#### `/setup` - Configuration automatique du serveur
- **Actions automatiques** :
  1. Crée canal forum "agis-alerts" avec permissions sécurisées
  2. Crée rôle "Validateur" avec couleur verte  
  3. Configure permissions : modérateurs lecture/écriture, membres aucun accès
  4. Ajoute automatiquement rôles admin existants aux permissions
  5. Teste la configuration et confirme le succès

#### `/stats [période]` - Statistiques avancées  
- **Paramètres** : Période en jours (défaut: 7 jours)
- **Métriques affichées** :
  - Signalements totaux/validés/en attente (forum Discord)
  - Signalements actifs en mémoire (ReportService)
  - Utilisateurs surveillés par rate limiting
  - État connexion base de données Supabase
  - Analyse tendances par période

#### `/check @utilisateur` - Vérification utilisateur complète
- **Informations Discord** :
  - Nom d'affichage, ID, date de création du compte
  - Statut membre du serveur actuel
- **Signalements locaux** (serveur actuel) :
  - Historique complet des signalements le concernant
  - Compteurs par statut (validés/pending/rejetés)
  - 3 signalements les plus récents avec détails
- **Base de données globale** (inter-serveurs) :
  - Statut flagué/non flagué dans la base Supabase
  - Niveau de risque automatique (Clean/Watch/Alert/High)
  - Nombre de flags actifs vs total historique
  - Dernière catégorie et raison (sans détails sensibles)
- **Niveau de risque calculé** :
  - 🟢 Faible (0 validé) / 🟡 Moyen (1 validé) / 🟠 Élevé (2-3 validés) / 🔴 Critique (4+ validés)

#### `/validate` - Interface de validation moderne
- **Fonctionnalités** :
  - Liste des 5 prochains signalements en attente
  - Informations : ID, cible, catégorie, âge du signalement
  - Boutons interactifs pour actions rapides
  - Compteur si plus de 5 signalements en queue
  - Historique des décisions pour audit

#### `/purge [jours]` - Nettoyage automatique
- **Paramètres** : Nombre de jours à conserver (défaut: 30)
- **Actions** :
  1. Supprime threads forum > X jours (actifs + archivés)
  2. Nettoie cache interne ReportService  
  3. Comptes détaillés : threads actifs supprimés, archivés supprimés
  4. Rapport final avec statistiques de nettoyage

### 🔧 **Commandes Debug (mode développement uniquement)**

#### `/debug-info` - Diagnostic système complet
- **Informations techniques** :
  - Versions Python, Discord.py, Supabase  
  - Utilisation mémoire et performance
  - État de tous les services (ReportService, RateLimiter, etc.)
  - Configuration active (sans secrets)
  - Santé connexion base de données

---

## ⚙️ Installation et Configuration

### 🚀 **Installation Rapide (3 étapes)**

1. **[Inviter Aegis Bot](LIEN_INVITATION)** avec permissions `328833518672`
   - Inclut toutes les permissions nécessaires
   - Pas besoin d'administrateur permanent
2. **Lancer `/setup`** (droits administrateur requis)
   - Configuration automatique complète en < 30 secondes
3. **Attribuer rôle "Validateur"** aux modérateurs
   - Donne accès aux commandes `/stats`, `/check`, `/validate`

### 📋 **Ce que fait automatiquement `/setup`**

- ✅ **Canal forum "agis-alerts"** avec permissions sécurisées :
  - Membres normaux : aucun accès 
  - Bot : lecture/écriture/gestion threads
  - Validateurs : lecture + utilisation commandes
  - Administrateurs : accès complet
- ✅ **Rôle "Validateur"** avec couleur verte distinctive
- ✅ **Tests automatiques** de fonctionnement
- ✅ **Confirmation visuelle** avec résumé des actions

### 🔐 **Variables d'environnement (auto-hébergement)**

```env
# Discord (OBLIGATOIRE)
DISCORD_TOKEN=votre_token_bot

# Supabase - Base de données centralisée (RECOMMANDÉ)  
SUPABASE_ENABLED=true
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_cle_anon

# Sécurité anti-abus (CRITIQUE pour anonymat)
REPORTER_SALT_SECRET=64_caracteres_hex_aleatoires

# Optionnel
TEST_MODE_ENABLED=false
DEBUG_ENABLED=false  
LOG_LEVEL=INFO
```

---

## 🔐 Système d'Anonymat et Sécurité

### 🛡️ **Protection d'Identité (détails techniques simplifiés)**

**Processus d'anonymisation** :
1. Votre ID Discord + ID serveur + clé secrète → Fonction mathématique
2. Résultat = code unique impossible à inverser
3. Seul ce code est stocké, jamais votre vraie identité
4. Même les administrateurs ne peuvent pas vous identifier

**Garanties de sécurité** :
- ✅ **Non-réversibilité** : Impossible de retrouver votre ID depuis le code
- ✅ **Résistance aux attaques** : Même avec accès complet à la base
- ✅ **Unité temporelle** : Chaque signalement a un code différent
- ✅ **Protection administrative** : Même les développeurs ne peuvent pas vous identifier

### 🚫 **Système Anti-Doublons**

**Détection automatique** :
- Même reporter + même serveur + même cible = **BLOQUÉ SILENCIEUSEMENT**
- Normalisation des noms (majuscules/minuscules, espaces)
- Cache haute performance pour vérification instantanée
- Aucune pénalité pour l'utilisateur qui tente un doublon

**Rate Limiting intelligent** :
- **3 signalements maximum par heure** par utilisateur
- Compteur par serveur (reset à minuit)
- Cooldown progressif en cas d'abus répété
- Messages d'erreur informatifs avec temps d'attente restant

### 📊 **Base de Données Inter-Serveurs**

**Supabase - Fonctionnalités** :
- **Signalements validés partagés** entre serveurs participants
- **Détection récidivistes** changeant de communauté
- **Respect vie privée** : Seul le statut flagué/non-flagué est partagé
- **Expiration automatique** : Flags supprimés après 6 mois sans récidive
- **Sécurité maximale** : RLS (Row Level Security) + fonctions chiffrées

**Niveaux d'alerte automatiques** :
- **🟢 Clean** (0 signalement validé) - Utilisateur normal
- **🟡 Watch** (1 signalement validé) - Surveillance discrète  
- **🟠 Alert** (2-3 signalements validés) - Attention renforcée
- **🔴 High Risk** (4+ signalements validés) - Mesures préventives

---

## 📊 Limites et Contraintes Techniques

### ⚡ **Rate Limiting**
- **3 signalements max/heure** par utilisateur et par serveur
- **500 caractères max** pour la raison du signalement
- **100 caractères max** pour le nom de la cible
- **Timeout modal** : 10 minutes pour remplir le formulaire

### 🏗️ **Architecture et Performance**
- **Cache mémoire** pour détection doublons instantanée
- **Validation entrées** : Sanitisation automatique anti-injection
- **Timeouts configurés** : 2 minutes pour commandes, 10 minutes pour modals
- **Logs détaillés** : Audit trail complet sans exposition d'identités

### 🌍 **Multilingue**
- **Langues supportées** : Français (défaut), Anglais
- **Détection automatique** : Basée sur la langue configurée du serveur
- **Fallback intelligent** : Retour au français si traduction manquante
- **Extensibilité** : Ajout facile de nouvelles langues via fichiers JSON

---

## ❓ FAQ Détaillée

### 🔐 **Anonymat et Sécurité**

**❓ Comment êtes-vous sûrs que l'anonymat est garanti ?**
✅ Le système utilise une fonction mathématique (hachage cryptographique) qui transforme votre identité en code. Cette transformation est à sens unique - impossible de faire le chemin inverse, même avec des superordinateurs.

**❓ Que voient exactement les modérateurs ?**
👁️ Ils voient : le signalement, la cible, la raison, un code anonyme (ex: "5a7f9e2d..."), l'horodatage. Ils ne voient JAMAIS votre nom, votre ID, ou toute info permettant de vous identifier.

**❓ Que se passe-t-il si je signale plusieurs fois la même personne ?**
🚫 Le système détecte le doublon automatiquement et ignore silencieusement votre nouvelle tentative. Vous n'êtes pas pénalisé, mais le signalement n'est pas créé.

**❓ Les administrateurs Discord peuvent-ils forcer l'accès à mon identité ?**
❌ Non. Même avec accès root au serveur et à la base de données, il est mathématiquement impossible de retrouver votre identité depuis le code anonyme.

### ⚙️ **Utilisation et Installation**

**❓ Quelles permissions exactes le bot nécessite-t-il ?**
🔧 Permissions minimales : Lire/envoyer messages, créer/gérer threads, embeds, commandes slash. Pour l'installation initiale, administrateur temporaire pour créer canal + rôle.

**❓ Que faire si `/setup` échoue ?**
🛠️ Vérifications : bot a-t-il les permissions admin ? Canal "agis-alerts" existe-t-il déjà ? Rôle "Validateur" existe-t-il ? Si problème persiste, supprimez manuellement et relancez.

**❓ Le bot peut-il fonctionner sans Supabase ?**
📊 Oui, mais fonctionnalités limitées : signalements locaux uniquement, pas de suivi inter-serveurs, pas de niveaux d'alerte globaux. Supabase fortement recommandé.

**❓ Comment traduire le bot dans ma langue ?**
🌍 Actuellement français + anglais. Pour autres langues, contactez le support pour guide d'ajout de traductions personnalisées.

### 🛠️ **Administration**

**❓ Comment interpréter les statistiques `/stats` ?**
📈 
- **Signalements totaux** : Tous les signalements de la période
- **Validés** : Confirmés par modérateurs (deviennent flags globaux)
- **En attente** : Non encore traités
- **Signalements actifs** : En mémoire du bot (cache)
- **Utilisateurs surveillés** : Compteur rate limiting actif

**❓ Quelle est la différence entre signalements locaux et globaux ?**
🌐 **Locaux** : Uniquement sur votre serveur, détails complets, vous contrôlez. **Globaux** : Base partagée, seul statut flagué/niveau risque, protection contre récidivistes.

**❓ Comment gérer un faux signalement ?**
⚖️ Utilisez `/validate` pour rejeter. Le signalement est marqué rejeté mais conservé pour audit. Si pattern de faux signalements, surveillez le code anonyme (même reporter = même code).

**❓ Que faire si le bot ne répond plus ?**
🔄 Vérifications : bot en ligne ? Permissions OK ? `/debug-info` pour diagnostic. Redémarrage serveur Discord peut résoudre problèmes de synchronisation des commandes.

---

## 🆘 Support et Ressources

### 📞 **Contacts Support**
- 🐛 **Bugs/Problèmes** : [GitHub Issues](lien) avec logs détaillés  
- 💬 **Questions** : [Discord Support](lien) - Communauté d'aide
- 📧 **Contact direct** : support@aegis-bot.com pour cas urgents

### 📚 **Documentations Techniques**
- 📖 **Guide développeur** : Architecture, APIs, contribution
- 🎥 **Tutoriels vidéo** : Installation, configuration, utilisation avancée
- 🔧 **Troubleshooting** : Solutions aux problèmes courants
- 📋 **Changelog** : Historique des mises à jour et nouvelles fonctionnalités

### 🔍 **Auto-Diagnostic**
```
Tests rapides si problème :
1. Bot en ligne (statut vert) ?
2. Commandes slash synchronisées ?  
3. Canal "agis-alerts" existe ?
4. Rôle "Validateur" attribué ?
5. `/debug-info` pour infos système
```

---

## 🚀 Prêt à Sécuriser votre Communauté ?

### 🎯 **Aegis Bot en Chiffres Précis**
- **🔒 100% Anonymat** garanti par hachage cryptographique
- **⚡ 3 étapes** d'installation (invitation + /setup + attribution rôles)
- **📊 8 catégories** de signalement avec niveaux de priorité
- **🌍 2 langues** (FR/EN) avec détection automatique
- **⏱️ 3 max/heure** rate limiting intelligent
- **📈 4 niveaux** d'alerte utilisateur automatiques
- **🧹 6 mois** expiration automatique des flags
- **🆓 Gratuit** avec usage illimité

### 🛡️ **Communautés Protégées avec Aegis**

**Fonctionnalités uniques** :
✅ Signalements **100% anonymes** - Impossible de retrouver le reporter  
✅ **Anti-doublons** intelligent - Empêche le spam de signalements  
✅ **Base inter-serveurs** - Détection récidivistes entre communautés  
✅ **Interface moderne** - Menus, modals, boutons intuitifs  
✅ **Rate limiting** - Protection contre l'abus (3 max/heure)  
✅ **Multilingue** - Français + Anglais avec détection auto  
✅ **Audit complet** - Logs transparents pour modérateurs  
✅ **Configuration auto** - Prêt en 1 minute avec /setup  

[**🚀 AJOUTER AEGIS À MON SERVEUR**](LIEN_INVITATION)

*La modération communautaire sécurisée et anonyme pour Discord* ✨

---

## 📋 Informations Techniques pour Développement Site

### 🎨 **Assets et Visuels**
- **Logo** : Shield (🛡️) avec couleurs Discord (bleu/gris)
- **Couleurs principales** : Bleu Discord (#5865F2), Vert succès (#00D166), Rouge alerte (#ED4245)
- **Screenshots nécessaires** :
  - Interface `/agis` (menu + modal)
  - Panel modérateur `/stats` 
  - Résultat `/check` utilisateur
  - Configuration `/setup`
  - Forum "agis-alerts" avec threads

### 📱 **Sections Site Recommandées**
1. **Hero** - "Modération Anonyme pour Discord" avec CTA principal
2. **Fonctionnalités** - 6 blocs : Anonymat, Anti-abus, Inter-serveurs, Multilingue, Installation, Support
3. **Comment ça marche** - 3 étapes : Signaler, Anonymiser, Modérer  
4. **Catégories** - Grid 8 catégories avec icônes et descriptions
5. **Installation** - Guide visuel 3 étapes avec captures
6. **FAQ** - Questions groupées par thème (Sécurité, Usage, Admin)
7. **Support** - Liens ressources + Discord community
8. **Footer** - Liens légaux + réseaux sociaux

### 🔗 **Liens Dynamiques à Intégrer**
- **Invitation bot** : `https://discord.com/api/oauth2/authorize?client_id=BOT_ID&permissions=328833518672&scope=bot%20applications.commands`
- **Serveur support** : Discord community link
- **Documentation** : Lien vers docs techniques  
- **GitHub** : Repository du projet
- **Status page** : Uptime et incidents

*Cette documentation contient tous les détails nécessaires pour créer un site web complet et professionnel pour Aegis Bot* 🎯