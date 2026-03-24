# Guide d'Importation BOM depuis Excel

## 📋 Vue d'ensemble

Cette fonctionnalité permet d'importer automatiquement une nomenclature (Bill of Materials - BOM) multi-niveaux depuis un fichier Excel. Le système crée automatiquement:
- Les **produits finis** (Finished Goods)
- Les **produits semi-finis** (PSF - Produits Semi-Finis)
- Les **matières premières** (MP)
- Les **relations d'assemblage** entre les produits

## 🎯 Cas d'utilisation

Vous avez un fichier Excel contenant la structure complète de vos produits avec leurs composants sur plusieurs niveaux. Au lieu de créer manuellement chaque produit, PSF et matière première, vous importez tout en une seule opération.

## 📊 Format du fichier Excel

### Colonnes requises

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **ParentItem** | Code du produit parent | M505110 |
| **ChildItem** | Code du composant enfant | M308000 |
| **NAME** | Nom/désignation du produit | M505110-01 |
| **BOMQTY** | Quantité nécessaire | 1, 100, 0.4 |
| **UNITID** | Unité de mesure | EA, Pcs, sq ft, m2 |
| **Level** | Niveau dans la nomenclature | 1, 2, 3... |

### Exemple de structure

```
ParentItem | ChildItem | NAME        | BOMQTY | UNITID | Level
-----------|-----------|-------------|--------|--------|------
M505110    | M308000   | M505110-01  | 1      | EA     | 1
M505110    | M308001   | M505110-01  | 1      | EA     | 1
M505110    | AV003253  | M505110-01  | 100    | sq ft  | 1
M505110    | AV003155  | M505110-01  | 0.4    | sq ft  | 1
M505110    | M206100   | M308000-01  | 1      | Pcs    | 2  ← NAME indique le vrai parent!
M505110    | M206100   | M308001-01  | 1      | Pcs    | 2  ← NAME indique le vrai parent!
```

**⚠️ IMPORTANT pour les niveaux 2+:**
- La colonne `ParentItem` reste le produit fini (M505110)
- La colonne `NAME` indique le **vrai parent** (M308000-01 ou M308001-01)
- Le système extrait le code parent de NAME (avant le tiret "-")
- Ainsi M206100 sera correctement attaché à M308000 et M308001, pas à M505110

## 🔍 Comment ça fonctionne?

### 1. Détection automatique des types de produits

Le système analyse le fichier Excel et détermine automatiquement:

- **Produits Finis (PF)**: Les `ParentItem` qui apparaissent au niveau 1 et ne sont jamais des `ChildItem`
  - Exemple: M505110, M505111, M505115, M505116

- **Produits Semi-Finis (PSF)**: Les `ChildItem` qui apparaissent aussi comme `ParentItem` ailleurs dans le fichier
  - Exemple: M308000, M308001 (ils sont enfants de M505110 mais ont eux-mêmes des composants)

- **Matières Premières (MP)**: Les `ChildItem` qui n'apparaissent jamais comme `ParentItem`
  - Exemple: AV003253, AV003155, M206100

### 2. Construction de la nomenclature multi-niveaux

**Logique de traitement:**

Pour **Niveau 1** (composants directs du produit fini):
- Le système utilise la colonne `ParentItem` pour déterminer le parent
- Exemple: M308000 appartient à M505110

Pour **Niveau 2+** (composants des PSF):
- Le système utilise la colonne `NAME` pour déterminer le vrai parent
- La colonne `NAME` contient le code du parent suivi d'un tiret (ex: "M308000-01")
- Le système extrait le code avant le tiret: "M308000-01" → parent = M308000
- Exemple: M206100 avec NAME="M308000-01" appartient à M308000, pas à M505110

**Niveau 1**: Composants directs du produit fini
```
M505110 (PF)
├── M308000 (PSF) - Quantité: 1 EA
├── M308001 (PSF) - Quantité: 1 EA
├── AV003253 (MP) - Quantité: 100 sq ft
└── AV003155 (MP) - Quantité: 0.4 sq ft
```

**Niveau 2**: Composants des PSF (attachés correctement grâce à la colonne NAME)
```
M308000 (PSF)
└── M206100 (MP) - Quantité: 1 Pcs  ← NAME="M308000-01" dans le fichier Excel

M308001 (PSF)
└── M206100 (MP) - Quantité: 1 Pcs  ← NAME="M308001-01" dans le fichier Excel
```

**Résultat final**: Nomenclature complète
```
M505110 (Produit Fini)
├── M308000 (PSF) - Qté: 1
│   └── M206100 (MP) - Qté: 1 Pcs
├── M308001 (PSF) - Qté: 1
│   └── M206100 (MP) - Qté: 1 Pcs
├── AV003253 (MP) - Qté: 100 sq ft
└── AV003155 (MP) - Qté: 0.4 sq ft
```

## 🚀 Utilisation

### Étape 1: Accéder à la fonctionnalité

1. Connectez-vous à l'application
2. Naviguez vers une **Zone**
3. Sélectionnez ou créez un **Projet**
4. Cliquez sur le bouton **"📥 Importer BOM Excel"**

### Étape 2: Préparer votre fichier Excel

Assurez-vous que votre fichier contient:
- ✅ Les 6 colonnes requises (ParentItem, ChildItem, NAME, BOMQTY, UNITID, Level)
- ✅ Des données cohérentes (pas de lignes vides dans les colonnes principales)
- ✅ Des niveaux corrects (1 pour les composants directs, 2 pour les sous-composants, etc.)

### Étape 3: Importer le fichier

1. Cliquez sur **"Choisir un fichier"**
2. Sélectionnez votre fichier Excel (.xlsx ou .xls)
3. Cliquez sur **"Importer"**

### Étape 4: Vérifier les résultats

Après l'importation, vous verrez un message de confirmation indiquant:
- ✅ Nombre de produits finis créés
- ✅ Nombre de PSF créés
- ✅ Nombre de matières premières créées
- ✅ Nombre d'assemblages créés

## 📈 Exemple concret

### Fichier Excel d'entrée (4 produits finis)

```
M505110, M505111, M505115, M505116
```

Chaque produit fini a:
- 2-4 composants de niveau 1 (PSF ou MP)
- Certains PSF ont des composants de niveau 2 (MP)

### Résultat après importation

```
✅ Importation réussie!
   - 4 produits finis créés
   - 6 produits semi-finis créés
   - 12 matières premières créées
   - 8 assemblages créés
```

## ⚠️ Points importants

### Gestion des doublons

- Le système vérifie si un produit existe déjà avant de le créer
- Si un produit avec la même référence existe dans le projet, il est réutilisé
- Pas de duplication des données

### Niveaux de nomenclature

- **Niveau 1**: Composants directs du produit fini
- **Niveau 2**: Composants des PSF de niveau 1
- **Niveau 3+**: Composants des PSF de niveau 2, etc.

### Unités de mesure supportées

- EA (Each - Pièce)
- Pcs (Pieces)
- sq ft (Square feet)
- m2 (Mètres carrés)
- kg, g, L, mL, etc.

## 🔧 Dépannage

### Erreur: "Colonnes manquantes"

**Cause**: Le fichier Excel ne contient pas toutes les colonnes requises

**Solution**: Vérifiez que votre fichier contient exactement ces colonnes:
- ParentItem
- ChildItem
- NAME
- BOMQTY
- UNITID
- Level

### Erreur: "Produit déjà existant"

**Cause**: Un produit avec la même référence existe déjà dans le projet

**Solution**: 
- Supprimez l'ancien produit si vous voulez le remplacer
- Ou modifiez la référence dans le fichier Excel

### Importation partielle

**Cause**: Certaines lignes du fichier Excel ont des données manquantes

**Solution**: Le système ignore les lignes avec des données manquantes dans ParentItem ou ChildItem. Vérifiez votre fichier Excel pour des cellules vides.

## 📝 Générer un fichier Excel exemple

Utilisez le script Python fourni pour générer un fichier exemple:

```bash
python exemple_bom_import.py
```

Cela créera un fichier `exemple_bom.xlsx` que vous pouvez utiliser comme modèle.

## 🎓 Avantages de cette fonctionnalité

1. **Gain de temps**: Importez des centaines de produits en quelques secondes
2. **Précision**: Évitez les erreurs de saisie manuelle
3. **Traçabilité**: Conservez votre fichier Excel comme documentation
4. **Flexibilité**: Supporte des nomenclatures multi-niveaux complexes
5. **Réutilisabilité**: Importez plusieurs fois dans différents projets

## 📞 Support

Pour toute question ou problème, consultez la documentation de l'application ou contactez l'administrateur système.
