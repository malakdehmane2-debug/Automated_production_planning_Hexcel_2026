# Guide d'Utilisation - Ordonnancement avec Opérateurs

## 🎯 Vue d'Ensemble

Ce système gère l'ordonnancement de production en tenant compte:
- **Capacité par opérateur** (ex: 1 opérateur produit 2 unités/shift)
- **Capabilités des opérateurs** (qui peut produire quoi)
- **3 shifts par jour** (au lieu de 2)
- **Deux méthodes d'ordonnancement**

---

## 📊 Les Deux Méthodes

### **MÉTHODE 1: Nombre Fixe d'Opérateurs**

**Principe:**
- Vous définissez vos opérateurs réels (OP1, OP2, etc.)
- Vous spécifiez les capabilités de chacun
- Le système assigne automatiquement qui produit quoi

**Avantages:**
- ✓ Réaliste (utilise vos vrais opérateurs)
- ✓ Respecte les compétences de chacun
- ✓ Planning directement applicable

**Utilisation:**
```python
scheduler = OperatorScheduler(shift_duration_hours=7.5, shifts_per_day=3)

# Ajouter les opérateurs avec leurs capabilités
scheduler.add_operator('OP1', ['M400200', 'M400201', 'M400228'])
scheduler.add_operator('OP2', ['M400200', 'M400228', 'M500324'])

# Générer le planning
schedule = scheduler.schedule_with_fixed_operators()
```

**Résultat:**
```
Jour  Shift  Opérateur  Item     Quantité
1     1      OP1        M400228  3
1     1      OP2        M400228  3
1     2      OP1        M400228  3
...
```

---

### **MÉTHODE 2: Calcul Automatique des Opérateurs**

**Principe:**
- Le système calcule combien d'opérateurs sont nécessaires
- Optimise pour finir dans les délais
- Peut créer des "opérateurs virtuels" si besoin

**Avantages:**
- ✓ Identifie les besoins en ressources humaines
- ✓ Optimise la durée de production
- ✓ Utile pour la planification RH

**Utilisation:**
```python
schedule, analysis = scheduler.schedule_with_calculated_operators()

print(f"Opérateurs nécessaires: {analysis['min_operators_needed']}")
```

**Résultat:**
```
Analyse des besoins:
- Charge totale: 887.35 heures
- Opérateurs minimum nécessaires: 8
- Heures disponibles par opérateur/semaine: 112.5h

Besoins par article:
Item      Charge(h)  Opérateurs nécessaires
M400228   182.00     5
M400229   171.60     4
...
```

---

## 🔧 Configuration Détaillée

### 1. Créer le Scheduler

```python
from ordonnancement_operateurs import OperatorScheduler

scheduler = OperatorScheduler(
    shift_duration_hours=7.5,  # Durée d'un shift
    shifts_per_day=3           # Nombre de shifts par jour
)
```

### 2. Ajouter les Articles

```python
scheduler.add_item(
    item_code='M400200',                    # Code article
    weekly_demand=19,                       # Besoin hebdomadaire
    capacity_per_operator_per_shift=2,      # Capacité d'UN opérateur en 1 shift
    cycle_time=2.0,                         # Temps de cycle (heures)
    efficiency=1.0,                         # Efficience (0-1)
    due_date_priority=1                     # 1=Lundi, 5=Vendredi
)
```

**⚠️ IMPORTANT:** 
- `capacity_per_operator_per_shift=2` signifie qu'**UN SEUL** opérateur produit 2 unités en 1 shift
- Si vous avez 3 opérateurs sur cet article, la capacité totale = 3 × 2 = 6 unités/shift

### 3. Définir les Opérateurs et Leurs Capabilités

```python
# Opérateur spécialisé série M400
scheduler.add_operator('OP1', ['M400200', 'M400201', 'M400228', 'M400229'])

# Opérateur spécialisé série M500
scheduler.add_operator('OP2', ['M500309', 'M500325', 'M500316'])

# Opérateur polyvalent
scheduler.add_operator('OP3', ['M400200', 'M500309', 'M500324'])
```

**Signification:**
- OP1 peut produire: M400200, M400201, M400228, M400229
- OP1 **NE PEUT PAS** produire: M500309, M500325, etc.

---

## 📈 Exemples de Résultats

### Méthode 1 - Charge par Opérateur

```
Opérateur  Quantité  Nombre de shifts
OP1        46        18
OP2        45        18
OP3        43        8
OP4        48        7
OP5        31        9
OP6        5         2
OP7        16        7
OP8        28        7
```

**Interprétation:**
- OP1 travaille 18 shifts et produit 46 unités au total
- OP6 travaille seulement 2 shifts (articles spécialisés)

### Méthode 2 - Analyse des Besoins

```
Item      Charge(h)  Shifts(1op)  Opérateurs nécessaires
M400228   182.00     24.27        5
M400229   171.60     22.88        4
M400201   108.90     14.52        3
M500324   62.40      8.32         2
```

**Interprétation:**
- M400228 nécessite **5 opérateurs** travaillant en parallèle pour finir à temps
- M500324 nécessite **2 opérateurs** seulement

---

## 🎨 Personnalisation

### Modifier le Nombre de Shifts par Jour

```python
# Passer de 3 à 2 shifts par jour
scheduler = OperatorScheduler(shift_duration_hours=7.5, shifts_per_day=2)
```

### Modifier la Durée d'un Shift

```python
# Passer de 7.5h à 8h
scheduler = OperatorScheduler(shift_duration_hours=8.0, shifts_per_day=3)
```

### Ajouter Plus d'Opérateurs

```python
# Ajouter autant d'opérateurs que nécessaire
for i in range(1, 21):  # 20 opérateurs
    scheduler.add_operator(f'OP{i}', ['M400200', 'M400201'])
```

---

## 📋 Fichiers Générés

### Méthode 1
- `planning_methode1_operateurs_fixes.csv`
  - Colonnes: Jour, Shift, Opérateur, Item, Quantité, Priorité EDD

### Méthode 2
- `planning_methode2_operateurs_calcules.csv`
  - Planning avec opérateurs calculés/virtuels
- `analyse_besoins_operateurs.csv`
  - Analyse détaillée des besoins par article

---

## 🔍 Comparaison des Méthodes

| Critère | Méthode 1 | Méthode 2 |
|---------|-----------|-----------|
| **Réalisme** | ✓ Très réaliste | Théorique |
| **Respect des compétences** | ✓ Oui | Partiellement |
| **Optimisation durée** | Moyen | ✓ Optimale |
| **Planification RH** | Non | ✓ Oui |
| **Applicable directement** | ✓ Oui | Non (besoin recrutement) |

**Recommandation:**
- **Méthode 1** pour le planning opérationnel quotidien
- **Méthode 2** pour analyser les besoins en ressources humaines

---

## 💡 Cas d'Usage Typiques

### Cas 1: Planning Hebdomadaire Normal
```python
# Utiliser Méthode 1 avec vos opérateurs réels
schedule = scheduler.schedule_with_fixed_operators()
schedule.to_csv('planning_semaine_12.csv')
```

### Cas 2: Analyser si Vous Avez Assez d'Opérateurs
```python
# Utiliser Méthode 2
schedule, analysis = scheduler.schedule_with_calculated_operators()
print(f"Vous avez besoin de {analysis['min_operators_needed']} opérateurs")
```

### Cas 3: Identifier les Goulots d'Étranglement
```python
# Regarder quels articles manquent d'opérateurs capables
prioritized = scheduler.prioritize_items()
for item in prioritized:
    if item['capable_operators_count'] < 2:
        print(f"⚠️ {item['item_code']}: seulement {item['capable_operators_count']} opérateur(s) capable(s)")
```

---

## ⚙️ Algorithme de Priorisation

### Étape 1: Calcul de la Charge
```
Charge (heures) = (Quantité × Cycle Time) / Efficience
```

### Étape 2: Calcul des Shifts
```
Shifts nécessaires = Charge / Durée shift
```

### Étape 3: Tri Multi-Critères
```
1. EDD (Earliest Due Date) - priorité principale
2. Nombre de shifts - critère secondaire (décroissant)
```

### Étape 4: Assignation aux Opérateurs
**Méthode 1:**
- Pour chaque article (dans l'ordre de priorité)
- Trouver les opérateurs capables
- Assigner au premier opérateur disponible
- Si tous occupés → passer au shift suivant

**Méthode 2:**
- Calculer combien d'opérateurs en parallèle
- Distribuer la charge entre eux
- Créer des opérateurs virtuels si nécessaire

---

## 🚨 Avertissements Importants

### ⚠️ Capacité Insuffisante
```
⚠️ ATTENTION: Aucun opérateur capable de produire M400200!
```
**Solution:** Ajouter un opérateur capable de produire cet article

### ⚠️ Goulot d'Étranglement
Si un article urgent n'a qu'un seul opérateur capable:
- Risque de retard
- Considérer la formation d'autres opérateurs

### ⚠️ Surcharge
Si la Méthode 2 indique plus d'opérateurs que vous n'en avez:
- Heures supplémentaires nécessaires
- Ou étaler sur plus de jours
- Ou recruter/former

---

## 📞 Support

Pour modifier les données:
1. Éditez la section `articles` dans `ordonnancement_operateurs.py`
2. Éditez la section `add_operator()` pour vos opérateurs réels
3. Relancez: `python ordonnancement_operateurs.py`

Pour questions: Consultez le code source avec commentaires détaillés
