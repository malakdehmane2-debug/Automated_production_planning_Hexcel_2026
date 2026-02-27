"""
Exemple d'utilisation du système d'ordonnancement avec gestion des absences
"""

import sys
sys.path.append('.')
from ordonnancement_operateurs import OperatorScheduler

def main():
    print("=" * 100)
    print("EXEMPLE: ORDONNANCEMENT AVEC ABSENCES D'OPÉRATEURS")
    print("=" * 100)
    
    # Créer l'instance
    scheduler = OperatorScheduler(shift_duration_hours=7.5, shifts_per_day=3)
    
    # ===== AJOUTER LES ARTICLES =====
    print("\n📦 Ajout des articles...")
    articles = [
        ('M400200', 10, 2, 2.0, 1.0, 1),
        ('M400201', 13, 2, 4.95, 1.0, 1),
        ('M400228', 27, 3, 5.2, 1.0, 1),
    ]
    
    for item_code, demand, capacity, cycle_time, efficiency, priority in articles:
        scheduler.add_item(item_code, demand, capacity, cycle_time, efficiency, priority)
    
    print(f"   ✓ {len(articles)} articles ajoutés")
    
    # ===== AJOUTER LES OPÉRATEURS =====
    print("\n👷 Ajout des opérateurs...")
    
    all_items = ['M400200', 'M400201', 'M400228']
    
    scheduler.add_operator('OP1', all_items, efficiency=1.00)
    scheduler.add_operator('OP2', all_items, efficiency=0.95)
    scheduler.add_operator('OP3', all_items, efficiency=0.90)
    scheduler.add_operator('OP4', all_items, efficiency=0.85)
    scheduler.add_operator('OP5', all_items, efficiency=0.80)
    scheduler.add_operator('OP6', all_items, efficiency=0.75)
    scheduler.add_operator('OP7', all_items, efficiency=0.70)
    scheduler.add_operator('OP8', all_items, efficiency=0.65)
    scheduler.add_operator('OP9', all_items, efficiency=0.60)
    scheduler.add_operator('OP10', all_items, efficiency=1.00)
    
    print(f"   ✓ {len(scheduler.operators)} opérateurs ajoutés")
    
    # ===== CONFIGURER LES ABSENCES =====
    # Shift 1 (Matin): 8 opérateurs normalement, 2 absents → 6 disponibles
    # Shift 2 (Soir): 9 opérateurs normalement, 1 absent → 8 disponibles
    # Shift 3 (Nuit): 10 opérateurs normalement, 0 absent → 10 disponibles
    scheduler.set_absences({1: 2, 2: 1, 3: 0})
    
    # ===== ORDONNANCEMENT MÉTHODE 1 =====
    print("\n\n")
    print("=" * 100)
    print("MÉTHODE 1: ORDONNANCEMENT AVEC ABSENCES")
    print("=" * 100)
    
    df_planning, df_workload = scheduler.schedule_with_fixed_operators()
    
    print("\n📋 Planning (premiers 20 shifts):")
    print(df_planning.head(20).to_string(index=False))
    
    print(f"\n... Total: {len(df_planning)} assignations")
    
    # Vérifier les objectifs
    produced = df_planning.groupby('Item')['Quantité'].sum()
    print("\n📊 Production vs Objectifs:")
    for item_code, demand, _, _, _, _ in articles:
        prod = produced.get(item_code, 0)
        print(f"   {item_code}: {prod}/{demand} unités ({prod/demand*100:.1f}%)")

if __name__ == "__main__":
    main()
