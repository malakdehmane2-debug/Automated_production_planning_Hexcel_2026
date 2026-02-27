from ordonnancement_operateurs import OperatorScheduler
import pandas as pd

def visualiser_shift_par_shift():
    """
    Créer une visualisation claire de qui fait quoi dans chaque shift
    """
    print("=" * 100)
    print("EXEMPLE DE VISUALISATION - QUI FAIT QUOI DANS CHAQUE SHIFT")
    print("=" * 100)
    
    # Créer un petit exemple
    scheduler = OperatorScheduler(shift_duration_hours=7.5, shifts_per_day=3)
    
    # Ajouter quelques articles
    scheduler.add_item('M400200', weekly_demand=20, capacity_per_operator_per_shift=2, 
                       cycle_time=2.0, efficiency=1.0, due_date_priority=1)
    scheduler.add_item('M400228', weekly_demand=30, capacity_per_operator_per_shift=3, 
                       cycle_time=5.2, efficiency=1.0, due_date_priority=1)
    scheduler.add_item('M500324', weekly_demand=25, capacity_per_operator_per_shift=10, 
                       cycle_time=1.95, efficiency=1.0, due_date_priority=2)
    
    # Ajouter 5 opérateurs
    scheduler.add_operator('OP1', ['M400200', 'M400228'])
    scheduler.add_operator('OP2', ['M400200', 'M400228'])
    scheduler.add_operator('OP3', ['M400228'])
    scheduler.add_operator('OP4', ['M500324'])
    scheduler.add_operator('OP5', ['M500324'])
    
    # Générer le planning
    schedule = scheduler.schedule_with_fixed_operators()
    
    # Afficher shift par shift
    for day in sorted(schedule['Jour'].unique()):
        print(f"\n{'='*100}")
        print(f"JOUR {day}")
        print(f"{'='*100}")
        
        day_data = schedule[schedule['Jour'] == day]
        
        for shift_num in sorted(day_data['Shift'].unique()):
            shift_data = day_data[day_data['Shift'] == shift_num]
            
            print(f"\n  📅 SHIFT {shift_num}:")
            print(f"  {'-'*96}")
            
            # Grouper par opérateur
            for _, row in shift_data.iterrows():
                print(f"  👤 {row['Opérateur']:8} → produit {row['Item']:10} × {row['Quantité']:3.0f} unités")
            
            # Résumé du shift
            total_qty = shift_data['Quantité'].sum()
            items_produced = shift_data['Item'].unique()
            print(f"  {'-'*96}")
            print(f"  📊 Total shift: {total_qty:.0f} unités | Articles: {', '.join(items_produced)}")
    
    print(f"\n{'='*100}")
    print("RÉSUMÉ GLOBAL")
    print(f"{'='*100}")
    
    # Statistiques par opérateur
    op_stats = schedule.groupby('Opérateur').agg({
        'Quantité': 'sum',
        'Shift': 'count'
    }).rename(columns={'Shift': 'Nombre de shifts'})
    
    print("\n📊 Production par opérateur:")
    for op, row in op_stats.iterrows():
        print(f"  {op}: {row['Quantité']:.0f} unités en {row['Nombre de shifts']:.0f} shifts")
    
    # Statistiques par article
    item_stats = schedule.groupby('Item')['Quantité'].sum()
    print("\n📦 Production par article:")
    for item, qty in item_stats.items():
        print(f"  {item}: {qty:.0f} unités")
    
    print(f"\n{'='*100}")
    
    # Sauvegarder
    schedule.to_excel('exemple_visualisation.xlsx', index=False)
    print("\n✓ Sauvegardé dans 'exemple_visualisation.xlsx'")


def exemple_11_operateurs():
    """
    Exemple avec 11 opérateurs comme mentionné par l'utilisateur
    """
    print("\n\n")
    print("=" * 100)
    print("EXEMPLE AVEC 11 OPÉRATEURS")
    print("=" * 100)
    
    scheduler = OperatorScheduler(shift_duration_hours=7.5, shifts_per_day=3)
    
    # Ajouter quelques articles
    scheduler.add_item('M400200', weekly_demand=50, capacity_per_operator_per_shift=2, 
                       cycle_time=2.0, efficiency=1.0, due_date_priority=1)
    scheduler.add_item('M400228', weekly_demand=60, capacity_per_operator_per_shift=3, 
                       cycle_time=5.2, efficiency=1.0, due_date_priority=1)
    
    # Ajouter 11 opérateurs
    for i in range(1, 12):
        if i <= 6:
            # 6 premiers opérateurs peuvent faire M400200 et M400228
            scheduler.add_operator(f'OP{i}', ['M400200', 'M400228'])
        else:
            # 5 derniers opérateurs peuvent faire seulement M400228
            scheduler.add_operator(f'OP{i}', ['M400228'])
    
    print(f"\n✓ {len(scheduler.operators)} opérateurs configurés")
    
    # Générer le planning
    schedule = scheduler.schedule_with_fixed_operators()
    
    # Afficher les premiers shifts
    print("\n📋 Aperçu des premiers shifts:")
    print("-" * 100)
    
    for day in [1, 2]:
        day_data = schedule[schedule['Jour'] == day]
        
        for shift_num in sorted(day_data['Shift'].unique())[:2]:  # 2 premiers shifts
            shift_data = day_data[day_data['Shift'] == shift_num]
            
            print(f"\nJour {day}, Shift {shift_num}:")
            print(f"  Nombre d'opérateurs actifs: {len(shift_data)}")
            
            # Compter par article
            items_count = shift_data.groupby('Item')['Quantité'].agg(['count', 'sum'])
            for item, row in items_count.iterrows():
                print(f"  - {item}: {row['count']:.0f} opérateurs produisent {row['sum']:.0f} unités")
    
    print("\n" + "=" * 100)
    print("STATISTIQUES GLOBALES")
    print("=" * 100)
    
    total_shifts = len(schedule['Shift'].unique()) + (schedule['Jour'].max() - 1) * 3
    print(f"\nDurée totale: {schedule['Jour'].max()} jours")
    print(f"Nombre de shifts utilisés: {total_shifts}")
    print(f"Total d'assignations: {len(schedule)}")
    
    # Charge par opérateur
    op_stats = schedule.groupby('Opérateur').agg({
        'Quantité': 'sum',
        'Shift': 'count'
    }).rename(columns={'Shift': 'Nombre de shifts'})
    
    print(f"\n📊 Charge de travail:")
    print(f"  Opérateur le plus chargé: {op_stats['Nombre de shifts'].max():.0f} shifts")
    print(f"  Opérateur le moins chargé: {op_stats['Nombre de shifts'].min():.0f} shifts")
    print(f"  Moyenne: {op_stats['Nombre de shifts'].mean():.1f} shifts")
    
    # Sauvegarder
    with pd.ExcelWriter('exemple_11_operateurs.xlsx', engine='openpyxl') as writer:
        schedule.to_excel(writer, sheet_name='Planning', index=False)
        op_stats.to_excel(writer, sheet_name='Charge par opérateur')
    
    print("\n✓ Sauvegardé dans 'exemple_11_operateurs.xlsx'")


if __name__ == "__main__":
    visualiser_shift_par_shift()
    exemple_11_operateurs()
    
    print("\n\n" + "=" * 100)
    print("EXPLICATION DU FONCTIONNEMENT")
    print("=" * 100)
    print("""
Dans chaque shift, TOUS les opérateurs travaillent en parallèle:

Exemple avec 11 opérateurs:
    
    Jour 1, Shift 1:
        OP1  → M400228 (3 unités)
        OP2  → M400228 (3 unités)
        OP3  → M400228 (3 unités)
        OP4  → M400228 (3 unités)
        OP5  → M400228 (3 unités)
        OP6  → M400228 (3 unités)
        OP7  → M400228 (3 unités)
        OP8  → M400228 (3 unités)
        OP9  → M400228 (3 unités)
        OP10 → M400228 (3 unités)
        OP11 → M400228 (3 unités)
        ────────────────────────────────
        Total: 33 unités produites en 1 shift!
    
    Jour 1, Shift 2:
        OP1  → M400228 (3 unités)
        OP2  → M400228 (3 unités)
        ... (tous les 11 opérateurs)
        ────────────────────────────────
        Total: 33 unités produites en 1 shift!
    
    Jour 1, Shift 3:
        OP1  → M400200 (2 unités)  ← Change d'article
        OP2  → M400200 (2 unités)
        ... etc

Avantage: Production très rapide grâce au travail en parallèle!
""")
    print("=" * 100)
