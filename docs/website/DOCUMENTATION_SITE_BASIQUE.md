# 🛡️ AEGIS BOT - Documentation Site Web

## 🎯 Qu'est-ce qu'Aegis Bot ?

**Aegis Bot** est un bot Discord qui permet à votre communauté de **signaler anonymement** les comportements problématiques. L'identité des personnes qui signalent est **complètement protégée** grâce à un système de sécurité avancé.

### ⭐ Pourquoi Choisir Aegis ?

- **🔐 Anonymat garanti** - Impossible de savoir qui a signalé
- **🛡️ Anti-spam intelligent** - Empêche les signalements en double 
- **🌍 Multilingue** - Interface en français et anglais
- **📊 Suivi inter-serveurs** - Base de données partagée entre communautés
- **🎨 Interface moderne** - Menus intuitifs et boutons interactifs

---

## 🎮 Comment ça marche ?

### 🚨 **Pour signaler quelqu'un**
1. Tapez `/agis` dans Discord
2. Choisissez le type de problème dans le menu
3. Remplissez le formulaire (nom, raison)
4. C'est envoyé aux modérateurs **sans révéler qui vous êtes**

### 👮 **Pour les modérateurs**
- Recevez les signalements dans un canal privé
- Vérifiez et validez les signalements
- Consultez l'historique des utilisateurs problématiques
- Gérez votre serveur avec des statistiques détaillées

---

## 📝 Types de Signalement

### 🚨 **Situations Urgentes**

**🛡️ Protection des mineurs**
- Quand : Comportement inapproprié envers les enfants
- Action : Traitement prioritaire immédiat

**⚔️ Menaces graves**  
- Quand : Menaces de violence ou chantage
- Action : Validation rapide et escalade possible

### ⚠️ **Comportements Problématiques**

**🚫 Harcèlement**
- Quand : Messages répétés non désirés, intimidation
- Action : Suivi de l'historique pour détecter les patterns

**💰 Arnaques**
- Quand : Liens suspects, fausses offres
- Action : Vérification et alerte à la communauté

### 🔶 **Contenus Déplacés**

**📵 Contenu inapproprié**
- Quand : Images/vidéos non adaptées à votre serveur
- Action : Modération du contenu

**🔍 Activité suspecte**
- Quand : Comportement de bot, comptes multiples
- Action : Surveillance renforcée

### 🔵 **Nuisances Mineures**

**📢 Spam**
- Quand : Messages publicitaires répétitifs
- Action : Limitation automatique

**❓ Autres**
- Quand : Violation des règles spécifiques de votre serveur
- Action : Évaluation personnalisée

---

## 🎮 Commandes Disponibles

### 👥 **Pour Tous les Membres**

**`/agis` - Créer un signalement**
- Interface simple avec menus déroulants
- Formulaire guidé étape par étape
- Anonymat garanti à 100%

**`/categories` - Voir tous les types**
- Liste complète des catégories de signalement
- Descriptions détaillées pour chaque type

### 🛡️ **Pour les Modérateurs**

**`/setup` - Configuration automatique**
- Crée automatiquement le canal de signalements
- Configure les rôles et permissions
- Prêt en 1 minute !

**`/stats` - Statistiques du serveur**
- Nombre de signalements par période
- Tendances et évolutions
- État de la base de données

**`/check @utilisateur` - Vérifier un membre**
- Historique complet des signalements
- Niveau de risque calculé automatiquement
- Informations locales et globales

**`/validate` - Valider les signalements**
- Interface moderne avec boutons
- Queue des signalements en attente
- Actions rapides : Valider/Rejeter

**`/purge` - Nettoyer les anciens signalements**
- Suppression automatique des vieux signalements
- Libère l'espace et améliore les performances

---

## ⚙️ Installation Facile

### 🚀 **En 3 étapes simples**

1. **[Inviter le bot](LIEN_INVITATION)** sur votre serveur
2. Taper **`/setup`** (nécessite les droits admin)
3. **C'est prêt !** Le bot crée tout automatiquement

### 📋 **Ce que `/setup` fait pour vous :**
- ✅ Crée le canal forum "agis-alerts" 
- ✅ Crée le rôle "Validateur" pour vos modérateurs
- ✅ Configure toutes les permissions nécessaires
- ✅ Teste que tout fonctionne correctement

### 🎯 **Attribution des rôles**
Après l'installation, donnez le rôle **"Validateur"** à vos modérateurs pour qu'ils puissent :
- Voir les signalements
- Utiliser `/stats`, `/check`, `/validate`
- Gérer la modération

---

## 🔐 Comment l'Anonymat fonctionne

### 🛡️ **Protection d'Identité**

Quand vous signalez quelqu'un :
1. **Votre nom devient un code secret** impossible à décrypter
2. **Seuls les détails du signalement** sont envoyés aux modérateurs  
3. **Impossible de remonter vers vous**, même pour les administrateurs
4. **Protection permanente** - votre identité ne peut jamais être révélée

### 🚫 **Anti-Doublons**

Le système détecte automatiquement :
- Si vous avez **déjà signalé** cette personne sur ce serveur
- **Empêche les signalements répétés** par la même personne
- **Aucune sanction** - votre tentative est simplement ignorée silencieusement

### 📊 **Suivi Inter-Serveurs**

- Les **signalements validés** sont partagés entre serveurs participants
- Permet de **détecter les récidivistes** qui changent de serveur
- **Seul le résultat** est partagé (flagué/pas flagué), pas les détails
- **Respect total** de la vie privée de chaque communauté

---

## 🎯 Niveaux d'Alerte Utilisateurs

Basé sur le **nombre de signalements validés** qu'un utilisateur a reçu :

### 🟢 **Utilisateur Propre** (0 signalement validé)
- Aucun signalement confirmé
- Profil normal

### 🟡 **Surveillance** (1 signalement validé)  
- Un incident confirmé
- Surveillance discrète

### 🟠 **Attention** (2-3 signalements validés)
- Plusieurs incidents confirmés  
- Surveillance renforcée recommandée

### 🔴 **Risque Élevé** (4+ signalements validés)
- Pattern de comportement problématique établi
- Mesures préventives recommandées

*Les niveaux se réinitialisent automatiquement après 6 mois sans nouveau signalement validé.*

---

## ❓ Questions Fréquentes

### 🔐 **Sécurité et Anonymat**

**❓ Mon identité est-elle vraiment protégée ?**
✅ Oui, totalement. Le système transforme votre identité en code impossible à décrypter.

**❓ Les modérateurs peuvent-ils savoir qui a signalé ?**
❌ Non, jamais. Ils voient seulement le signalement et un code anonyme.

**❓ Puis-je signaler plusieurs fois la même personne ?**
⚠️ Non, le système bloque automatiquement les doublons pour éviter le spam.

### ⚙️ **Utilisation**

**❓ Comment installer Aegis sur mon serveur ?**
🚀 Invitez le bot → tapez `/setup` → c'est prêt en 1 minute !

**❓ Quelles permissions le bot nécessite-t-il ?**
🔧 Permissions standards : lire/envoyer messages, créer threads, gérer les threads.

**❓ Le bot fonctionne-t-il hors ligne ?**
📊 Oui pour les signalements locaux, mais la base globale nécessite une connexion.

### 🛠️ **Administration**

**❓ Comment voir les statistiques de mon serveur ?**
📈 Utilisez `/stats` - vous verrez tous les chiffres importants.

**❓ Comment nettoyer les anciens signalements ?**
🧹 Utilisez `/purge` - supprime automatiquement les signalements de plus de 30 jours.

**❓ Un utilisateur peut-il contester un signalement ?**
⚖️ Les utilisateurs ne savent pas qu'ils sont signalés. Seuls les modérateurs gèrent les validations.

---

## 🆘 Besoin d'Aide ?

### 📞 **Support Rapide**
- 🐛 **Problèmes techniques** : [GitHub Issues](lien)
- 💬 **Questions générales** : [Discord Support](lien)
- 📧 **Contact direct** : support@aegis-bot.com

### 📚 **Ressources**
- 📖 **Guide complet** : [Documentation technique](lien)
- 🎥 **Tutoriels vidéo** : [Chaîne YouTube](lien)
- ❓ **FAQ étendue** : [Base de connaissances](lien)

---

## 🚀 Prêt à Protéger votre Communauté ?

### 🎯 **Aegis Bot en chiffres**
- **🔒 100% Anonyme** - Identité jamais révélée
- **⚡ Installation** - 1 minute avec `/setup`  
- **🌍 Multilingue** - Français + Anglais
- **📊 Inter-serveurs** - Base de données partagée
- **🆓 Gratuit** - Usage illimité

### 🛡️ **Rejoignez les communautés protégées**

[**🚀 AJOUTER AEGIS À MON SERVEUR**](LIEN_INVITATION)

*Protégez votre communauté en gardant l'anonymat des reporters* ✨

---

*Aegis Bot - La modération communautaire nouvelle génération*