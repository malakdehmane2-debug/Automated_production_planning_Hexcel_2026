# Guide de Test - Importation BOM Multi-Niveaux

## 🎯 Objectif du Test

Vérifier que l'importation Excel crée correctement la nomenclature multi-niveaux et que le calcul des besoins totaux agrège bien les quantités.

## 📊 Cas de Test: M505110

### Structure attendue

```
M505110 (Produit Fini)
├── M308000 (PSF) - Qté: 1 EA
│   └── M206100 (MP) - Qté: 1 Pcs
├── M308001 (PSF) - Qté: 1 EA
│   └── M206100 (MP) - Qté: 1 Pcs
├── AV003253 (MP) - Qté: 100 sq ft
└── AV003155 (MP) - Qté: 0.4 sq ft
```

### Besoins Totaux Attendus

Pour produire **1 unité de M505110**, vous avez besoin de:

| Référence | Quantité | Unité | Calcul |
|-----------|----------|-------|--------|
| **M206100** | **2** | **Pcs** | 1 (de M308000) + 1 (de M308001) = **2** |
| AV003253 | 100 | sq ft | Direct |
| AV003155 | 0.4 | sq ft | Direct |

**⚠️ IMPORTANT:** M206100 doit apparaître avec une quantité de **2 Pcs**, pas 1!

## 🧪 Procédure de Test

### Étape 1: Préparer le fichier Excel

Votre fichier Excel doit contenir exactement ces lignes:

```
ParentItem | ChildItem | NAME        | BOMQTY | UNITID | Level
-----------|-----------|-------------|--------|--------|------
M505110    | M308000   | M505110-01  | 1      | EA     | 1
M505110    | M308001   | M505110-01  | 1      | EA     | 1
M505110    | AV003253  | M505110-01  | 100    | sq ft  | 1
M505110    | AV003155  | M505110-01  | 0.4    | sq ft  | 1
M505110    | M206100   | M308000-01  | 1      | Pcs    | 2
M505110    | M206100   | M308001-01  | 1      | Pcs    | 2
```

**Points clés:**
- Lignes 5-6: M206100 apparaît **2 fois** (une pour chaque PSF)
- Colonne NAME niveau 2: "M308000-01" et "M308001-01" indiquent les vrais parents

### Étape 2: Importer le fichier

1. Lancez l'application Flask:
   ```bash
   python app.py
   ```

2. Naviguez vers votre projet

3. Cliquez sur **"📥 Importer BOM Excel"**

4. Sélectionnez votre fichier Excel

5. Cliquez sur **"Importer"**

### Étape 3: Vérifier les logs d'importation

Dans la console, vous devriez voir:

```
[Niveau 1] MP: M308000 → Parent: M505110 (Qté: 1 EA)
  ✓ MP créée: M308000 attachée à M505110
[Niveau 1] MP: M308001 → Parent: M505110 (Qté: 1 EA)
  ✓ MP créée: M308001 attachée à M505110
[Niveau 1] MP: AV003253 → Parent: M505110 (Qté: 100 sq ft)
  ✓ MP créée: AV003253 attachée à M505110
[Niveau 1] MP: AV003155 → Parent: M505110 (Qté: 0.4 sq ft)
  ✓ MP créée: AV003155 attachée à M505110
[Niveau 2] MP: M206100 → Parent: M308000 (Qté: 1 Pcs)
  ✓ MP créée: M206100 attachée à M308000
[Niveau 2] MP: M206100 → Parent: M308001 (Qté: 1 Pcs)
  ✓ MP créée: M206100 attachée à M308001
```

**✅ Vérification:** M206100 doit être créé **2 fois**, une fois pour M308000 et une fois pour M308001.

### Étape 4: Consulter la nomenclature

1. Cliquez sur le produit **M505110**

2. Cliquez sur **"Nomenclature"**

3. Vérifiez l'arbre de nomenclature

### Étape 5: Vérifier les logs de calcul

Dans la console, vous devriez voir:

```
DEBUG MP - Produit: M505110, Multiplicateur: 1.0
DEBUG MP - 2 items trouvés pour M505110
  → AV003253: 0.0 + (100.0 × 1.0) = 100.0
  → AV003155: 0.0 + (0.4 × 1.0) = 0.4
DEBUG MP - 2 assemblages pour M505110
  → Descente vers PSF: M308000 (qté: 1.0)
  DEBUG MP - Produit: M308000, Multiplicateur: 1.0
  DEBUG MP - 1 items trouvés pour M308000
    → M206100: 0.0 + (1.0 × 1.0) = 1.0
  → Descente vers PSF: M308001 (qté: 1.0)
  DEBUG MP - Produit: M308001, Multiplicateur: 1.0
  DEBUG MP - 1 items trouvés pour M308001
    → M206100: 1.0 + (1.0 × 1.0) = 2.0  ← AGRÉGATION!

=== RÉSUMÉ MP TOTAUX ===
M206100: 2.0 Pcs  ← CORRECT!
AV003253: 100.0 sq ft
AV003155: 0.4 sq ft
```

**✅ Vérification clé:** 
- M206100 commence à 0.0
- Après M308000: 0.0 + 1.0 = 1.0
- Après M308001: 1.0 + 1.0 = **2.0** ✓

### Étape 6: Vérifier l'affichage

Dans la section **"Matières Premières Totales"**, vous devez voir:

| Référence | Désignation | Quantité Totale |
|-----------|-------------|-----------------|
| M206100 | M308000-01 | **2.0 Pcs** |
| AV003253 | M505110-01 | 100.0 sq ft |
| AV003155 | M505110-01 | 0.4 sq ft |

## 🐛 Problèmes Possibles

### Problème 1: M206100 montre 1 Pcs au lieu de 2

**Cause:** Les MP ne sont pas correctement attachées aux PSF lors de l'importation.

**Solution:** Vérifiez les logs d'importation. M206100 doit être créé 2 fois:
- Une fois attaché à M308000
- Une fois attaché à M308001

### Problème 2: M206100 n'apparaît pas du tout

**Cause:** Le niveau 2 n'est pas traité ou la colonne NAME n'est pas correctement parsée.

**Solution:** Vérifiez que:
- La colonne NAME contient "M308000-01" et "M308001-01"
- Le niveau est bien 2 dans le fichier Excel

### Problème 3: M206100 est attaché à M505110 au lieu des PSF

**Cause:** La logique de détection du parent pour niveau 2 ne fonctionne pas.

**Solution:** Vérifiez les logs d'importation. Vous devriez voir:
```
[Niveau 2] MP: M206100 → Parent: M308000
```
Et PAS:
```
[Niveau 2] MP: M206100 → Parent: M505110
```

## 📝 Résumé des Vérifications

- [ ] Fichier Excel correctement formaté avec 6 lignes
- [ ] M206100 apparaît 2 fois dans le fichier (niveau 2)
- [ ] Importation réussie sans erreur
- [ ] Logs montrent M206100 créé 2 fois (pour M308000 et M308001)
- [ ] Arbre de nomenclature montre M206100 sous M308000 ET M308001
- [ ] Calcul récursif agrège: 0 + 1 + 1 = 2
- [ ] Affichage final: M206100 = **2 Pcs** ✓

## 🎓 Explication Technique

Le système utilise un `defaultdict` pour agréger les quantités:

```python
mp_totaux = defaultdict(lambda: {'designation': '', 'quantite': 0.0, 'unite': ''})

# Première itération (M308000)
mp_totaux['M206100']['quantite'] += 1.0 * 1.0  # = 1.0

# Deuxième itération (M308001)
mp_totaux['M206100']['quantite'] += 1.0 * 1.0  # = 2.0
```

La clé est que **la même référence (M206100) accumule les quantités** grâce à l'opérateur `+=`.

## 🚀 Prochaines Étapes

Une fois le test validé avec M505110, vous pouvez:
1. Importer les autres produits finis (M505111, M505115, M505116)
2. Vérifier que chaque produit calcule correctement ses besoins totaux
3. Utiliser ces données pour la planification de production
