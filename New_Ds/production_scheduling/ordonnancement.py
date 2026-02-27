import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class ProductionScheduler:
    def __init__(self, shift_duration_hours=7.5):
        self.shift_duration = shift_duration_hours
        self.items_data = {}
        self.weekly_demands = {}
        self.due_dates = {}
        self.cycle_times = {}
        self.efficiencies = {}
        self.daily_capacities = {}
        
    def add_item(self, item_code, weekly_demand, daily_capacity_1shift, 
                 cycle_time, efficiency=1.0, due_date_priority=None):
        """
        Ajouter un article avec ses paramètres
        
        Parameters:
        - item_code: Code de l'article (ex: M400200)
        - weekly_demand: Besoin hebdomadaire (quantité)
        - daily_capacity_1shift: Capacité journalière pour 1 shift
        - cycle_time: Temps de cycle actuel (en heures)
        - efficiency: Efficience moyenne (0-1)
        - due_date_priority: Priorité de date d'échéance (plus petit = plus urgent)
        """
        self.items_data[item_code] = {
            'weekly_demand': weekly_demand,
            'daily_capacity_1shift': daily_capacity_1shift,
            'cycle_time': cycle_time,
            'efficiency': efficiency,
            'due_date_priority': due_date_priority if due_date_priority else 999
        }
        
    def calculate_load(self, item_code):
        """
        Calculer la charge en heures pour un article
        Charge = (Quantité demandée * Cycle Time) / Efficience
        """
        item = self.items_data[item_code]
        quantity = item['weekly_demand']
        cycle_time = item['cycle_time']
        efficiency = item['efficiency'] if item['efficiency'] > 0 else 1.0
        
        load_hours = (quantity * cycle_time) / efficiency
        return load_hours
    
    def calculate_required_shifts(self, item_code):
        """
        Calculer le nombre de shifts nécessaires pour produire la quantité demandée
        Nombre de shifts = Charge (heures) / Durée d'un shift (7.5h)
        """
        load_hours = self.calculate_load(item_code)
        required_shifts = load_hours / self.shift_duration
        return required_shifts
    
    def calculate_production_days(self, item_code):
        """
        Calculer le nombre de jours nécessaires basé sur la capacité journalière
        """
        item = self.items_data[item_code]
        quantity = item['weekly_demand']
        daily_capacity = item['daily_capacity_1shift']
        
        if daily_capacity > 0:
            days_needed = quantity / daily_capacity
        else:
            days_needed = 0
            
        return days_needed
    
    def prioritize_items(self):
        """
        Prioriser les articles selon:
        1. EDD (Earliest Due Date) - priorité principale
        2. Nombre de shifts nécessaires (plus grand = plus prioritaire)
        """
        priority_list = []
        
        for item_code in self.items_data.keys():
            item = self.items_data[item_code]
            required_shifts = self.calculate_required_shifts(item_code)
            load_hours = self.calculate_load(item_code)
            due_date_priority = item['due_date_priority']
            
            priority_list.append({
                'item_code': item_code,
                'weekly_demand': item['weekly_demand'],
                'daily_capacity_1shift': item['daily_capacity_1shift'],
                'cycle_time': item['cycle_time'],
                'efficiency': item['efficiency'],
                'load_hours': load_hours,
                'required_shifts': required_shifts,
                'due_date_priority': due_date_priority,
                'production_days': self.calculate_production_days(item_code)
            })
        
        # Trier par: 1) EDD (priorité plus petite d'abord), 2) Nombre de shifts (plus grand d'abord)
        priority_list.sort(key=lambda x: (x['due_date_priority'], -x['required_shifts']))
        
        return priority_list
    
    def generate_schedule(self, start_date=None):
        """
        Générer le planning d'ordonnancement
        """
        if start_date is None:
            start_date = datetime.now()
        
        prioritized_items = self.prioritize_items()
        
        schedule = []
        current_date = start_date
        cumulative_shifts = 0
        
        for item in prioritized_items:
            item_code = item['item_code']
            quantity = item['weekly_demand']
            required_shifts = item['required_shifts']
            load_hours = item['load_hours']
            
            # Calculer combien de shifts complets et partiels
            full_shifts = int(required_shifts)
            partial_shift_hours = (required_shifts - full_shifts) * self.shift_duration
            
            schedule_entry = {
                'Rang': len(schedule) + 1,
                'Item': item_code,
                'Quantité': quantity,
                'Capacité/shift': item['daily_capacity_1shift'],
                'Cycle Time (h)': item['cycle_time'],
                'Efficience': item['efficiency'],
                'Charge (heures)': round(load_hours, 2),
                'Shifts nécessaires': round(required_shifts, 2),
                'Priorité EDD': item['due_date_priority'],
                'Date début': current_date.strftime('%Y-%m-%d'),
                'Shifts complets': full_shifts,
                'Shift partiel (h)': round(partial_shift_hours, 2) if partial_shift_hours > 0 else 0
            }
            
            schedule.append(schedule_entry)
            
            # Avancer la date pour le prochain article
            # Supposer qu'on peut faire 2-3 shifts par jour
            days_for_this_item = np.ceil(required_shifts / 2)  # 2 shifts par jour en moyenne
            current_date += timedelta(days=days_for_this_item)
            cumulative_shifts += required_shifts
        
        return pd.DataFrame(schedule)
    
    def generate_detailed_schedule(self):
        """
        Générer un planning détaillé avec répartition par shift et par jour
        """
        prioritized_items = self.prioritize_items()
        
        detailed_schedule = []
        shift_counter = 1
        day_counter = 1
        
        for item in prioritized_items:
            item_code = item['item_code']
            quantity = item['weekly_demand']
            required_shifts = item['required_shifts']
            daily_capacity = item['daily_capacity_1shift']
            
            remaining_quantity = quantity
            shifts_allocated = 0
            
            while remaining_quantity > 0 and shifts_allocated < required_shifts:
                # Quantité à produire dans ce shift
                qty_this_shift = min(daily_capacity, remaining_quantity)
                
                detailed_schedule.append({
                    'Jour': day_counter,
                    'Shift': shift_counter,
                    'Item': item_code,
                    'Quantité à produire': qty_this_shift,
                    'Quantité restante': remaining_quantity - qty_this_shift,
                    'Priorité EDD': item['due_date_priority']
                })
                
                remaining_quantity -= qty_this_shift
                shifts_allocated += 1
                shift_counter += 1
                
                # Après 2 shifts, passer au jour suivant
                if shift_counter % 3 == 1:
                    day_counter += 1
        
        return pd.DataFrame(detailed_schedule)
    
    def print_summary(self):
        """
        Afficher un résumé du planning
        """
        prioritized_items = self.prioritize_items()
        
        total_load = sum([item['load_hours'] for item in prioritized_items])
        total_shifts = sum([item['required_shifts'] for item in prioritized_items])
        total_quantity = sum([item['weekly_demand'] for item in prioritized_items])
        
        print("=" * 80)
        print("RÉSUMÉ DU PLANNING DE PRODUCTION")
        print("=" * 80)
        print(f"Nombre total d'articles: {len(prioritized_items)}")
        print(f"Quantité totale à produire: {total_quantity}")
        print(f"Charge totale (heures): {total_load:.2f} heures")
        print(f"Shifts totaux nécessaires: {total_shifts:.2f} shifts")
        print(f"Durée d'un shift: {self.shift_duration} heures")
        print(f"Jours de production estimés (2 shifts/jour): {np.ceil(total_shifts/2):.0f} jours")
        print("=" * 80)


# DONNÉES D'ENTRÉE BASÉES SUR VOS IMAGES
def main():
    # Créer l'instance du scheduler
    scheduler = ProductionScheduler(shift_duration_hours=7.5)
    
    # Données de l'image 2 et 3
    # Format: (item_code, weekly_demand, daily_capacity_1shift, cycle_time, efficiency, due_date_priority)
    
    items_input = [
        # Item, Besoin semaine, Daily Capacity 1shift, Cycle Time, Efficiency, Due Date Priority
        ('M400200', 10, 2, 2.0, 1.0, 1),  # Lundi - priorité 1
        ('M400201', 13, 2, 4.95, 1.0, 1),  # Lundi - priorité 1
        ('M400228', 27, 3, 5.2, 1.0, 1),  # Lundi - priorité 1
        ('M400229', 27, 3, 5.2, 1.0, 1),  # Lundi - priorité 1
        
        ('M500309', 1, 20, 2.85, 1.0, 2),  # Mardi - priorité 2
        ('M400200', 3, 2, 2.0, 1.0, 2),  # Mardi - priorité 2
        ('M400201', 3, 2, 4.95, 1.0, 2),  # Mardi - priorité 2
        ('M400228', 2, 3, 5.2, 1.0, 2),  # Mardi - priorité 2
        ('M400229', 2, 3, 5.2, 1.0, 2),  # Mardi - priorité 2
        ('M500325', 6, 4, 2.25, 1.0, 2),  # Mardi - priorité 2
        ('M500316', 15, 8, 2.25, 1.0, 2),  # Mardi - priorité 2
        ('M500304', 8, 6, 2.25, 1.0, 2),  # Mardi - priorité 2
        
        ('M502026', 1, 8, 2.25, 1.0, 3),  # Mercredi - priorité 3
        ('M400200', 3, 2, 2.0, 1.0, 3),  # Mercredi - priorité 3
        ('M400201', 3, 2, 4.95, 1.0, 3),  # Mercredi - priorité 3
        ('M400228', 2, 3, 5.2, 1.0, 3),  # Mercredi - priorité 3
        ('M400229', 2, 3, 5.2, 1.0, 3),  # Mercredi - priorité 3
        ('M500325', 6, 4, 2.25, 1.0, 3),  # Mercredi - priorité 3
        ('M500324', 13, 10, 1.95, 1.0, 3),  # Mercredi - priorité 3
        ('M500304', 8, 6, 2.25, 1.0, 3),  # Mercredi - priorité 3
        ('M500319', 15, 10, 1.95, 1.0, 3),  # Mercredi - priorité 3
        
        ('M502239', 4, 8, 2.85, 1.0, 4),  # Jeudi - priorité 4
        ('M400200', 3, 2, 2.0, 1.0, 4),  # Jeudi - priorité 4
        ('M400201', 3, 2, 4.95, 1.0, 4),  # Jeudi - priorité 4
        ('M400228', 2, 3, 5.2, 1.0, 4),  # Jeudi - priorité 4
        ('M400229', 2, 3, 5.2, 1.0, 4),  # Jeudi - priorité 4
        ('M500325', 8, 4, 2.25, 1.0, 4),  # Jeudi - priorité 4
        ('M500317', 7, 5, 2.25, 1.0, 4),  # Jeudi - priorité 4
        ('M500329', 4, 8, 2.7, 1.0, 4),  # Jeudi - priorité 4
        ('M500318', 4, 10, 1.95, 1.0, 4),  # Jeudi - priorité 4
        
        ('M500327', 6, 4, 5.2, 1.0, 5),  # Vendredi - priorité 5
        ('M500327', 6, 4, 5.2, 1.0, 5),  # Vendredi - priorité 5
        ('M400228', 2, 3, 5.2, 1.0, 5),  # Vendredi - priorité 5
        ('M500328', 1, 4, 2.25, 1.0, 5),  # Vendredi - priorité 5
        ('M500324', 19, 10, 1.95, 1.0, 5),  # Vendredi - priorité 5
        ('M500328', 8, 4, 2.25, 1.0, 5),  # Vendredi - priorité 5
        ('M500317', 7, 5, 2.25, 1.0, 5),  # Vendredi - priorité 5
        ('M500311', 6, 5, 5.2, 1.0, 5),  # Vendredi - priorité 5
    ]
    
    # Agréger les demandes par item (car certains items apparaissent plusieurs fois)
    aggregated_items = {}
    for item_code, demand, capacity, cycle_time, efficiency, priority in items_input:
        if item_code not in aggregated_items:
            aggregated_items[item_code] = {
                'total_demand': demand,
                'capacity': capacity,
                'cycle_time': cycle_time,
                'efficiency': efficiency,
                'min_priority': priority
            }
        else:
            aggregated_items[item_code]['total_demand'] += demand
            aggregated_items[item_code]['min_priority'] = min(aggregated_items[item_code]['min_priority'], priority)
    
    # Ajouter les items au scheduler
    for item_code, data in aggregated_items.items():
        scheduler.add_item(
            item_code=item_code,
            weekly_demand=data['total_demand'],
            daily_capacity_1shift=data['capacity'],
            cycle_time=data['cycle_time'],
            efficiency=data['efficiency'],
            due_date_priority=data['min_priority']
        )
    
    # Afficher le résumé
    scheduler.print_summary()
    
    # Générer le planning principal
    print("\n")
    print("=" * 80)
    print("PLANNING D'ORDONNANCEMENT (SÉQUENCE DE PRODUCTION)")
    print("=" * 80)
    schedule_df = scheduler.generate_schedule()
    print(schedule_df.to_string(index=False))
    
    # Générer le planning détaillé par shift
    print("\n")
    print("=" * 80)
    print("PLANNING DÉTAILLÉ PAR SHIFT")
    print("=" * 80)
    detailed_df = scheduler.generate_detailed_schedule()
    print(detailed_df.head(30).to_string(index=False))
    print(f"\n... ({len(detailed_df)} lignes au total)")
    
    # Sauvegarder en Excel avec plusieurs feuilles
    with pd.ExcelWriter('planning_ordonnancement.xlsx', engine='openpyxl') as writer:
        schedule_df.to_excel(writer, sheet_name='Séquence Production', index=False)
        detailed_df.to_excel(writer, sheet_name='Planning Détaillé', index=False)
    print("\n✓ Planning sauvegardé dans 'planning_ordonnancement.xlsx'")
    print("  - Feuille 1: Séquence Production")
    print("  - Feuille 2: Planning Détaillé")
    
    # Calcul de l'adhérence au planning
    total_shifts_needed = schedule_df['Shifts nécessaires'].sum()
    working_days_available = 5  # 5 jours dans la semaine
    shifts_per_day = 2  # Capacité moyenne
    total_shifts_available = working_days_available * shifts_per_day
    
    adherence = min(100, (total_shifts_available / total_shifts_needed) * 100)
    
    print("\n")
    print("=" * 80)
    print("ANALYSE D'ADHÉRENCE AU PLANNING")
    print("=" * 80)
    print(f"Shifts nécessaires: {total_shifts_needed:.2f}")
    print(f"Shifts disponibles (5 jours × 2 shifts): {total_shifts_available}")
    print(f"Adhérence au planning: {adherence:.1f}%")
    
    if adherence < 100:
        print(f"\n⚠ ATTENTION: Capacité insuffisante!")
        print(f"   Il manque {total_shifts_needed - total_shifts_available:.2f} shifts")
        print(f"   Solutions: Heures supplémentaires ou étaler sur plus de jours")
    else:
        print(f"\n✓ Capacité suffisante pour atteindre 100% d'adhérence")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
