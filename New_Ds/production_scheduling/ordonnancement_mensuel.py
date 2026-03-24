import pandas as pd
from datetime import datetime, timedelta

class MonthlyMultiProjectScheduler:
    def __init__(self, shift_duration_hours=7.5):
        self.shift_duration = shift_duration_hours
        self.projects = {}
        self.operators = {}
        self.operator_capabilities = {}
        self.operators_per_shift = {1: 8, 2: 9, 3: 10}
        
    def add_project(self, project_name, items_data):
        """
        Ajouter un projet avec ses items et besoins mensuels
        items_data: dict avec {
            'item_code': {
                'monthly_demand': int,
                'capacity_per_operator_per_shift': int,
                'cycle_time': float,
                'due_date_priority': int,
                'capable_operators': list
            }
        }
        """
        self.projects[project_name] = items_data
        
    def add_operator(self, operator_name, capable_items, efficiency=1.0, shift=1):
        """Ajouter un opérateur avec ses capacités"""
        op_name = f"{operator_name}_S{shift}"
        
        self.operators[op_name] = {
            'base_name': operator_name,
            'capable_items': capable_items,
            'efficiency': efficiency,
            'shift': shift
        }
        
        for item in capable_items:
            if item not in self.operator_capabilities:
                self.operator_capabilities[item] = []
            self.operator_capabilities[item].append(op_name)
    
    def calculate_load(self, project_name, item_code, weekly_demand):
        """Calculer la charge en heures pour un item"""
        item = self.projects[project_name][item_code]
        cycle_time = item['cycle_time']
        load_hours = (weekly_demand * cycle_time) / 60.0
        return load_hours
    
    def calculate_required_shifts(self, project_name, item_code, weekly_demand, num_operators=1):
        """
        Calculer le nombre de shifts nécessaires
        Formule: Charge totale (heures) / (Durée shift × Nombre d'opérateurs)
        """
        load_hours = self.calculate_load(project_name, item_code, weekly_demand)
        total_hours_per_shift = self.shift_duration * num_operators
        required_shifts = load_hours / total_hours_per_shift
        return required_shifts
    
    def print_project_analysis(self):
        """Afficher l'analyse des besoins pour chaque projet"""
        print("\n" + "="*100)
        print("ANALYSE DES BESOINS PAR PROJET")
        print("="*100)
        
        for project_name, items in self.projects.items():
            print(f"\n📊 Projet: {project_name}")
            print(f"{'Item':<15} {'Demande/Mois':<15} {'Demande/Sem':<15} {'Load (h)':<12} {'Shifts Req.':<12}")
            print("-" * 80)
            
            total_monthly = 0
            total_load = 0
            total_shifts = 0
            
            for item_code, item_data in items.items():
                monthly_demand = item_data['monthly_demand']
                weekly_demand = monthly_demand // 4
                
                load = self.calculate_load(project_name, item_code, weekly_demand)
                shifts_req = self.calculate_required_shifts(project_name, item_code, weekly_demand, num_operators=1)
                
                total_monthly += monthly_demand
                total_load += load
                total_shifts += shifts_req
                
                print(f"{item_code:<15} {monthly_demand:<15} {weekly_demand:<15} {load:<12.2f} {shifts_req:<12.2f}")
            
            print("-" * 80)
            print(f"{'TOTAL':<15} {total_monthly:<15} {'':<15} {total_load:<12.2f} {total_shifts:<12.2f}")
    
    def get_rotated_shift(self, original_shift, week_num):
        """
        Calculer le shift rotatif en fonction de la semaine
        Rotation: Nuit→Matin, Soir→Nuit, Matin→Soir
        """
        rotation_map = {
            1: {1: 1, 2: 2, 3: 3},  # Semaine 1: pas de rotation
            2: {1: 2, 2: 3, 3: 1},  # Semaine 2: 1→2, 2→3, 3→1
            3: {1: 3, 2: 1, 3: 2},  # Semaine 3: 1→3, 2→1, 3→2
            4: {1: 1, 2: 2, 3: 3},  # Semaine 4: retour initial
        }
        return rotation_map[week_num][original_shift]
    
    def schedule_month(self, start_date=None):
        """Ordonnancer la production pour 4 semaines avec rotation des shifts"""
        if start_date is None:
            start_date = datetime.now()
        
        all_assignments = []
        
        # Pour chaque semaine
        for week_num in range(1, 5):
            print(f"\n{'='*100}")
            print(f"SEMAINE {week_num}")
            print(f"{'='*100}")
            
            # Préparer les items de la semaine (demande mensuelle / 4)
            weekly_items = {}
            for project_name, items in self.projects.items():
                for item_code, item_data in items.items():
                    weekly_demand = item_data['monthly_demand'] // 4
                    if item_data['monthly_demand'] % 4 > 0 and week_num <= (item_data['monthly_demand'] % 4):
                        weekly_demand += 1
                    
                    if weekly_demand > 0:
                        weekly_items[f"{project_name}_{item_code}"] = {
                            'project': project_name,
                            'item_code': item_code,
                            'weekly_demand': weekly_demand,
                            'capacity': item_data['capacity_per_operator_per_shift'],
                            'cycle_time': item_data['cycle_time'],
                            'due_date_priority': item_data['due_date_priority'],
                            'capable_operators': item_data['capable_operators']
                        }
            
            # Prioriser les items par EDD
            prioritized_items = sorted(weekly_items.values(), 
                                     key=lambda x: x['due_date_priority'])
            
            # Garder trace de ce qui reste à produire
            remaining_items = {item['item_code']: item['weekly_demand'] 
                             for item in prioritized_items}
            
            day = 1
            shift_num = 1
            week_finished = False
            
            # Ordonnancement pour cette semaine (17 shifts max)
            while any(qty > 0 for qty in remaining_items.values()) and not week_finished:
                # Déterminer le shift actuel avec rotation
                current_shift = shift_num
                
                # Opérateurs assignés dans ce shift
                assigned_operators = set()
                shift_production = {}
                
                # Parcourir les articles par ordre de priorité
                for item in prioritized_items:
                    item_code = item['item_code']
                    project_name = item['project']
                    
                    if remaining_items[item_code] <= 0:
                        continue
                    
                    # Trouver les opérateurs capables pour cet item avec rotation
                    capable_ops = []
                    for op_name in self.operator_capabilities.get(item_code, []):
                        original_shift = self.operators[op_name]['shift']
                        rotated_shift = self.get_rotated_shift(original_shift, week_num)
                        
                        if rotated_shift == current_shift and op_name not in assigned_operators:
                            capable_ops.append(op_name)
                    
                    # Trier par efficience décroissante
                    capable_ops.sort(key=lambda op: self.operators[op]['efficiency'], reverse=True)
                    
                    # Assigner les opérateurs
                    for op_name in capable_ops:
                        if op_name in assigned_operators:
                            continue
                        
                        efficiency = self.operators[op_name]['efficiency']
                        capacity = int(item['capacity'] * efficiency)
                        
                        if capacity <= 0:
                            continue
                        
                        quantity = min(capacity, remaining_items[item_code])
                        
                        if quantity > 0:
                            all_assignments.append({
                                'Semaine': week_num,
                                'Jour': day,
                                'Shift': current_shift,
                                'Projet': project_name,
                                'Opérateur': op_name,
                                'Item': item_code,
                                'Quantité': quantity,
                                'Efficience': efficiency,
                                'Priorité EDD': item['due_date_priority']
                            })
                            
                            remaining_items[item_code] -= quantity
                            assigned_operators.add(op_name)
                            
                            if item_code not in shift_production:
                                shift_production[item_code] = 0
                            shift_production[item_code] += quantity
                
                # Passer au shift suivant
                shift_num += 1
                
                # Gérer le passage au jour suivant
                if day <= 5:
                    if shift_num > 3:
                        shift_num = 1
                        day += 1
                else:
                    if shift_num > 2:
                        shift_num = 1
                        day += 1
                
                # Vérifier si la semaine est terminée (6 jours, 17 shifts max)
                if day > 6:
                    week_finished = True
            
            # Afficher le résumé de la semaine
            print(f"\n📊 Résumé Semaine {week_num}:")
            for item_code, remaining in remaining_items.items():
                produced = [item for item in prioritized_items if item['item_code'] == item_code][0]['weekly_demand'] - remaining
                objective = [item for item in prioritized_items if item['item_code'] == item_code][0]['weekly_demand']
                status = "✓" if remaining == 0 else "⚠"
                print(f"   {status} {item_code}: {produced}/{objective} unités")
        
        return pd.DataFrame(all_assignments)
    
    def export_to_excel(self, schedule_df, filename="planning_mensuel_multi_projets.xlsx"):
        """Exporter le planning mensuel vers Excel"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            schedule_df.to_excel(writer, sheet_name='Planning Mensuel', index=False)
            
            # Stats par projet
            stats_by_project = schedule_df.groupby('Projet').agg({
                'Quantité': 'sum',
                'Shift': 'count'
            }).rename(columns={'Shift': 'Nombre de shifts'})
            stats_by_project.to_excel(writer, sheet_name='Stats par Projet')
            
            # Stats par semaine
            stats_by_week = schedule_df.groupby('Semaine').agg({
                'Quantité': 'sum',
                'Shift': 'count'
            }).rename(columns={'Shift': 'Nombre de shifts'})
            stats_by_week.to_excel(writer, sheet_name='Stats par Semaine')
            
            # Analyse des besoins par projet
            analysis_data = []
            for project_name, items in self.projects.items():
                for item_code, item_data in items.items():
                    monthly_demand = item_data['monthly_demand']
                    weekly_demand = monthly_demand // 4
                    load = self.calculate_load(project_name, item_code, weekly_demand)
                    shifts_req = self.calculate_required_shifts(project_name, item_code, weekly_demand, num_operators=1)
                    
                    analysis_data.append({
                        'Projet': project_name,
                        'Item': item_code,
                        'Demande Mensuelle': monthly_demand,
                        'Demande Hebdomadaire': weekly_demand,
                        'Load (heures)': round(load, 2),
                        'Shifts Requis': round(shifts_req, 2),
                        'Cycle Time (min)': item_data['cycle_time'],
                        'Priorité EDD': item_data['due_date_priority']
                    })
            
            analysis_df = pd.DataFrame(analysis_data)
            analysis_df.to_excel(writer, sheet_name='Analyse Besoins', index=False)
        
        print(f"\n✓ Sauvegardé: {filename}")


def main():
    print("=" * 100)
    print("ORDONNANCEMENT MENSUEL MULTI-PROJETS (4 SEMAINES)")
    print("=" * 100)
    
    scheduler = MonthlyMultiProjectScheduler(shift_duration_hours=7.5)
    
    print("\n📋 Ajout des projets...")
    
    # Projet BF
    scheduler.add_project('BF', {
        'M400200': {'monthly_demand': 40, 'capacity_per_operator_per_shift': 180, 'cycle_time': 2.5, 'due_date_priority': 1, 'capable_operators': ['OP1', 'OP2', 'OP7']},
        'M400201': {'monthly_demand': 53, 'capacity_per_operator_per_shift': 160, 'cycle_time': 2.8, 'due_date_priority': 1, 'capable_operators': ['OP1', 'OP2', 'OP7']},
        'M400228': {'monthly_demand': 107, 'capacity_per_operator_per_shift': 225, 'cycle_time': 2.0, 'due_date_priority': 1, 'capable_operators': ['OP1', 'OP2', 'OP7', 'OP8', 'OP10']},
        'M400229': {'monthly_demand': 91, 'capacity_per_operator_per_shift': 205, 'cycle_time': 2.2, 'due_date_priority': 1, 'capable_operators': ['OP1', 'OP2', 'OP7', 'OP8', 'OP10']},
        'M500304': {'monthly_demand': 80, 'capacity_per_operator_per_shift': 129, 'cycle_time': 3.5, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500309': {'monthly_demand': 3, 'capacity_per_operator_per_shift': 113, 'cycle_time': 4.0, 'due_date_priority': 4, 'capable_operators': ['OP5', 'OP6']},
        'M500312': {'monthly_demand': 64, 'capacity_per_operator_per_shift': 141, 'cycle_time': 3.2, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500313': {'monthly_demand': 44, 'capacity_per_operator_per_shift': 150, 'cycle_time': 3.0, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500318': {'monthly_demand': 74, 'capacity_per_operator_per_shift': 155, 'cycle_time': 2.9, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500319': {'monthly_demand': 91, 'capacity_per_operator_per_shift': 145, 'cycle_time': 3.1, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500324': {'monthly_demand': 128, 'capacity_per_operator_per_shift': 250, 'cycle_time': 1.8, 'due_date_priority': 3, 'capable_operators': ['OP3', 'OP4']},
        'M500329': {'monthly_demand': 16, 'capacity_per_operator_per_shift': 107, 'cycle_time': 4.2, 'due_date_priority': 4, 'capable_operators': ['OP5', 'OP6']},
        'M502239': {'monthly_demand': 17, 'capacity_per_operator_per_shift': 118, 'cycle_time': 3.8, 'due_date_priority': 4, 'capable_operators': ['OP5', 'OP6']},
        'M500311': {'monthly_demand': 44, 'capacity_per_operator_per_shift': 136, 'cycle_time': 3.3, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500323': {'monthly_demand': 76, 'capacity_per_operator_per_shift': 167, 'cycle_time': 2.7, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500317': {'monthly_demand': 101, 'capacity_per_operator_per_shift': 173, 'cycle_time': 2.6, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500325': {'monthly_demand': 91, 'capacity_per_operator_per_shift': 188, 'cycle_time': 2.4, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
        'M500326': {'monthly_demand': 2, 'capacity_per_operator_per_shift': 90, 'cycle_time': 5.0, 'due_date_priority': 5, 'capable_operators': ['OP5', 'OP6']},
        'M500327': {'monthly_demand': 67, 'capacity_per_operator_per_shift': 132, 'cycle_time': 3.4, 'due_date_priority': 5, 'capable_operators': ['OP5', 'OP6']},
        'M500328': {'monthly_demand': 34, 'capacity_per_operator_per_shift': 125, 'cycle_time': 3.6, 'due_date_priority': 2, 'capable_operators': ['OP3', 'OP4']},
    })
    
    # Projet FF
    scheduler.add_project('FF', {
        'FF001': {'monthly_demand': 50, 'capacity_per_operator_per_shift': 196, 'cycle_time': 2.3, 'due_date_priority': 2, 'capable_operators': ['OP1', 'OP2']},
        'FF002': {'monthly_demand': 75, 'capacity_per_operator_per_shift': 167, 'cycle_time': 2.7, 'due_date_priority': 3, 'capable_operators': ['OP3', 'OP4']},
        'FF003': {'monthly_demand': 60, 'capacity_per_operator_per_shift': 150, 'cycle_time': 3.0, 'due_date_priority': 4, 'capable_operators': ['OP5', 'OP6']},
    })
    
    # Projet Acituri
    scheduler.add_project('Acituri', {
        'AC001': {'monthly_demand': 40, 'capacity_per_operator_per_shift': 180, 'cycle_time': 2.5, 'due_date_priority': 2, 'capable_operators': ['OP1', 'OP7']},
        'AC002': {'monthly_demand': 55, 'capacity_per_operator_per_shift': 160, 'cycle_time': 2.8, 'due_date_priority': 2, 'capable_operators': ['OP2', 'OP8']},
    })
    
    # Projet Leg
    scheduler.add_project('Leg', {
        'LEG001': {'monthly_demand': 30, 'capacity_per_operator_per_shift': 141, 'cycle_time': 3.2, 'due_date_priority': 3, 'capable_operators': ['OP3', 'OP4']},
        'LEG002': {'monthly_demand': 45, 'capacity_per_operator_per_shift': 155, 'cycle_time': 2.9, 'due_date_priority': 3, 'capable_operators': ['OP5', 'OP6']},
    })
    
    # Projet Hinge
    scheduler.add_project('Hinge', {
        'HNG001': {'monthly_demand': 35, 'capacity_per_operator_per_shift': 173, 'cycle_time': 2.6, 'due_date_priority': 3, 'capable_operators': ['OP1', 'OP2']},
        'HNG002': {'monthly_demand': 50, 'capacity_per_operator_per_shift': 145, 'cycle_time': 3.1, 'due_date_priority': 3, 'capable_operators': ['OP7', 'OP8']},
    })
    
    print("\n👥 Ajout des opérateurs...")
    
    # Ajouter les opérateurs pour chaque shift
    for shift in [1, 2, 3]:
        num_ops = {1: 8, 2: 9, 3: 10}[shift]
        
        for i in range(1, num_ops + 1):
            op_name = f'OP{i}'
            efficiency = 1.00 - (i - 1) * 0.02
            
            if i <= 2:
                capable = ['M400200', 'M400201', 'M400228', 'M400229', 'FF001', 'AC001', 'AC002', 'HNG001']
            elif i <= 4:
                capable = ['M500304', 'M500312', 'M500313', 'M500318', 'M500319', 'M500324', 
                          'M500311', 'M500323', 'M500317', 'M500325', 'M500328', 'FF002', 'LEG001']
            elif i <= 6:
                capable = ['M500309', 'M500329', 'M502239', 'M500326', 'M500327', 'FF003', 'LEG002']
            elif i <= 8:
                capable = ['M400228', 'M400229', 'AC002', 'HNG002']
            else:
                capable = ['M400228', 'M400229']
            
            scheduler.add_operator(op_name, capable, efficiency=efficiency, shift=shift)
    
    # Afficher l'analyse des besoins
    scheduler.print_project_analysis()
    
    print("\n🚀 Lancement de l'ordonnancement mensuel (4 semaines)...")
    
    schedule = scheduler.schedule_month(start_date=datetime(2026, 3, 1))
    
    if not schedule.empty:
        print(f"\n📋 Planning généré: {len(schedule)} assignations")
        print("\nAperçu du planning (30 premières lignes):")
        print(schedule.head(30).to_string(index=False))
        
        scheduler.export_to_excel(schedule)
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
