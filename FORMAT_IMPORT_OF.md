# 📋 Format d'Import des Ordres de Fabrication (OF)

## 🎯 Vue d'Ensemble

Ce document décrit le format Excel requis pour importer des Ordres de Fabrication (OF) dans le système APS.

---

## 📊 Colonnes du Fichier Excel

### ✅ Colonnes Obligatoires

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| **Production** | Texte | Numéro unique de l'ordre de production | PROD-001 |
| **Item_number** | Texte | Code du produit (doit exister dans le projet) | M505110 |
| **Quantity** | Nombre | Quantité à produire | 100 |
| **Original_scheduled_start_date** | Date | Date de début planifiée (YYYY-MM-DD) | 2026-03-26 |
| **Original_scheduled_end_date** | Date | Date de fin planifiée (YYYY-MM-DD) | 2026-03-30 |
| **End_date** | Date | Date de fin (YYYY-MM-DD) | 2026-03-30 |
| **Priority_EDD** | Nombre | Priorité EDD (1=Lundi urgent, 5=Vendredi) | 1 |
| **Temps_cycle** | Nombre | Temps de cycle en heures par unité | 0.5 |
| **Capacite_operateur** | Nombre | Capacité par opérateur (unités/shift) | 20 |

### 📝 Colonnes Optionnelles (mais recommandées)

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| **Name** | Texte | Nom du produit | Bracket Assembly |
| **Unit** | Texte | Unité de mesure (EA, KG, M, etc.) | EA |
| **Delivery** | Date | Date de livraison (YYYY-MM-DD) | 2026-03-30 |
| **Status** | Texte | Statut (Scheduled, Started, Finished, etc.) | Scheduled |
| **Master_plan** | Texte | Plan directeur | PLAN-2026-Q1 |
| **Master_production_line** | Texte | Ligne de production principale | LINE-A |
| **Production_group** | Texte | Groupe de production | GROUP-1 |
| **Pool** | Texte | Pool de ressources | POOL-A |
| **Priority_reason** | Texte | Raison de la priorité | Customer urgent |
| **Efficience** | Nombre | Efficience (0.0 à 1.0, ex: 0.85 = 85%) | 1.0 |
| **Property** | Texte | Propriété | Standard |
| **Category** | Texte | Catégorie | Assembly |
| **Reference_type** | Texte | Type de référence | Production |
| **Created_by** | Texte | Créé par | Admin |

### 🔧 Colonnes Techniques Avancées

| Colonne | Type | Description | Valeur par défaut |
|---------|------|-------------|-------------------|
| **Reported_as_finished** | Nombre | Quantité déjà produite | 0 |
| **Report_remainder_as_finished** | Oui/Non | Signaler le reste comme terminé | No |
| **Remain_status** | Texte | Statut restant | (vide) |
| **Quality_order_status** | Texte | Statut ordre qualité | (vide) |
| **Locked_for_rescheduling** | Oui/Non | Verrouillé pour replanification | No |
| **Original_scheduled_start_time** | Heure | Heure de début planifiée (HH:MM:SS) | 08:00:00 |
| **Original_scheduled_end_time** | Heure | Heure de fin planifiée (HH:MM:SS) | 17:00:00 |
| **Regrade** | Texte | Regrade | (vide) |
| **Commentaire** | Texte | Commentaires libres | (vide) |

---

## 📝 Exemple de Fichier Excel

### Feuille 1: OF_Import

| Production | Item_number | Name | Quantity | Unit | Original_scheduled_start_date | Original_scheduled_end_date | End_date | Priority_EDD | Temps_cycle | Capacite_operateur |
|------------|-------------|------|----------|------|------------------------------|----------------------------|----------|--------------|-------------|-------------------|
| PROD-001 | M505110 | Bracket Assembly | 100 | EA | 2026-03-26 | 2026-03-30 | 2026-03-30 | 1 | 0.5 | 20 |
| PROD-002 | M505111 | Support Frame | 150 | EA | 2026-03-26 | 2026-03-31 | 2026-03-31 | 1 | 0.6 | 18 |
| PROD-003 | M505115 | Mounting Plate | 200 | EA | 2026-03-27 | 2026-04-01 | 2026-04-01 | 2 | 0.4 | 25 |

---

## 🚀 Comment Utiliser

### 1. Générer le Fichier Excel Exemple

```bash
cd c:\Users\DELL\Desktop\Hexcel
python generer_excel_of_complet.py
```

Cela créera le fichier **`EXEMPLE_IMPORT_OF_COMPLET.xlsx`** avec:
- Feuille 1: **OF_Import** - Données exemple
- Feuille 2: **Instructions** - Description des colonnes

### 2. Préparer Vos Données

1. Ouvrez le fichier Excel exemple
2. Remplacez les données exemple par vos vraies données
3. **Important**: Assurez-vous que les codes produits (`Item_number`) existent dans votre projet
4. Vérifiez que les dates sont au format `YYYY-MM-DD`
5. Vérifiez que les priorités EDD sont entre 1 et 5

### 3. Importer dans l'Application

1. Lancez l'application: `python app.py`
2. Allez sur le Dashboard
3. Sélectionnez votre projet (ex: BF) dans la liste déroulante
4. Cliquez sur **"Module OF"**
5. Cliquez sur **"Importer Excel"**
6. Uploadez votre fichier Excel
7. Les OF seront créés automatiquement!

---

## ⚠️ Points Importants

### Validation des Données

✅ **Vérifications automatiques:**
- Les codes produits doivent exister dans le projet
- Les dates doivent être au format YYYY-MM-DD
- Les priorités EDD doivent être entre 1 et 5
- Les quantités doivent être positives
- Le numéro de production doit être unique

❌ **Erreurs courantes:**
- Code produit inexistant → OF ignoré
- Date invalide → Erreur d'import
- Priorité hors limites → Valeur par défaut (5)
- Quantité négative ou nulle → OF ignoré

### Priorité EDD (Earliest Due Date)

| Valeur | Jour | Urgence | Utilisation |
|--------|------|---------|-------------|
| 1 | Lundi | **Très urgent** | Commandes clients urgentes |
| 2 | Mardi | Urgent | Commandes prioritaires |
| 3 | Mercredi | Normal | Production standard |
| 4 | Jeudi | Faible | Production planifiée |
| 5 | Vendredi | Très faible | Production différable |

### Temps de Cycle et Capacité

- **Temps_cycle**: Temps nécessaire pour produire **1 unité** (en heures)
  - Exemple: 0.5 = 30 minutes par pièce
  
- **Capacite_operateur**: Nombre d'unités qu'**un opérateur** peut produire en **1 shift**
  - Exemple: 20 = un opérateur produit 20 pièces par shift
  
- **Efficience**: Performance réelle vs théorique (0.0 à 1.0)
  - 1.0 = 100% (performance optimale)
  - 0.85 = 85% (performance moyenne)
  - 0.70 = 70% (performance faible)

---

## 📊 Calculs Automatiques

Lors de l'import, le système calcule automatiquement:

1. **Numéro OF**: Généré automatiquement si non fourni (OF-YYYY-NNN)
2. **Date de création**: Date/heure actuelle
3. **Statut initial**: "en_attente" (Scheduled)
4. **Quantité produite**: 0 par défaut
5. **Taux de complétion**: 0% au départ

---

## 🔄 Mise à Jour de la Base de Données

Après avoir modifié le modèle `OrdreFabrication`, exécutez:

```bash
cd c:\Users\DELL\Desktop\Hexcel
python
>>> from app import create_app
>>> from models import db
>>> app = create_app()
>>> with app.app_context():
...     db.drop_all()  # ⚠️ Supprime toutes les données!
...     db.create_all()
>>> exit()
```

**⚠️ ATTENTION**: `db.drop_all()` supprime **TOUTES** les données existantes!

Pour une migration sans perte de données, utilisez Flask-Migrate:

```bash
flask db migrate -m "Ajout attributs OF complets"
flask db upgrade
```

---

## 📞 Support

Pour toute question:
1. Consultez `MODULE_OF_ORDONNANCEMENT_COMPLET.md`
2. Consultez `ARCHITECTURE_MODULE_OF.md`
3. Vérifiez les logs dans la console Flask

---

**Date de création**: 25 Mars 2026  
**Version**: 2.0 - Format Complet  
**Statut**: ✅ Prêt pour Production
