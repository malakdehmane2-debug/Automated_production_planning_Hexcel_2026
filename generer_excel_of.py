"""
Script pour générer un fichier Excel exemple pour l'importation des OF
À exécuter avec: python generer_excel_of.py
"""

import pandas as pd
from datetime import datetime, timedelta

# Date de départ
date_debut = datetime(2026, 3, 25)

# Créer des données exemple pour les OF
data = {
    'Produit': [
        'M505110', 'M505111', 'M505115', 'M505116',
        'M505110', 'M505111', 'M505115'
    ],
    'Quantite': [
        100, 150, 200, 120,
        80, 100, 150
    ],
    'DateLancement': [
        (date_debut + timedelta(days=1)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=1)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=2)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=2)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=3)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=3)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=4)).strftime('%Y-%m-%d')
    ],
    'DateLivraison': [
        (date_debut + timedelta(days=5)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=6)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=7)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=8)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=9)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=10)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=11)).strftime('%Y-%m-%d')
    ],
    'PrioriteEDD': [
        1,  # Lundi - Urgent
        1,  # Lundi - Urgent
        2,  # Mardi
        2,  # Mardi
        3,  # Mercredi
        4,  # Jeudi
        5   # Vendredi
    ],
    'TempsCycle': [
        0.5, 0.6, 0.4, 0.55,
        0.5, 0.6, 0.4
    ],
    'CapaciteOperateur': [
        20, 18, 25, 22,
        20, 18, 25
    ]
}

df = pd.DataFrame(data)

# Sauvegarder en Excel
filename = 'EXEMPLE_IMPORT_OF.xlsx'
df.to_excel(filename, index=False, sheet_name='OF')

print(f"✅ Fichier {filename} créé avec succès!")
print(f"\n📊 Contenu du fichier:")
print(f"   - Nombre d'OF: {len(df)}")
print(f"   - Produits uniques: {df['Produit'].nunique()}")
print(f"\n📋 Aperçu des données:")
print(df.to_string(index=False))
print(f"\n💡 Instructions d'utilisation:")
print("   1. Assurez-vous que les produits (M505110, M505111, etc.) existent dans votre projet")
print("   2. Allez dans: Dashboard → Sélectionner projet BF → Module OF → Importer Excel")
print("   3. Uploadez le fichier EXEMPLE_IMPORT_OF.xlsx")
print("   4. Les OF seront créés automatiquement")
print(f"\n📝 Format des colonnes:")
print("   - Produit: Code du produit (doit exister dans le projet)")
print("   - Quantite: Nombre d'unités à produire")
print("   - DateLancement: Date de début (YYYY-MM-DD)")
print("   - DateLivraison: Date limite (YYYY-MM-DD)")
print("   - PrioriteEDD: 1=Lundi (urgent) à 5=Vendredi")
print("   - TempsCycle: Temps pour produire 1 unité (en heures)")
print("   - CapaciteOperateur: Unités qu'un opérateur peut faire par shift")
