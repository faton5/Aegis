# 📜 Scripts Aegis Bot

Scripts utilitaires organisés par catégorie.

## 🧪 **Tests**
*Scripts de test et validation*

- **[run_tests.py](run_tests.py)** - Script principal de tests automatisés
- **[run_tests.bat](run_tests.bat)** - Version batch pour Windows
- **[test_anti_abuse_simple.py](tests/test_anti_abuse_simple.py)** - Tests système anti-abus
- **[test_anti_abuse_system.py](tests/test_anti_abuse_system.py)** - Tests complets anti-abus

## 🗃️ **Database**
*Scripts de gestion base de données*

- **[check_database_state.py](database/check_database_state.py)** - Vérification état BDD
- **[debug_user_flags.py](database/debug_user_flags.py)** - Debug flags utilisateurs

## 🎯 **Utilisation**

### Lancer tous les tests
```bash
python scripts/run_tests.py
```

### Tests avec couverture
```bash  
python scripts/run_tests.py -c
```

### Test anti-abus rapide
```bash
python scripts/tests/test_anti_abuse_simple.py
```

### Vérifier base de données
```bash
python scripts/database/check_database_state.py
```

---

*Scripts organisés pour un développement efficace* 🚀