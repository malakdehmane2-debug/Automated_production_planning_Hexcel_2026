# Architecture du Module OF et Ordonnancement

## 🎯 Vue d'ensemble

Module complet de gestion des Ordres de Fabrication (OF) avec ordonnancement intégré pour chaque projet.

## 📊 Flux de Travail

```
Dashboard
    ↓
Liste des Projets (par Zone)
    ↓
[Clic sur "Module OF"]
    ↓
Module OF du Projet
    ├── Liste des OF (filtrables: tous, en cours, terminés, en attente)
    ├── Créer un OF manuellement
    ├── Importer des OF depuis Excel
    └── Statistiques (total, en cours, terminés, en attente)
    ↓
[Clic sur "Configurer Ordonnancement"]
    ↓
Configuration Ordonnancement
    ├── Sélection des OF à ordonnancer
    ├── Paramètres (nombre d'opérateurs par shift, absences)
    ├── Définition des compétences opérateurs
    └── Lancement du calcul
    ↓
[Génération du Planning]
    ↓
Affichage du Planning
    ├── Vue par jour/shift/opérateur
    ├── Quantités assignées
    └── Export Excel
```

## 🗄️ Modèle de Données

### OrdreFabrication
```python
- id (PK)
- numero_of (unique, ex: OF-2024-0001)
- projet_id (FK)
- produit_id (FK)
- quantite_demandee
- quantite_produite
- date_creation
- date_lancement
- date_livraison_prevue
- date_livraison_reelle
- statut (en_attente, en_cours, termine, annule)
- priorite_edd (1-5, Lundi-Vendredi)
- temps_cycle (heures)
- capacite_par_operateur (unités/shift)
- efficience (0.0-1.0)
- commentaire
```

## 🛣️ Routes Créées

### Module OF
- `GET /zone/<id>/projet/<id>/of` - Liste des OF avec filtres
- `GET/POST /zone/<id>/projet/<id>/of/creer` - Créer un OF
- `GET/POST /zone/<id>/projet/<id>/of/importer` - Importer OF depuis Excel

### Ordonnancement
- `GET/POST /zone/<id>/projet/<id>/ordonnancement/config` - Configuration
- `POST /zone/<id>/projet/<id>/ordonnancement/generer` - Générer planning
- `GET /zone/<id>/projet/<id>/ordonnancement/planning` - Afficher planning

## 📄 Templates à Créer

### 1. `templates/of/liste.html`
- Tableau des OF avec colonnes:
  - Numéro OF
  - Produit
  - Quantité demandée/produite
  - Dates
  - Statut (badge coloré)
  - Priorité EDD
  - Actions (voir, modifier, supprimer)
- Filtres par statut (boutons)
- Statistiques en haut
- Boutons: Créer OF, Importer Excel

### 2. `templates/of/creer.html`
- Formulaire de création d'OF:
  - Sélection produit (dropdown)
  - Quantité demandée
  - Date lancement
  - Date livraison prévue
  - Priorité EDD (1-5)
  - Temps cycle (optionnel)
  - Capacité par opérateur (optionnel)
  - Efficience (défaut 1.0)
  - Commentaire

### 3. `templates/of/importer.html`
- Upload fichier Excel
- Instructions format:
  ```
  Colonnes: Produit, Quantite, DateLancement, DateLivraison, PrioriteEDD
  Optionnel: TempsCycle, CapaciteOperateur
  ```
- Exemple téléchargeable

### 4. `templates/ordonnancement/config.html`
- **Section 1: Sélection des OF**
  - Liste checkboxes des OF disponibles
  - Affichage: Numéro, Produit, Quantité, Priorité
  
- **Section 2: Paramètres Shifts**
  - Shift 1 (Matin): Nombre opérateurs, Absences
  - Shift 2 (Après-midi): Nombre opérateurs, Absences
  - Shift 3 (Nuit): Nombre opérateurs, Absences
  
- **Section 3: Compétences Opérateurs** (optionnel pour v1)
  - Définir quels opérateurs peuvent faire quels produits
  
- **Bouton: Générer Planning**

### 5. `templates/ordonnancement/planning.html`
- Tableau planning:
  ```
  | Jour | Shift | OP01 | OP02 | ... | OP14 |
  |------|-------|------|------|-----|------|
  |      |       | Item | Item |     | Item |
  |      |       | Qté  | Qté  |     | Qté  |
  ```
- Légende couleurs (par priorité EDD)
- Statistiques:
  - Charge totale (heures)
  - Taux d'utilisation
  - Nombre de shifts nécessaires
- **Bouton: Exporter Excel**

## 🔧 Intégration OperatorScheduler

### Étape 1: Copier la classe
```python
# Créer: ordonnancement_engine.py
# Copier OperatorScheduler depuis ordonnancement_operateurs.py
```

### Étape 2: Adapter pour Flask
```python
def generer_planning_projet(projet_id, of_ids, params):
    """
    Args:
        projet_id: ID du projet
        of_ids: Liste des IDs d'OF à ordonnancer
        params: {
            'operators_per_shift': {1: 8, 2: 9, 3: 10},
            'absences_per_shift': {1: 0, 2: 0, 3: 0}
        }
    
    Returns:
        DataFrame avec colonnes: Jour, Shift, Opérateur, Item, Quantité
    """
    scheduler = OperatorScheduler(
        operators_per_shift=params['operators_per_shift'],
        absences_per_shift=params['absences_per_shift']
    )
    
    # Charger les OF depuis la DB
    ordres = OrdreFabrication.query.filter(
        OrdreFabrication.id.in_(of_ids)
    ).all()
    
    # Ajouter les items au scheduler
    for of in ordres:
        scheduler.add_item(
            item_code=of.produit.reference,
            weekly_demand=of.quantite_demandee - of.quantite_produite,
            capacity_per_operator_per_shift=of.capacite_par_operateur or 10,
            cycle_time=of.temps_cycle or 1.0,
            efficiency=of.efficience,
            due_date_priority=of.priorite_edd
        )
    
    # Ajouter les opérateurs (pour v1: tous polyvalents)
    for i in range(1, 15):
        op_name = f"OP{i:02d}"
        scheduler.add_operator(
            operator_name=op_name,
            capable_items=[of.produit.reference for of in ordres],
            efficiency=0.85
        )
    
    # Générer le planning (Méthode 1)
    assignments = scheduler.schedule_with_fixed_operators()
    
    return pd.DataFrame(assignments)
```

### Étape 3: Sauvegarder les résultats
```python
# Option 1: Sauvegarder dans la session Flask
session['planning_projet_{projet_id}'] = planning_df.to_json()

# Option 2: Créer un modèle PlanningOrdonnancement
# Option 3: Générer Excel et sauvegarder le fichier
```

## 📝 Format Excel Import OF

```
| Produit  | Quantite | DateLancement | DateLivraison | PrioriteEDD | TempsCycle | CapaciteOperateur |
|----------|----------|---------------|---------------|-------------|------------|-------------------|
| M505110  | 100      | 2024-03-25    | 2024-03-29    | 1           | 0.5        | 20                |
| M505111  | 150      | 2024-03-26    | 2024-03-30    | 2           | 0.6        | 18                |
```

## 🎨 Statuts et Couleurs

- **en_attente**: Badge gris (secondary)
- **en_cours**: Badge bleu (primary)
- **termine**: Badge vert (success)
- **annule**: Badge rouge (danger)

## 🚀 Prochaines Étapes

1. ✅ Modèle OrdreFabrication créé
2. ✅ Dashboard modifié avec boutons projets
3. ✅ Routes créées (OF + Ordonnancement)
4. ⏳ Créer templates (liste OF, créer, importer, config, planning)
5. ⏳ Copier et adapter OperatorScheduler
6. ⏳ Intégrer génération planning
7. ⏳ Export Excel du planning
8. ⏳ Tests avec données réelles

## 💡 Améliorations Futures (v2)

- Gestion fine des compétences opérateurs
- Historique des plannings générés
- Comparaison méthode 1 vs méthode 2
- Optimisation avec contraintes supplémentaires
- Dashboard temps réel de production
- Mise à jour automatique quantités produites
- Alertes retards de livraison
