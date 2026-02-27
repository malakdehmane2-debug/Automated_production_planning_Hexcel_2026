from ordonnancement import ProductionScheduler
import pandas as pd

def exemple_simple():
    """
    Exemple d'utilisation simple avec quelques articles
    """
    print("=" * 80)
    print("EXEMPLE SIMPLE - 5 ARTICLES")
    print("=" * 80)
    
    scheduler = ProductionScheduler(shift_duration_hours=7.5)
    
    # Ajouter quelques articles
    scheduler.add_item('M400200', weekly_demand=10, daily_capacity_1shift=2, 
                       cycle_time=2.0, efficiency=1.0, due_date_priority=1)
    
    scheduler.add_item('M400228', weekly_demand=27, daily_capacity_1shift=3, 
                       cycle_time=5.2, efficiency=1.0, due_date_priority=1)
    
    scheduler.add_item('M500324', weekly_demand=32, daily_capacity_1shift=10, 
                       cycle_time=1.95, efficiency=1.0, due_date_priority=3)
    
    scheduler.add_item('M500327', weekly_demand=12, daily_capacity_1shift=4, 
                       cycle_time=5.2, efficiency=1.0, due_date_priority=5)
    
    scheduler.add_item('M500309', weekly_demand=1, daily_capacity_1shift=20, 
                       cycle_time=2.85, efficiency=1.0, due_date_priority=2)
    
    # Générer et afficher
    scheduler.print_summary()
    schedule = scheduler.generate_schedule()
    print("\n" + schedule.to_string(index=False))
    
    return scheduler


def exemple_avec_efficience():
    """
    Exemple avec différentes efficiences
    """
    print("\n\n")
    print("=" * 80)
    print("EXEMPLE AVEC EFFICIENCES VARIABLES")
    print("=" * 80)
    
    scheduler = ProductionScheduler(shift_duration_hours=7.5)
    
    # Articles avec différentes efficiences
    scheduler.add_item('M400200', weekly_demand=10, daily_capacity_1shift=2, 
                       cycle_time=2.0, efficiency=1.0, due_date_priority=1)
    
    scheduler.add_item('M400201', weekly_demand=13, daily_capacity_1shift=2, 
                       cycle_time=4.95, efficiency=0.85, due_date_priority=1)  # Efficience 85%
    
    scheduler.add_item('M500312', weekly_demand=16, daily_capacity_1shift=10, 
                       cycle_time=1.95, efficiency=0.70, due_date_priority=2)  # Efficience 70%
    
    scheduler.print_summary()
    schedule = scheduler.generate_schedule()
    print("\n" + schedule.to_string(index=False))
    
    print("\n📊 IMPACT DE L'EFFICIENCE:")
    print("   - M400200 (100% efficience): Charge = 10 × 2.0 / 1.0 = 20.0h")
    print("   - M400201 (85% efficience):  Charge = 13 × 4.95 / 0.85 = 75.7h")
    print("   - M500312 (70% efficience):  Charge = 16 × 1.95 / 0.70 = 44.6h")
    print("   → Plus l'efficience est basse, plus la charge augmente!")


def exemple_comparaison_priorites():
    """
    Exemple montrant l'impact des priorités EDD et des shifts
    """
    print("\n\n")
    print("=" * 80)
    print("EXEMPLE - IMPACT DES PRIORITÉS")
    print("=" * 80)
    
    scheduler = ProductionScheduler(shift_duration_hours=7.5)
    
    # Article A: Priorité EDD faible mais beaucoup de shifts
    scheduler.add_item('Article_A', weekly_demand=50, daily_capacity_1shift=5, 
                       cycle_time=3.0, efficiency=1.0, due_date_priority=5)
    
    # Article B: Priorité EDD moyenne, shifts moyens
    scheduler.add_item('Article_B', weekly_demand=20, daily_capacity_1shift=10, 
                       cycle_time=2.0, efficiency=1.0, due_date_priority=3)
    
    # Article C: Priorité EDD haute mais peu de shifts
    scheduler.add_item('Article_C', weekly_demand=5, daily_capacity_1shift=20, 
                       cycle_time=1.0, efficiency=1.0, due_date_priority=1)
    
    # Article D: Priorité EDD haute et beaucoup de shifts
    scheduler.add_item('Article_D', weekly_demand=40, daily_capacity_1shift=4, 
                       cycle_time=4.0, efficiency=1.0, due_date_priority=1)
    
    schedule = scheduler.generate_schedule()
    print("\n" + schedule[['Rang', 'Item', 'Shifts nécessaires', 'Priorité EDD']].to_string(index=False))
    
    print("\n📋 ORDRE DE PRODUCTION:")
    print("   1. Article_D: Priorité EDD=1 (urgent) + 21.33 shifts (long)")
    print("   2. Article_C: Priorité EDD=1 (urgent) + 0.67 shifts (court)")
    print("   3. Article_B: Priorité EDD=3 (moyen) + 2.67 shifts")
    print("   4. Article_A: Priorité EDD=5 (tard) + 20.00 shifts")
    print("\n   → EDD prime sur le nombre de shifts!")
    print("   → À EDD égal, on produit d'abord les articles longs")


def calculer_adherence_personnalisee():
    """
    Calculer l'adhérence avec des paramètres personnalisés
    """
    print("\n\n")
    print("=" * 80)
    print("CALCUL D'ADHÉRENCE PERSONNALISÉ")
    print("=" * 80)
    
    scheduler = ProductionScheduler(shift_duration_hours=7.5)
    
    # Ajouter des articles
    scheduler.add_item('M400228', weekly_demand=27, daily_capacity_1shift=3, 
                       cycle_time=5.2, efficiency=1.0, due_date_priority=1)
    scheduler.add_item('M400229', weekly_demand=27, daily_capacity_1shift=3, 
                       cycle_time=5.2, efficiency=1.0, due_date_priority=1)
    scheduler.add_item('M500324', weekly_demand=32, daily_capacity_1shift=10, 
                       cycle_time=1.95, efficiency=1.0, due_date_priority=3)
    
    schedule = scheduler.generate_schedule()
    total_shifts = schedule['Shifts nécessaires'].sum()
    
    print(f"\nShifts totaux nécessaires: {total_shifts:.2f}")
    print("\nSCÉNARIOS:")
    
    scenarios = [
        ("1 shift/jour × 5 jours", 1, 5),
        ("2 shifts/jour × 5 jours", 2, 5),
        ("3 shifts/jour × 5 jours", 3, 5),
        ("2 shifts/jour × 6 jours", 2, 6),
        ("2 shifts/jour × 7 jours", 2, 7),
    ]
    
    for name, shifts_per_day, days in scenarios:
        available = shifts_per_day * days
        adherence = min(100, (available / total_shifts) * 100)
        status = "✓" if adherence >= 100 else "✗"
        print(f"   {status} {name:25} = {available:2} shifts → Adhérence: {adherence:5.1f}%")


if __name__ == "__main__":
    # Exécuter tous les exemples
    exemple_simple()
    exemple_avec_efficience()
    exemple_comparaison_priorites()
    calculer_adherence_personnalisee()
    
    print("\n\n")
    print("=" * 80)
    print("✓ EXEMPLES TERMINÉS")
    print("=" * 80)
    print("\nPour utiliser avec vos propres données:")
    print("1. Créez une instance: scheduler = ProductionScheduler(shift_duration_hours=7.5)")
    print("2. Ajoutez vos articles: scheduler.add_item(...)")
    print("3. Générez le planning: schedule = scheduler.generate_schedule()")
    print("4. Sauvegardez: schedule.to_csv('mon_planning.csv')")
