# 🔐 Guide Permissions Discord - Aegis Bot

## ❌ **ERREUR 403 - Missing Permissions**

Si tu vois cette erreur : `403 Forbidden (error code: 50013): Missing Permissions`

**→ Le bot n'a pas les bonnes permissions Discord !**

---

## 🛠️ **SOLUTION RAPIDE**

### **1. Utilise ce lien d'invitation :**
```
https://discord.com/oauth2/authorize?client_id=TON_BOT_ID&permissions=328833518672&scope=bot
```
*(Remplace TON_BOT_ID par l'ID de ton bot)*

### **2. Ou donne ces permissions manuellement :**

#### **🔧 Permissions Serveur :**
- ✅ **Gérer les rôles** - Pour créer le rôle "Validateur"
- ✅ **Gérer les salons** - Pour créer le forum "agis-alerts"  
- ✅ **Voir les salons** - Accès de base

#### **📝 Permissions Messages :**
- ✅ **Envoyer des messages** - Réponses aux commandes
- ✅ **Envoyer messages dans les fils** - Forum alerts
- ✅ **Intégrer des liens** - Embeds riches
- ✅ **Lire l'historique** - Vérifications

#### **🧵 Permissions Threads :**
- ✅ **Créer des fils publics** - Threads forum
- ✅ **Envoyer messages dans les fils** - Alerts

---

## 🎯 **VALEUR PERMISSION TOTALE**

**Valeur numérique : `328833518672`**

Cette valeur correspond exactement aux permissions minimales nécessaires pour qu'Aegis fonctionne correctement.

---

## ✅ **VÉRIFICATION AUTOMATIQUE**

Le bot vérifie maintenant automatiquement ses permissions au démarrage :

```
🤖 Démarrage d'Aegis Bot...
📋 Vérification de la configuration...
✅ Configuration validée
🔌 Connexion à Discord...
✅ BotName connecté - 2 serveur(s) - 9 commandes
✅ Permissions OK sur ServeurTest
⚠️ Permissions manquantes sur ServeurProblème: Manage Roles, Manage Channels
   URL d'invitation: https://discord.com/oauth2/authorize?client_id=123456789&permissions=328833518672&scope=bot
```

---

## 🚨 **ERREURS COURANTES**

### **`Missing Permissions` lors du `/setup`**
- **Cause** : Bot n'a pas "Gérer les rôles" ou "Gérer les salons"
- **Solution** : Re-inviter avec le lien ci-dessus

### **Bot ne peut pas créer des threads**
- **Cause** : Pas la permission "Créer des fils publics"
- **Solution** : Donner la permission dans Paramètres Serveur → Rôles → @BotName

### **Embeds ne s'affichent pas**
- **Cause** : Pas la permission "Intégrer des liens"
- **Solution** : Activer cette permission pour le rôle du bot

---

## 💡 **CONSEILS**

1. **Role Position** : Le rôle du bot doit être AU-DESSUS des rôles qu'il veut gérer
2. **Permissions Salon** : Vérifier aussi les permissions spécifiques par salon
3. **Admin** : Donner "Administrateur" donne toutes les permissions (mais pas recommandé)

---

## 📞 **AIDE**

Si tu as encore des problèmes :
1. Vérifier que le bot est bien en ligne
2. Tester avec `/categories` (commande simple)
3. Regarder les logs de démarrage pour voir les permissions manquantes
4. Re-inviter le bot avec le lien complet

**Le bot te dira exactement quelles permissions manquent !**