# Système d'Ordonnancement de Production

## Description
Ce système génère automatiquement un planning d'ordonnancement optimal pour atteindre 100% d'adhérence au planning hebdomadaire.

## Fonctionnalités

### 1. Calcul de la Charge (Load)
- **Formule**: `Charge (heures) = (Quantité × Cycle Time) / Efficience`
- Prend en compte l'efficience moyenne de production
- Calcule le temps réel nécessaire pour chaque article

### 2. Calcul des Shifts Nécessaires
- **Formule**: `Nombre de shifts = Charge (heures) / 7.5h`
- Durée d'un shift: 7.5 heures
- Calcule combien de shifts sont nécessaires pour chaque article

### 3. Priorisation Intelligente
Le système priorise selon **deux critères**:

1. **EDD (Earliest Due Date)** - Critère principal
   - Priorité 1 = Lundi (le plus urgent)
   - Priorité 2 = Mardi
   - Priorité 3 = Mercredi
   - Priorité 4 = Jeudi
   - Priorité 5 = Vendredi

2. **Nombre de Shifts** - Critère secondaire
   - Les articles nécessitant plus de shifts sont produits en premier
   - Évite les retards sur les productions longues

### 4. Outputs Générés

Le système génère **3 fichiers**:

1. **planning_ordonnancement.csv** - Planning principal avec:
   - Rang de production
   - Item et quantité
   - Charge en heures
   - Nombre de shifts nécessaires
   - Priorité EDD
   - Date de début estimée

2. **planning_detaille_shifts.csv** - Planning détaillé par shift:
   - Jour et shift
   - Item à produire
   - Quantité par shift
   - Quantité restante

3. **Console output** - Résumé avec:
   - Charge totale
   - Shifts totaux nécessaires
   - Adhérence au planning (%)

## Installation

```bash
pip install pandas numpy
```

## Utilisation

```bash
python ordonnancement.py
```

## Structure des Données

### Format d'entrée pour chaque article:
```python
scheduler.add_item(
    item_code='M400200',           # Code article
    weekly_demand=10,              # Besoin hebdomadaire
    daily_capacity_1shift=2,       # Capacité par shift
    cycle_time=2.0,                # Temps de cycle (heures)
    efficiency=1.0,                # Efficience (0-1)
    due_date_priority=1            # Priorité EDD (1-5)
)
```

## Exemple de Résultat

```
RÉSUMÉ DU PLANNING DE PRODUCTION
================================================================================
Nombre total d'articles: 20
Quantité totale à produire: 306
Charge totale (heures): 850.50 heures
Shifts totaux nécessaires: 113.40 shifts
Durée d'un shift: 7.5 heures
Jours de production estimés (2 shifts/jour): 57 jours
================================================================================

PLANNING D'ORDONNANCEMENT (SÉQUENCE DE PRODUCTION)
================================================================================
Rang  Item      Quantité  Charge(h)  Shifts  Priorité  Date début
1     M400228   27        140.40     18.72   1         2026-02-24
2     M400229   27        140.40     18.72   1         2026-03-05
3     M400201   13        64.35      8.58    1         2026-03-10
...
================================================================================

ANALYSE D'ADHÉRENCE AU PLANNING
================================================================================
Shifts nécessaires: 113.40
Shifts disponibles (5 jours × 2 shifts): 10
Adhérence au planning: 8.8%

⚠ ATTENTION: Capacité insuffisante!
   Il manque 103.40 shifts
   Solutions: Heures supplémentaires ou étaler sur plus de jours
================================================================================
```

## Personnalisation

### Modifier la durée d'un shift:
```python
scheduler = ProductionScheduler(shift_duration_hours=8.0)
```

### Ajouter de nouveaux articles:
```python
scheduler.add_item('M500XXX', weekly_demand=50, daily_capacity_1shift=10, 
                   cycle_time=3.5, efficiency=0.95, due_date_priority=2)
```

### Modifier les priorités EDD:
Changez le paramètre `due_date_priority` (1 = plus urgent, 5 = moins urgent)

## Algorithme de Séquençage

1. **Collecte des données** pour tous les articles
2. **Calcul de la charge** (heures) pour chaque article
3. **Calcul des shifts nécessaires** pour chaque article
4. **Tri multi-critères**:
   - Premier critère: EDD (priorité croissante)
   - Second critère: Shifts nécessaires (décroissant)
5. **Génération du planning** avec dates de début
6. **Calcul de l'adhérence** au planning

## Notes Importantes

- Le système agrège automatiquement les demandes multiples pour le même article
- Les articles avec la même priorité EDD sont triés par nombre de shifts
- L'adhérence à 100% nécessite une capacité suffisante en shifts
- Le planning peut être ajusté en modifiant les paramètres d'entrée

## Support

Pour toute question ou modification, consultez le code source dans `ordonnancement.py`
