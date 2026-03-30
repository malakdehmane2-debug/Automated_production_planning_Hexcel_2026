"""
Script pour générer un fichier Excel exemple pour l'importation des OF
"""

import pandas as pd
from datetime import datetime, timedelta

# Date de départ
date_debut = datetime.now()

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
filename = 'exemple_import_of.xlsx'
df.to_excel(filename, index=False)

print(f"✅ Fichier {filename} créé avec succès!")
print(f"\nNombre d'OF: {len(df)}")
print(f"Produits uniques: {df['Produit'].nunique()}")
print(f"\n📊 Répartition par priorité EDD:")
print(df['PrioriteEDD'].value_counts().sort_index())
print(f"\n📋 Aperçu des données:")
print(df.head(10).to_string(index=False))
print(f"\n💡 Instructions:")
print("1. Assurez-vous que les produits existent dans votre projet")
print("2. Importez ce fichier via: Module OF → Importer Excel")
print("3. Les OF seront créés automatiquement avec leurs paramètres")
