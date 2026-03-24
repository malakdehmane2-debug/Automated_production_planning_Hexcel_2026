import pandas as pd

# Créer un exemple de fichier BOM basé sur l'image fournie
# IMPORTANT: Pour les niveaux 2+, la colonne NAME indique le vrai parent
# Exemple: NAME = "M308000-01" signifie que M206100 appartient à M308000

data = {
    'ParentItem': [
        'M505110', 'M505110', 'M505110', 'M505110', 'M505110', 'M505110',
        'M505111', 'M505111', 'M505111', 'M505111', 'M505111', 'M505111',
        'M505115', 'M505115', 'M505115', 'M505115', 'M505115', 'M505115', 'M505115',
        'M505116', 'M505116', 'M505116', 'M505116', 'M505116', 'M505116', 'M505116'
    ],
    'ChildItem': [
        'M308000', 'M308001', 'AV003253', 'AV003155', 'M206100', 'M206100',
        'M308000', 'M308001', 'AV003253', 'AV003155', 'M206100', 'M206100',
        'M308004', 'M308005', 'P0170V19', 'AV003253', 'AV003155', 'M206101', 'M206101',
        'M308004', 'M308005', 'P0170V19', 'AV003253', 'AV003155', 'M206101', 'M206101'
    ],
    'NAME': [
        # Niveau 1: NAME = nom du produit fini
        'M505110-01', 'M505110-01', 'M505110-01', 'M505110-01', 
        # Niveau 2: NAME = nom du PSF parent (M308000-01 signifie que M206100 appartient à M308000)
        'M308000-01', 'M308001-01',
        
        'M505111-01', 'M505111-01', 'M505111-01', 'M505111-01', 
        'M308000-01', 'M308001-01',
        
        'M505115-01', 'M505115-01', 'M505115-01', 'M505115-01', 'M505115-01', 
        'M308004-02', 'M308005-02',
        
        'M505116-01', 'M505116-01', 'M505116-01', 'M505116-01', 'M505116-01', 
        'M308004-02', 'M308005-02'
    ],
    'BOMQTY': [
        1, 1, 100, 0.4, 1, 1,
        1, 1, 100, 0.4, 1, 1,
        2, 2, 5, 100, 0.667, 1, 1,
        2, 2, 5, 100, 0.667, 1, 1
    ],
    'UNITID': [
        'EA', 'EA', 'sq ft', 'sq ft', 'Pcs', 'Pcs',
        'EA', 'EA', 'sq ft', 'sq ft', 'Pcs', 'Pcs',
        'EA', 'EA', 'm2', 'sq ft', 'sq ft', 'Pcs', 'Pcs',
        'EA', 'EA', 'm2', 'sq ft', 'sq ft', 'Pcs', 'Pcs'
    ],
    'BOMQTYSERIE': [
        1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1
    ],
    'Level': [
        1, 1, 1, 1, 2, 2,
        1, 1, 1, 1, 2, 2,
        1, 1, 1, 1, 1, 2, 2,
        1, 1, 1, 1, 1, 2, 2
    ]
}

df = pd.DataFrame(data)

# Sauvegarder en Excel
df.to_excel('exemple_bom.xlsx', index=False)
print("✅ Fichier exemple_bom.xlsx créé avec succès!")
print(f"\nNombre de lignes: {len(df)}")
print(f"Produits finis uniques: {df[df['Level']==1]['ParentItem'].nunique()}")
print(f"\n📊 Structure de la nomenclature:")
print(f"   - Niveau 1: Composants directs des produits finis")
print(f"   - Niveau 2: Composants des PSF (le parent réel est dans la colonne NAME)")
print(f"\n🔍 Exemple de lecture:")
print(f"   Ligne avec Level=2, ChildItem=M206100, NAME=M308000-01")
print(f"   → M206100 appartient à M308000 (pas à M505110)")
print(f"\nAperçu des données:")
print(df.head(10))
