# 🛡️ Permissions Discord Requises par Commande

## 📋 **Résumé des Commandes et Permissions**

### ✅ **Commandes Utilisateur (Tout le monde)**

| Commande | Permissions Discord | Permissions Serveur | Description |
|----------|-------------------|-------------------|-------------|
| `/agis` | `Send Messages` | Aucune | Créer signalement anonyme |
| `/categories` | `Send Messages` | Aucune | Voir catégories signalement |

### 🔐 **Commandes Administration**

| Commande | Permissions Discord | Permissions Serveur | Description |
|----------|-------------------|-------------------|-------------|
| `/setup` | `Administrator` | Admin serveur | Configuration initiale |
| `/stats` | `Manage Messages` | Rôle Modérateur+ | Statistiques serveur |
| `/check` | `Manage Messages` | Rôle Validateur+ | Vérifier utilisateur |
| `/validate` | `Manage Messages` | Rôle Validateur+ | Interface validation |
| `/purge` | `Manage Messages` | Rôle Modérateur+ | Purger anciens rapports |
| `/config` | `Manage Guild` | Rôle Admin+ | Configuration avancée |

### 🔧 **Commandes Debug (Conditionnelles)**

| Commande | Permissions Discord | Permissions Serveur | Description |
|----------|-------------------|-------------------|-------------|
| `/debug-mode` | `Administrator` | Admin serveur | Activer/désactiver debug |
| `/debug-info` | `Manage Messages` | Debug activé + Modérateur | Infos système |
| `/debug-services` | `Manage Messages` | Debug activé + Modérateur | État services |
| `/debug-config` | `Manage Messages` | Debug activé + Modérateur | Configuration actuelle |
| `/debug-translations` | `Manage Messages` | Debug activé + Modérateur | Test traductions |

---

## 🎯 **Permissions Discord Bot Minimales**

**Valeur numérique : `328833518672`**

### **Permissions Texte :**
- `Send Messages` (2048) - Envoyer réponses
- `Send Messages in Threads` (274877906944) - Threads forum  
- `Embed Links` (16384) - Embeds riches
- `Use Slash Commands` (2147483648) - Commandes slash
- `Manage Messages` (8192) - Gestion modération
- `Read Message History` (65536) - Historique

### **Permissions Serveur :**
- `View Channels` (1024) - Voir canaux
- `Manage Roles` (268435456) - Rôles quarantaine
- `Create Public Threads` (34359738368) - Forum alerts

---

## 📖 **Détail par Commande**

### **`/agis` - Signalement Anonyme**
- **Permission Discord** : `Send Messages` (2048)
- **Permission Serveur** : Aucune restriction
- **Utilisation** : Tous les membres du serveur
- **Vérifications** : Rate limiting (3/heure par utilisateur)

### **`/categories` - Voir Catégories**  
- **Permission Discord** : `Send Messages` (2048)
- **Permission Serveur** : Aucune restriction
- **Utilisation** : Tous les membres du serveur
- **Vérifications** : Aucune

### **`/setup` - Configuration Serveur**
- **Permission Discord** : `Administrator` (8)
- **Permission Serveur** : Administrateur du serveur
- **Utilisation** : Admins seulement
- **Vérifications** : `interaction.user.guild_permissions.administrator`

### **`/stats` - Statistiques**
- **Permission Discord** : `Manage Messages` (8192)  
- **Permission Serveur** : Rôle "Modérateur" ou supérieur
- **Utilisation** : Équipe modération
- **Vérifications** : Rôles configurés dans config serveur

### **`/check` - Vérifier Utilisateur**
- **Permission Discord** : `Manage Messages` (8192)
- **Permission Serveur** : Rôle "Validateur" ou supérieur  
- **Utilisation** : Équipe validation
- **Vérifications** : Rôles `check_command_roles` dans config

### **`/validate` - Interface Validation**
- **Permission Discord** : `Manage Messages` (8192)
- **Permission Serveur** : Rôle "Validateur" ou supérieur
- **Utilisation** : Équipe validation
- **Vérifications** : Rôles `check_command_roles` dans config

### **`/purge` - Purger Données**
- **Permission Discord** : `Manage Messages` (8192)
- **Permission Serveur** : Rôle "Modérateur" ou supérieur
- **Utilisation** : Équipe modération
- **Vérifications** : Permissions élevées requises

### **`/config` - Configuration Avancée**
- **Permission Discord** : `Manage Guild` (32)
- **Permission Serveur** : Rôle "Administrateur"
- **Utilisation** : Admins seulement
- **Vérifications** : Rôles `config_command_roles` dans config

### **`/debug-mode` - Contrôle Debug**
- **Permission Discord** : `Administrator` (8)
- **Permission Serveur** : Administrateur du serveur
- **Utilisation** : Admins seulement
- **Vérifications** : `interaction.user.guild_permissions.administrator`

### **Commandes Debug** (`/debug-*`)
- **Permission Discord** : `Manage Messages` (8192)
- **Permission Serveur** : Debug activé + Rôle "Modérateur"
- **Utilisation** : Modération avec debug activé
- **Vérifications** : `debug_enabled: true` dans config serveur

---

## ⚠️ **Important : Sécurité**

1. **Commandes Debug** désactivées par défaut
2. **Rate Limiting** sur `/agis` (3 rapports/heure)
3. **Validation rôles** sur toutes commandes admin
4. **Logs audit** pour actions sensibles
5. **Permissions minimales** pour fonctionnement

## 🔧 **Configuration Recommandée**

```json
{
  "permissions": {
    "check_command_roles": ["Validateur", "Modérateur", "Administrateur"],
    "config_command_roles": ["Administrateur"],  
    "bypass_auto_actions": ["Modérateur", "Administrateur"]
  }
}
```