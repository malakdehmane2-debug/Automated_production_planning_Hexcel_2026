"""
Script pour générer un fichier Excel exemple complet pour l'importation des OF
Avec tous les attributs du système
"""

import pandas as pd
from datetime import datetime, timedelta

# Date de départ
date_debut = datetime(2026, 3, 25)

# Créer des données exemple complètes pour les OF
data = {
    # Colonnes obligatoires de base
    'Production': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
    'Item_number': ['M505110', 'M505111', 'M505115', 'M505116', 'M505110'],
    'Name': ['Bracket Assembly', 'Support Frame', 'Mounting Plate', 'Connector Block', 'Bracket Assembly'],
    'Quantity': [100, 150, 200, 120, 80],
    'Unit': ['EA', 'EA', 'EA', 'EA', 'EA'],
    
    # Dates
    'Created_date_and_time': [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ],
    'Original_scheduled_start_date': [
        (date_debut + timedelta(days=1)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=1)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=2)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=2)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=3)).strftime('%Y-%m-%d')
    ],
    'Original_scheduled_end_date': [
        (date_debut + timedelta(days=5)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=6)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=7)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=8)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=9)).strftime('%Y-%m-%d')
    ],
    'End_date': [
        (date_debut + timedelta(days=5)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=6)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=7)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=8)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=9)).strftime('%Y-%m-%d')
    ],
    'Delivery': [
        (date_debut + timedelta(days=5)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=6)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=7)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=8)).strftime('%Y-%m-%d'),
        (date_debut + timedelta(days=9)).strftime('%Y-%m-%d')
    ],
    
    # Statuts
    'Status': ['Scheduled', 'Scheduled', 'Scheduled', 'Scheduled', 'Scheduled'],
    'Remain_status': ['', '', '', '', ''],
    'Quality_order_status': ['', '', '', '', ''],
    
    # Planification
    'Master_plan': ['PLAN-2026-Q1', 'PLAN-2026-Q1', 'PLAN-2026-Q1', 'PLAN-2026-Q1', 'PLAN-2026-Q1'],
    'Master_production_line': ['LINE-A', 'LINE-A', 'LINE-B', 'LINE-B', 'LINE-A'],
    'Production_group': ['GROUP-1', 'GROUP-1', 'GROUP-2', 'GROUP-2', 'GROUP-1'],
    'Pool': ['POOL-A', 'POOL-A', 'POOL-B', 'POOL-B', 'POOL-A'],
    'Locked_for_rescheduling': ['No', 'No', 'No', 'No', 'No'],
    
    # Priorité (1=Lundi=Urgent, 5=Vendredi)
    'Priority_EDD': [1, 1, 2, 2, 3],
    'Priority_reason': ['Customer urgent', 'Customer urgent', 'Standard', 'Standard', 'Standard'],
    
    # Informations techniques pour ordonnancement
    'Temps_cycle': [0.5, 0.6, 0.4, 0.55, 0.5],
    'Capacite_operateur': [20, 18, 25, 22, 20],
    'Efficience': [1.0, 0.95, 0.90, 0.85, 1.0],
    
    # Autres attributs
    'Property': ['Standard', 'Standard', 'Standard', 'Standard', 'Standard'],
    'Reported_as_finished': [0, 0, 0, 0, 0],
    'Report_remainder_as_finished': ['No', 'No', 'No', 'No', 'No'],
    'Reference_type': ['Production', 'Production', 'Production', 'Production', 'Production'],
    'Created_by': ['Admin', 'Admin', 'Admin', 'Admin', 'Admin'],
    'Regrade': ['', '', '', '', ''],
    'Category': ['Assembly', 'Assembly', 'Fabrication', 'Fabrication', 'Assembly'],
    'Commentaire': ['', '', '', '', '']
}

df = pd.DataFrame(data)

# Sauvegarder en Excel avec formatage
filename = 'EXEMPLE_IMPORT_OF_COMPLET.xlsx'

with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='OF_Import', index=False)
    
    # Ajouter une feuille avec les instructions
    instructions = pd.DataFrame({
        'Colonne': [
            'Production', 'Item_number', 'Name', 'Quantity', 'Unit',
            'Original_scheduled_start_date', 'Original_scheduled_end_date',
            'End_date', 'Delivery', 'Status', 'Master_plan',
            'Master_production_line', 'Production_group', 'Priority_EDD',
            'Temps_cycle', 'Capacite_operateur', 'Efficience'
        ],
        'Description': [
            'Numéro de production (unique)',
            'Code du produit (doit exister dans le projet)',
            'Nom du produit',
            'Quantité à produire',
            'Unité (EA, KG, M, etc.)',
            'Date de début planifiée (YYYY-MM-DD)',
            'Date de fin planifiée (YYYY-MM-DD)',
            'Date de fin (YYYY-MM-DD)',
            'Date de livraison (YYYY-MM-DD)',
            'Statut (Scheduled, Started, Finished, etc.)',
            'Plan directeur',
            'Ligne de production principale',
            'Groupe de production',
            'Priorité EDD (1=Lundi urgent, 5=Vendredi)',
            'Temps de cycle en heures par unité',
            'Capacité par opérateur (unités/shift)',
            'Efficience (0.0 à 1.0, ex: 0.85 = 85%)'
        ],
        'Obligatoire': [
            'Oui', 'Oui', 'Non', 'Oui', 'Non',
            'Oui', 'Oui', 'Oui', 'Non', 'Non',
            'Non', 'Non', 'Non', 'Oui',
            'Oui', 'Oui', 'Non'
        ]
    })
    instructions.to_excel(writer, sheet_name='Instructions', index=False)

print(f"✅ Fichier {filename} créé avec succès!")
print(f"\n📊 Contenu:")
print(f"   - Nombre d'OF: {len(df)}")
print(f"   - Colonnes: {len(df.columns)}")
print(f"\n📋 Colonnes incluses:")
for col in df.columns:
    print(f"   - {col}")
print(f"\n💡 Instructions:")
print("   1. Le fichier contient 2 feuilles:")
print("      - OF_Import: Données exemple à importer")
print("      - Instructions: Description de chaque colonne")
print("   2. Assurez-vous que les produits existent dans votre projet")
print("   3. Importez via: Dashboard → Projet BF → Module OF → Importer Excel")
print(f"\n📝 Colonnes obligatoires minimales:")
print("   - Production (numéro unique)")
print("   - Item_number (code produit)")
print("   - Quantity")
print("   - Original_scheduled_start_date")
print("   - Original_scheduled_end_date")
print("   - End_date")
print("   - Priority_EDD (1-5)")
print("   - Temps_cycle")
print("   - Capacite_operateur")
