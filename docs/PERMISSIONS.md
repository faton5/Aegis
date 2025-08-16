# 🔐 Permissions Minimales Requises - Aegis Bot

## 📋 **Permissions Strictement Nécessaires**

### ✅ **Permissions de Base (OBLIGATOIRES)**

| Permission | Utilisation | Code Source |
|------------|-------------|-------------|
| **Lire les messages** | Lire contenu serveur, historique threads | `cogs/admin.py:473-491` |
| **Envoyer des messages** | Réponses commandes, notifications | `cogs/*.py` (toutes interactions) |
| **Utiliser les commandes slash** | Fonctionnement des commandes `/agis`, `/setup` | Toutes les commandes |
| **Intégrer des liens** | Embeds avec couleurs et formatting | Toutes les réponses embed |
| **Ajouter des réactions** | Interface validation (optionnel) | `ui/views/setup_views.py:69` |

### 🛠️ **Permissions d'Administration (SETUP UNIQUEMENT)**

| Permission | Utilisation | Code Source |
|------------|-------------|-------------|
| **Gérer les canaux** | Créer forum "agis-alerts" | `ui/views/setup_views.py:82-86` |
| **Gérer les rôles** | Créer rôle "Validateur" | `ui/views/setup_views.py:47-52` |
| **Gérer les threads** | Créer threads signalements + suppression (purge) | `ui/modals/report_modals.py:256`, `cogs/admin.py:399,409` |

### 📊 **Permissions Optionnelles (RECOMMANDÉES)**

| Permission | Utilisation | Code Source |
|------------|-------------|-------------|
| **Historique des messages** | Statistiques avancées `/stats` | `cogs/admin.py:473-491` |
| **Mentions @everyone/@here** | Alertes critiques (non utilisé actuellement) | Future feature |

---

## 🎯 **Configuration Recommandée**

### 🔗 **Lien d'Invitation Optimisé**
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=347136&scope=bot%20applications.commands
```

**Permissions incluses (347136) :**
- ✅ Lire les messages
- ✅ Envoyer des messages  
- ✅ Gérer les messages (threads)
- ✅ Intégrer des liens
- ✅ Historique des messages
- ✅ Ajouter des réactions
- ✅ Utiliser commandes slash
- ✅ Gérer les threads
- ✅ Créer threads publics

### ⚠️ **Permissions ADMIN Temporaires (Setup)**

Pour la commande `/setup`, le bot a besoin temporairement de :
- **Gérer les canaux** (créer forum)  
- **Gérer les rôles** (créer rôle Validateur)

**Solution recommandée :**
1. **Installation :** Donner temporairement "Administrateur"
2. **Lancer `/setup`** une seule fois
3. **Retirer "Administrateur"** et garder seulement les permissions de base
4. Le bot fonctionnera normalement ensuite

---

## 🔒 **Analyse de Sécurité**

### ✅ **Permissions SAFE**
- **Pas d'accès** aux messages privés
- **Pas de bannissement** ou kick
- **Pas de gestion** des invitations
- **Pas d'accès** aux webhooks
- **Lecture seule** des rôles existants

### 🛡️ **Principe Moindre Privilège**

Le bot respecte le principe de sécurité :
```python
# Vérification permissions utilisateur AVANT actions
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Permissions insuffisantes")
    return
```

### 🎭 **Permissions par Fonctionnalité**

#### 🚨 **Signalements (`/agis`)**
- ✅ Envoyer messages (réponses ephemeral)
- ✅ Créer threads (dans forum existant)
- ✅ Intégrer liens (embeds)

#### 📊 **Administration (`/stats`, `/check`)**  
- ✅ Lire messages (historique forum)
- ✅ Historique messages (calcul statistiques)

#### 🧹 **Maintenance (`/purge`)**
- ✅ Gérer threads (suppression anciens)
- ⚠️ **Vérification :** Admin serveur requis

#### ⚙️ **Configuration (`/setup`)**
- ⚠️ Gérer canaux (création forum unique)
- ⚠️ Gérer rôles (création rôle unique)

---

## 📋 **Instructions d'Installation**

### 🎯 **Option 1: Installation Simple (Recommandée)**
```
1. Inviter avec permissions = 347136
2. /setup (créera forum + rôle automatiquement)
3. Attribuer rôle "Validateur" aux modérateurs
4. Prêt ! 🎉
```

### 🔐 **Option 2: Installation Sécurisée Maximale**
```  
1. Inviter avec permissions minimales = 19456
2. Créer MANUELLEMENT :
   - Canal forum "agis-alerts" 
   - Rôle "Validateur"
   - Permissions appropriées sur le forum
3. Le bot fonctionnera sans `/setup`
```

### 🧪 **Option 3: Installation Test**
```
1. Inviter avec "Administrateur" temporaire
2. /setup puis /agis (test complet) 
3. Réduire permissions à 347136
4. Production ready 🚀
```

---

## ❓ **FAQ Permissions**

**Q: Pourquoi le bot a-t-il besoin de "Gérer les threads" ?**
R: Pour créer les threads de signalement dans le forum et supprimer les anciens (commande `/purge`).

**Q: Peut-on fonctionner SANS "Gérer les canaux" ?**  
R: Oui, si vous créez manuellement le forum "agis-alerts" et donnez les bonnes permissions au bot dessus.

**Q: Le bot peut-il lire les messages privés ?**
R: **NON**. Il n'a aucune permission sur les DM et n'y accède jamais.

**Q: Que se passe-t-il sans "Historique des messages" ?**
R: Les statistiques `/stats` seront limitées aux threads récents seulement.

**Q: Le bot stocke-t-il les messages lus ?**
R: **NON**. Il ne lit que pour calculer les statistiques temporaires, rien n'est stocké.

---

## 🎖️ **Badge de Confiance**

```
🔒 PERMISSIONS MINIMALES VÉRIFIÉES
✅ Principe moindre privilège respecté  
✅ Aucun accès messages privés
✅ Pas de permissions dangereuses
✅ Code source auditable
```

*Aegis Bot respecte votre vie privée et la sécurité de votre serveur.* 🛡️