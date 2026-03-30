"""
Moteur d'ordonnancement pour l'application Flask
Adapté de ordonnancement_operateurs.py pour intégration avec la base de données
"""

import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict
from models import OrdreFabrication, Produit


class OperatorScheduler:
    """
    Classe pour ordonnancer la production avec un nombre fixe d'opérateurs (Méthode 1)
    """
    
    def __init__(self, shift_duration_hours=7.5, shifts_per_day=3, operators_per_shift=None, absences_per_shift=None):
        self.shift_duration = shift_duration_hours
        self.shifts_per_day = shifts_per_day
        
        # Nombre d'opérateurs par shift: {1: 8, 2: 9, 3: 10}
        self.operators_per_shift = operators_per_shift or {1: 8, 2: 9, 3: 10}
        
        # Nombre d'absences par shift: {1: 0, 2: 0, 3: 0}
        self.absences_per_shift = absences_per_shift or {1: 0, 2: 0, 3: 0}
        
        self.items_data = {}
        self.operators = {}
        self.operator_capabilities = {}
    
    def add_item(self, item_code, weekly_demand, capacity_per_operator_per_shift, 
                 cycle_time, efficiency=1.0, due_date_priority=None):
        """
        Ajouter un article avec ses paramètres
        
        Parameters:
        - item_code: Code de l'article
        - weekly_demand: Besoin hebdomadaire
        - capacity_per_operator_per_shift: Capacité qu'UN opérateur peut produire en 1 shift
        - cycle_time: Temps de cycle (heures)
        - efficiency: Efficience moyenne (0-1)
        - due_date_priority: Priorité EDD (1=Lundi, 5=Vendredi)
        """
        self.items_data[item_code] = {
            'weekly_demand': weekly_demand,
            'capacity_per_operator_per_shift': capacity_per_operator_per_shift,
            'cycle_time': cycle_time,
            'efficiency': efficiency,
            'due_date_priority': due_date_priority if due_date_priority else 999
        }
    
    def add_operator(self, operator_name, capable_items: List[str], efficiency=1.0):
        """
        Ajouter un opérateur avec ses capabilités et son efficience
        
        Parameters:
        - operator_name: Nom de l'opérateur (ex: "OP1", "OP2")
        - capable_items: Liste des articles que cet opérateur peut produire
        - efficiency: Efficience de l'opérateur (0.0-1.0, ex: 0.85 = 85%)
        """
        self.operators[operator_name] = {
            'capable_items': set(capable_items),
            'assigned_tasks': [],
            'efficiency': efficiency
        }
        
        # Indexer les capabilités par article
        for item in capable_items:
            if item not in self.operator_capabilities:
                self.operator_capabilities[item] = []
            self.operator_capabilities[item].append(operator_name)
    
    def calculate_load(self, item_code):
        """Calculer la charge en heures"""
        item = self.items_data[item_code]
        quantity = item['weekly_demand']
        cycle_time = item['cycle_time']
        efficiency = item['efficiency'] if item['efficiency'] > 0 else 1.0
        
        load_hours = (quantity * cycle_time) / efficiency
        return load_hours
    
    def calculate_required_shifts(self, item_code, num_operators=1):
        """
        Calculer le nombre de shifts nécessaires basé sur la charge (load)
        """
        load_hours = self.calculate_load(item_code)
        total_hours_per_shift = self.shift_duration * num_operators
        required_shifts = load_hours / total_hours_per_shift
        return required_shifts
    
    def prioritize_items(self):
        """Prioriser les articles selon EDD et nombre de shifts"""
        priority_list = []
        
        for item_code in self.items_data.keys():
            item = self.items_data[item_code]
            required_shifts = self.calculate_required_shifts(item_code, num_operators=1)
            load_hours = self.calculate_load(item_code)
            due_date_priority = item['due_date_priority']
            
            # Trouver combien d'opérateurs peuvent faire cet article
            capable_operators = self.operator_capabilities.get(item_code, [])
            
            priority_list.append({
                'item_code': item_code,
                'weekly_demand': item['weekly_demand'],
                'capacity_per_operator': item['capacity_per_operator_per_shift'],
                'cycle_time': item['cycle_time'],
                'efficiency': item['efficiency'],
                'load_hours': load_hours,
                'required_shifts_1op': required_shifts,
                'due_date_priority': due_date_priority,
                'capable_operators_count': len(capable_operators),
                'capable_operators': capable_operators
            })
        
        # Trier par: 1) EDD, 2) Nombre de shifts
        priority_list.sort(key=lambda x: (x['due_date_priority'], -x['required_shifts_1op']))
        
        return priority_list
    
    def schedule_with_fixed_operators(self, start_date=None):
        """
        MÉTHODE 1: Ordonnancer avec un nombre fixe d'opérateurs
        TOUS les opérateurs travaillent simultanément dans chaque shift
        """
        if start_date is None:
            start_date = datetime.now()
        
        if not self.operators:
            raise ValueError("Aucun opérateur défini! Utilisez add_operator() d'abord.")
        
        prioritized_items = self.prioritize_items()
        
        assignments = []
        day = 1
        shift = 1
        
        # Garder trace de ce qui reste à produire pour chaque article
        remaining_items = {item['item_code']: item['weekly_demand'] for item in prioritized_items}
        
        # Continuer jusqu'à ce que tout soit produit OU que la semaine soit terminée
        week_finished = False
        
        while any(qty > 0 for qty in remaining_items.values()) and not week_finished:
            # Déterminer combien d'opérateurs sont disponibles pour ce shift
            base_operators = self.operators_per_shift.get(shift, 8)
            absences = self.absences_per_shift.get(shift, 0)
            max_operators_this_shift = base_operators - absences
            operators_assigned_count = 0
            
            # Pour ce shift, tous les opérateurs travaillent en parallèle
            shift_production = {}
            
            # Parcourir les articles par ordre de priorité
            for item in prioritized_items:
                item_code = item['item_code']
                remaining_qty = remaining_items[item_code]
                
                if remaining_qty <= 0:
                    continue
                
                # Capacité de base du produit (unités/shift)
                item_data = self.items_data[item_code]
                base_capacity = item_data['capacity_per_operator_per_shift']
                
                capable_ops = [op for op in item['capable_operators'] if op in self.operators]
                
                if not capable_ops:
                    continue
                
                # Assigner les opérateurs capables à cet article dans ce shift
                for op_name in capable_ops:
                    # Vérifier si on a atteint le maximum d'opérateurs pour ce shift
                    if operators_assigned_count >= max_operators_this_shift:
                        break
                    
                    # Vérifier si cet opérateur n'est pas déjà assigné dans ce shift
                    if op_name not in shift_production:
                        # Capacité réelle = Capacité produit × Efficience opérateur
                        operator_efficiency = self.operators[op_name]['efficiency']
                        capacity_per_op = int(base_capacity * operator_efficiency)
                        
                        # Si la capacité calculée est 0, utiliser au moins 1
                        if capacity_per_op == 0:
                            capacity_per_op = 1
                        
                        # Quantité entière basée sur la capacité
                        qty_this_shift = int(min(capacity_per_op, remaining_qty))
                        
                        if qty_this_shift > 0:
                            assignments.append({
                                'Jour': day,
                                'Shift': shift,
                                'Opérateur': op_name,
                                'Item': item_code,
                                'Quantité': qty_this_shift,
                                'Priorité EDD': item['due_date_priority']
                            })
                            
                            shift_production[op_name] = item_code
                            remaining_items[item_code] -= qty_this_shift
                            remaining_qty -= qty_this_shift
                            operators_assigned_count += 1
                            
                            if remaining_qty <= 0:
                                break
                
                # Si on a atteint le maximum d'opérateurs, passer à l'article suivant
                if operators_assigned_count >= max_operators_this_shift:
                    break
            
            # Passer au shift suivant
            shift += 1
            max_shifts_today = 2 if day == 6 else self.shifts_per_day
            if shift > max_shifts_today:
                shift = 1
                day += 1
                # Après le jour 6, la semaine est terminée
                if day > 6:
                    week_finished = True
        
        return pd.DataFrame(assignments)


def generer_planning_depuis_of(projet_id, of_ids, params):
    """
    Générer un planning d'ordonnancement à partir des OF sélectionnés
    
    Args:
        projet_id: ID du projet
        of_ids: Liste des IDs d'OF à ordonnancer
        params: {
            'operators_per_shift': {1: 8, 2: 9, 3: 10},
            'absences_per_shift': {1: 0, 2: 0, 3: 0}
        }
    
    Returns:
        dict avec:
        - assignments: DataFrame avec le planning détaillé
        - stats: Statistiques du planning
        - of_details: Détails par OF
    """
    
    # Créer le scheduler
    scheduler = OperatorScheduler(
        operators_per_shift=params.get('operators_per_shift', {1: 8, 2: 9, 3: 10}),
        absences_per_shift=params.get('absences_per_shift', {1: 0, 2: 0, 3: 0})
    )
    
    # Charger les OF depuis la DB
    ordres = OrdreFabrication.query.filter(
        OrdreFabrication.id.in_(of_ids)
    ).all()
    
    if not ordres:
        raise ValueError("Aucun OF trouvé avec les IDs fournis")
    
    # Ajouter les items au scheduler
    for of in ordres:
        quantite_restante = of.quantite_demandee - of.quantite_produite
        
        if quantite_restante <= 0:
            continue
        
        scheduler.add_item(
            item_code=of.produit.reference,
            weekly_demand=quantite_restante,
            capacity_per_operator_per_shift=of.capacite_par_operateur or 10,  # Valeur par défaut
            cycle_time=of.temps_cycle or 1.0,  # Valeur par défaut
            efficiency=of.efficience,
            due_date_priority=of.priorite_edd
        )
    
    # Ajouter les opérateurs (pour v1: tous polyvalents)
    # Dans une version future, ces données viendront de la DB
    item_codes = [of.produit.reference for of in ordres]
    
    for i in range(1, 15):  # 14 opérateurs
        op_name = f"OP{i:02d}"
        scheduler.add_operator(
            operator_name=op_name,
            capable_items=item_codes,  # Tous polyvalents pour v1
            efficiency=0.85  # Efficience moyenne
        )
    
    # Générer le planning (Méthode 1)
    assignments_df = scheduler.schedule_with_fixed_operators()
    
    # Calculer les statistiques
    if not assignments_df.empty:
        nb_jours = assignments_df['Jour'].max()
        nb_shifts = len(assignments_df)
        
        # Calculer le taux d'utilisation
        total_operators_available = sum([
            params['operators_per_shift'].get(i, 0) - params['absences_per_shift'].get(i, 0)
            for i in [1, 2, 3]
        ])
        
        operators_used = assignments_df.groupby(['Jour', 'Shift'])['Opérateur'].nunique().mean()
        taux_utilisation = round((operators_used / total_operators_available) * 100, 1) if total_operators_available > 0 else 0
        
        stats = {
            'nb_of': len(ordres),
            'duree_jours': nb_jours,
            'nb_shifts': nb_shifts,
            'taux_utilisation': taux_utilisation
        }
        
        # Détails par OF
        of_details = []
        for of in ordres:
            of_assignments = assignments_df[assignments_df['Item'] == of.produit.reference]
            
            if not of_assignments.empty:
                jour_debut = of_assignments['Jour'].min()
                shift_debut = of_assignments[of_assignments['Jour'] == jour_debut]['Shift'].min()
                jour_fin = of_assignments['Jour'].max()
                shift_fin = of_assignments[of_assignments['Jour'] == jour_fin]['Shift'].max()
                quantite_planifiee = of_assignments['Quantité'].sum()
                duree_shifts = len(of_assignments)
                
                of_details.append({
                    'numero_of': of.numero_of,
                    'produit': of.produit.reference,
                    'quantite': quantite_planifiee,
                    'priorite': of.priorite_edd,
                    'jour_debut': jour_debut,
                    'shift_debut': shift_debut,
                    'jour_fin': jour_fin,
                    'shift_fin': shift_fin,
                    'duree_shifts': duree_shifts
                })
    else:
        stats = {
            'nb_of': len(ordres),
            'duree_jours': 0,
            'nb_shifts': 0,
            'taux_utilisation': 0
        }
        of_details = []
    
    return {
        'assignments': assignments_df.to_dict('records') if not assignments_df.empty else [],
        'stats': stats,
        'of_details': of_details
    }
