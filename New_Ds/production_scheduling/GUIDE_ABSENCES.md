# 📘 Guide d'Utilisation - Gestion des Absences

## 🎯 Fonctionnalité

Le système d'ordonnancement peut maintenant prendre en compte les **absences d'opérateurs** par shift. Le programme vous demandera interactivement combien d'opérateurs sont absents pour chaque shift.

---

## 🚀 Comment Utiliser

### **1. Lancer le Programme**

```powershell
cd C:\Users\DELL\CascadeProjects\production_scheduling
python ordonnancement_operateurs.py
```

### **2. Répondre aux Questions**

Le programme vous posera les questions suivantes:

```
⚠️  CONFIGURATION DES ABSENCES
====================================================================================================
Nombre d'opérateurs par shift (sans absences):
   - Shift 1 (Matin): 8 opérateurs
   - Shift 2 (Soir):  9 opérateurs
   - Shift 3 (Nuit):  10 opérateurs

Avez-vous des absences à signaler? (o/n):
```

#### **Option A: Pas d'absences**
```
Avez-vous des absences à signaler? (o/n): n
```
→ Le système utilisera tous les opérateurs disponibles

#### **Option B: Avec absences**
```
Avez-vous des absences à signaler? (o/n): o
   Shift 1 (Matin): Nombre d'absents (0-8): 2
   Shift 2 (Soir): Nombre d'absents (0-9): 1
   Shift 3 (Nuit): Nombre d'absents (0-10): 0
```

---

## 📊 Exemples de Scénarios

### **Scénario 1: Journée Normale**
```
Avez-vous des absences à signaler? (o/n): n

Résultat:
✓ Aucune absence signalée - tous les opérateurs sont disponibles
   Shift 1: 8 opérateurs disponibles
   Shift 2: 9 opérateurs disponibles
   Shift 3: 10 opérateurs disponibles
```

### **Scénario 2: Absences Légères**
```
Avez-vous des absences à signaler? (o/n): o
   Shift 1 (Matin): Nombre d'absents (0-8): 1
   Shift 2 (Soir): Nombre d'absents (0-9): 0
   Shift 3 (Nuit): Nombre d'absents (0-10): 0

Résultat:
⚠️  Absences configurées:
   Shift 1: 1 absent(s) → 7 opérateurs disponibles
   Shift 2: 0 absent(s) → 9 opérateurs disponibles
   Shift 3: 0 absent(s) → 10 opérateurs disponibles
```

### **Scénario 3: Absences Importantes**
```
Avez-vous des absences à signaler? (o/n): o
   Shift 1 (Matin): Nombre d'absents (0-8): 3
   Shift 2 (Soir): Nombre d'absents (0-9): 2
   Shift 3 (Nuit): Nombre d'absents (0-10): 1

Résultat:
⚠️  Absences configurées:
   Shift 1: 3 absent(s) → 5 opérateurs disponibles
   Shift 2: 2 absent(s) → 7 opérateurs disponibles
   Shift 3: 1 absent(s) → 9 opérateurs disponibles
```

---

## ⚠️ Validation des Entrées

Le système **valide automatiquement** vos entrées:

### **Entrée Invalide - Nombre Trop Grand**
```
Shift 1 (Matin): Nombre d'absents (0-8): 10
   ❌ Erreur: Le nombre doit être entre 0 et 8
Shift 1 (Matin): Nombre d'absents (0-8): 2
```

### **Entrée Invalide - Pas un Nombre**
```
Shift 1 (Matin): Nombre d'absents (0-8): abc
   ❌ Erreur: Veuillez entrer un nombre valide
Shift 1 (Matin): Nombre d'absents (0-8): 2
```

---

## 🔄 Impact sur l'Ordonnancement

Les absences **réduisent le nombre d'opérateurs** disponibles pour chaque shift:

### **Sans Absences:**
```
Jour 1, Shift 1: Peut assigner jusqu'à 8 opérateurs
Jour 1, Shift 2: Peut assigner jusqu'à 9 opérateurs
Jour 1, Shift 3: Peut assigner jusqu'à 10 opérateurs
```

### **Avec Absences {1: 2, 2: 1, 3: 0}:**
```
Jour 1, Shift 1: Peut assigner jusqu'à 6 opérateurs (8 - 2)
Jour 1, Shift 2: Peut assigner jusqu'à 8 opérateurs (9 - 1)
Jour 1, Shift 3: Peut assigner jusqu'à 10 opérateurs (10 - 0)
```

**Conséquence:** 
- ⏱️ Peut nécessiter plus de shifts pour compléter la production
- 📉 Peut réduire le taux d'atteinte des objectifs si les absences sont importantes
- 🔄 Le système s'adapte automatiquement et optimise avec les ressources disponibles

---

## 💡 Conseils

1. **Soyez Réaliste:** Entrez le nombre réel d'absents prévus
2. **Planification:** Si vous avez beaucoup d'absences, le système vous montrera si les objectifs peuvent être atteints
3. **Flexibilité:** Vous pouvez relancer le programme avec différents scénarios d'absences pour comparer

---

## 🎯 Résumé

✅ Le programme demande **interactivement** les absences  
✅ Validation **automatique** des entrées  
✅ Ajustement **automatique** du nombre d'opérateurs  
✅ Impact **visible** dans les résultats d'ordonnancement  

Bonne planification! 🚀
