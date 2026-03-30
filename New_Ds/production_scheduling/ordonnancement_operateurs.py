import pandas as pd

from datetime import datetime, timedelta

import numpy as np

from typing import List, Dict, Set



class OperatorScheduler:

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

                 cycle_time, efficiency=1.0, due_date=None, weight=None):

        """

        Ajouter un article avec ses paramètres

        

        Parameters:

        - item_code: Code de l'article

        - weekly_demand: Besoin hebdomadaire

        - capacity_per_operator_per_shift: Capacité qu'UN opérateur peut produire en 1 shift

        - cycle_time: Temps de cycle (heures)

        - efficiency: Efficience moyenne (0-1)

        - due_date: Date d'échéance (datetime ou string 'YYYY-MM-DD')

        - weight: Poids pour le tri (indicateur d'importance)

        """

        # Convertir la date si c'est une string

        if isinstance(due_date, str):

            due_date = datetime.strptime(due_date, '%Y-%m-%d')

        

        self.items_data[item_code] = {

            'weekly_demand': weekly_demand,

            'capacity_per_operator_per_shift': capacity_per_operator_per_shift,

            'cycle_time': cycle_time,

            'efficiency': efficiency,

            'due_date': due_date if due_date else datetime(2099, 12, 31),

            'weight': weight if weight is not None else 1

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

    

    def set_absences(self, absences_per_shift):

        """

        Définir le nombre d'absences par shift

        

        Parameters:

        - absences_per_shift: Dict {shift_number: nombre_absences}

          Exemple: {1: 2, 2: 1, 3: 0} = 2 absents shift 1, 1 absent shift 2, 0 absent shift 3

        """

        self.absences_per_shift = absences_per_shift

        print(f"\n⚠️  Absences configurées:")

        for shift, absences in absences_per_shift.items():

            available = self.operators_per_shift.get(shift, 0) - absences

            print(f"   Shift {shift}: {absences} absent(s) → {available} opérateurs disponibles")

    

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

        Formule: Charge totale (heures) / (Durée shift × Nombre d'opérateurs)

        

        La charge inclut l'efficience: Charge = (Quantité × Cycle Time) / Efficience

        

        Parameters:

        - item_code: Code de l'article

        - num_operators: Nombre d'opérateurs travaillant en parallèle

        """

        # Calculer la charge totale en heures (inclut déjà l'efficience)

        load_hours = self.calculate_load(item_code)

        

        # Capacité totale par shift = durée shift × nombre d'opérateurs

        total_hours_per_shift = self.shift_duration * num_operators

        

        # Nombre de shifts nécessaires basé sur la charge

        required_shifts = load_hours / total_hours_per_shift

        return required_shifts

    

    def prioritize_items(self):

        """Prioriser les articles avec un score combiné (EDD + Poids + Shifts)"""

        priority_list = []

        

        # Collecter toutes les données

        for item_code in self.items_data.keys():

            item = self.items_data[item_code]

            required_shifts = self.calculate_required_shifts(item_code, num_operators=1)

            load_hours = self.calculate_load(item_code)

            due_date = item['due_date']

            weight = item.get('weight', 1)

            

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

                'due_date': due_date,

                'weight': weight,

                'capable_operators_count': len(capable_operators),

                'capable_operators': capable_operators

            })

        

        # Normaliser les valeurs et calculer le score combiné

        if priority_list:

            # Trouver min/max pour normalisation

            min_date = min(item['due_date'] for item in priority_list)

            max_date = max(item['due_date'] for item in priority_list)

            date_range = (max_date - min_date).days if max_date != min_date else 1

            

            max_weight = max(item['weight'] for item in priority_list)

            min_weight = min(item['weight'] for item in priority_list)

            weight_range = max_weight - min_weight if max_weight != min_weight else 1

            

            max_shifts = max(item['required_shifts_1op'] for item in priority_list)

            min_shifts = min(item['required_shifts_1op'] for item in priority_list)

            shifts_range = max_shifts - min_shifts if max_shifts != min_shifts else 1

            

            # Calculer le score pour chaque article

            for item in priority_list:

                # Normaliser entre 0 et 1

                norm_date = (item['due_date'] - min_date).days / date_range

                norm_weight = (item['weight'] - min_weight) / weight_range

                norm_shifts = (item['required_shifts_1op'] - min_shifts) / shifts_range

                

                # Poids d'importance (ajustables selon vos besoins)

                W_date = 0.5    # 50% d'importance pour la date

                W_weight = 0.3  # 30% d'importance pour le poids

                W_shifts = 0.2  # 20% d'importance pour les shifts

                

                # Score combiné (plus petit = plus prioritaire)

                # Pour date: plus proche = mieux (donc on garde la valeur normalisée)

                # Pour weight: plus grand = mieux (donc on inverse avec 1-)

                # Pour shifts: plus grand = mieux (donc on inverse avec 1-)

                score = (W_date * norm_date) + (W_weight * (1 - norm_weight)) + (W_shifts * (1 - norm_shifts))

                

                item['priority_score'] = score

            

            # Trier par score (plus petit score = plus prioritaire)

            priority_list.sort(key=lambda x: x['priority_score'])

        

        return priority_list

    

    # ========== MÉTHODE 1: NOMBRE FIXE D'OPÉRATEURS ==========

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

            # Déterminer combien d'opérateurs sont disponibles pour ce shift (en tenant compte des absences)

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

                                'Date échéance': item['due_date'].strftime('%Y-%m-%d'),

                                'Poids': item['weight'],

                                'Score': round(item.get('priority_score', 0), 3)

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

            

            # Passer au shift suivant avec contrainte: jour 6 = 2 shifts seulement

            shift += 1

            max_shifts_today = 2 if day == 6 else self.shifts_per_day

            if shift > max_shifts_today:

                shift = 1

                day += 1

                # Après le jour 6, la semaine est terminée - ARRÊTER

                if day > 6:

                    week_finished = True

        

        return pd.DataFrame(assignments)

    

    # ========== MÉTHODE 2: CALCUL AUTOMATIQUE DES OPÉRATEURS ==========

    def calculate_required_operators(self):

        """

        MÉTHODE 2: Calculer le nombre d'opérateurs nécessaires

        pour compléter la charge dans les délais

        """

        prioritized_items = self.prioritize_items()

        

        # Calculer la charge totale

        total_load_hours = sum([item['load_hours'] for item in prioritized_items])

        

        # Calculer les shifts disponibles dans une semaine: 5 jours × 3 shifts + 1 jour × 2 shifts

        total_shifts_available = (5 * self.shifts_per_day) + 2  # 5 jours × 3 + jour 6 × 2 = 17 shifts

        total_hours_available_per_operator = total_shifts_available * self.shift_duration

        

        # Nombre minimum d'opérateurs nécessaires

        min_operators_needed = np.ceil(total_load_hours / total_hours_available_per_operator)

        

        # Analyse par article

        operator_requirements = []

        

        for item in prioritized_items:

            item_code = item['item_code']

            load_hours = item['load_hours']

            

            # Combien d'opérateurs pour finir cet article dans les délais?

            # Supposons qu'on veut finir chaque article en 1-2 jours max

            max_days_per_item = 2

            max_shifts_per_item = max_days_per_item * self.shifts_per_day

            max_hours_available = max_shifts_per_item * self.shift_duration

            

            operators_for_this_item = np.ceil(load_hours / max_hours_available)

            

            operator_requirements.append({

                'Item': item_code,

                'Charge (h)': load_hours,

                'Shifts (1 op)': item['required_shifts_1op'],

                'Opérateurs nécessaires': int(operators_for_this_item),

                'Date échéance': item['due_date'].strftime('%Y-%m-%d'),

                'Poids': item['weight'],

                'Opérateurs capables': ', '.join(item['capable_operators']) if item['capable_operators'] else 'Aucun'

            })

        

        return {

            'total_load_hours': total_load_hours,

            'min_operators_needed': int(min_operators_needed),

            'operator_requirements': pd.DataFrame(operator_requirements),

            'hours_per_operator_per_week': total_hours_available_per_operator

        }

    

    def schedule_with_calculated_operators(self, start_date=None):

        """

        MÉTHODE 2: Ordonnancer en calculant automatiquement les opérateurs nécessaires

        """

        if start_date is None:

            start_date = datetime.now()

        

        prioritized_items = self.prioritize_items()

        

        # Calculer les besoins en opérateurs

        operator_analysis = self.calculate_required_operators()

        

        assignments = []

        day = 1

        shift = 1

        

        # Pour chaque article, assigner des opérateurs virtuels

        virtual_operator_id = 1

        

        for item in prioritized_items:

            item_code = item['item_code']

            remaining_quantity = item['weekly_demand']

            load_hours = item['load_hours']

            

            # Capacité de base du produit (unités/shift)

            item_data = self.items_data[item_code]

            base_capacity = item_data['capacity_per_operator_per_shift']

            

            # Pour la méthode 2, utiliser l'efficience moyenne des opérateurs capables

            capable_ops = item['capable_operators']

            if capable_ops:

                avg_efficiency = np.mean([self.operators[op]['efficiency'] for op in capable_ops if op in self.operators])

            else:

                avg_efficiency = 1.0

            

            # Capacité réelle = Capacité produit × Efficience moyenne

            capacity_per_op = int(base_capacity * avg_efficiency)

            

            # Si la capacité calculée est 0, utiliser au moins 1

            if capacity_per_op == 0:

                capacity_per_op = 1

            

            # Déterminer combien d'opérateurs en parallèle

            max_days = 2

            max_hours = max_days * self.shifts_per_day * self.shift_duration

            num_parallel_operators = max(1, int(np.ceil(load_hours / max_hours)))

            

            # Limiter par les opérateurs capables disponibles

            capable_ops = item['capable_operators']

            if capable_ops:

                num_parallel_operators = min(num_parallel_operators, len(capable_ops))

            

            # Distribuer la quantité entre les opérateurs

            qty_per_operator = np.ceil(remaining_quantity / num_parallel_operators)

            

            for op_idx in range(num_parallel_operators):

                qty_for_this_op = min(qty_per_operator, remaining_quantity)

                remaining_for_this_op = qty_for_this_op

                

                # Assigner des shifts à cet opérateur

                while remaining_for_this_op > 0:

                    # Quantité entière basée sur la capacité

                    qty_this_shift = int(min(capacity_per_op, remaining_for_this_op))

                    if qty_this_shift == 0:

                        qty_this_shift = 1  # Au moins 1 unité

                    

                    # Nom de l'opérateur (réel si disponible, sinon virtuel)

                    if capable_ops and op_idx < len(capable_ops):

                        op_name = capable_ops[op_idx]

                    else:

                        op_name = f"OP_Virtual_{virtual_operator_id}"

                        virtual_operator_id += 1

                    

                    assignments.append({

                        'Jour': day,

                        'Shift': shift,

                        'Opérateur': op_name,

                        'Item': item_code,

                        'Quantité': qty_this_shift,

                        'Date échéance': item['due_date'].strftime('%Y-%m-%d'),

                        'Poids': item['weight'],

                        'Score': round(item.get('priority_score', 0), 3)

                    })

                    

                    remaining_for_this_op -= qty_this_shift

                    shift += 1

                    # Contrainte: jour 6 = 2 shifts seulement

                    max_shifts_today = 2 if day == 6 else self.shifts_per_day

                    if shift > max_shifts_today:

                        shift = 1

                        day += 1

                        # Après le jour 6, recommencer à jour 1 (nouvelle semaine)

                        if day > 6:

                            day = 1

                

                remaining_quantity -= qty_for_this_op

        

        return pd.DataFrame(assignments), operator_analysis

    

    def print_summary(self, method="both"):

        """Afficher un résumé"""

        prioritized_items = self.prioritize_items()

        

        total_load = sum([item['load_hours'] for item in prioritized_items])

        total_shifts_1op = sum([item['required_shifts_1op'] for item in prioritized_items])

        total_quantity = sum([item['weekly_demand'] for item in prioritized_items])

        

        print("=" * 100)

        print("RÉSUMÉ DU SYSTÈME D'ORDONNANCEMENT AVEC OPÉRATEURS")

        print("=" * 100)

        print(f"Nombre d'articles: {len(prioritized_items)}")

        print(f"Quantité totale: {total_quantity}")

        print(f"Charge totale: {total_load:.2f} heures")

        print(f"Shifts nécessaires (1 opérateur): {total_shifts_1op:.2f} shifts")

        print(f"Durée d'un shift: {self.shift_duration}h")

        print(f"Shifts par jour: {self.shifts_per_day}")

        print(f"Nombre d'opérateurs définis: {len(self.operators)}")

        print("=" * 100)





def main():

    print("=" * 100)

    print("SYSTÈME D'ORDONNANCEMENT AVEC GESTION DES OPÉRATEURS")

    print("=" * 100)

    

    # Créer l'instance

    scheduler = OperatorScheduler(shift_duration_hours=7.5, shifts_per_day=3)

    

    # ===== DEMANDER LES ABSENCES =====

    print("\n⚠️  CONFIGURATION DES ABSENCES")

    print("=" * 100)

    print("Nombre d'opérateurs par shift (sans absences):")

    print("   - Shift 1 (Matin): 8 opérateurs")

    print("   - Shift 2 (Soir):  9 opérateurs")

    print("   - Shift 3 (Nuit):  10 opérateurs")

    print()

    

    # Demander si l'utilisateur veut configurer des absences

    response = input("Avez-vous des absences à signaler? (o/n): ").strip().lower()

    

    if response in ['o', 'oui', 'y', 'yes']:

        absences = {}

        

        # Demander pour chaque shift

        for shift_num in [1, 2, 3]:

            shift_name = {1: "Matin", 2: "Soir", 3: "Nuit"}[shift_num]

            max_ops = {1: 8, 2: 9, 3: 10}[shift_num]

            

            while True:

                try:

                    nb_absents = input(f"   Shift {shift_num} ({shift_name}): Nombre d'absents (0-{max_ops}): ").strip()

                    nb_absents = int(nb_absents)

                    

                    if 0 <= nb_absents <= max_ops:

                        absences[shift_num] = nb_absents

                        break

                    else:

                        print(f"      ❌ Erreur: Le nombre doit être entre 0 et {max_ops}")

                except ValueError:

                    print("      ❌ Erreur: Veuillez entrer un nombre valide")

        

        # Configurer les absences

        scheduler.set_absences(absences)

    else:

        print("   ✓ Aucune absence signalée - tous les opérateurs sont disponibles")

        scheduler.set_absences({1: 0, 2: 0, 3: 0})

    

    # ===== AJOUTER LES ARTICLES =====

    print("\n📦 Ajout des articles...")

    # Format: (Code, Besoin/semaine, Capacité/shift, Cycle time, Efficience, Date échéance, Poids)

    articles = [

        ('M400200', 10, 2, 2.0, 1.0, '2026-03-29', 5),

        ('M400201', 13, 2, 4.95, 1.0, '2026-03-29', 4),

        ('M400228', 27, 3, 5.2, 1.0, '2026-03-29', 3),

        ('M400229', 27, 3, 5.2, 1.0, '2026-03-29', 2),

        ('M500309', 1, 20, 2.85, 1.0, '2026-03-30', 1),

        ('M500325', 23, 4, 2.25, 1.0, '2026-03-30', 4),

        ('M500304', 20, 6, 2.25, 1.0, '2026-03-30', 5),

        ('M502026', 1, 4, 2.25, 1.0, '2026-03-31', 5),

        ('M500324', 32, 10, 1.95, 1.0, '2026-03-31', 3),

        ('M500319', 23, 10, 1.95, 1.0, '2026-03-31', 2),

        ('M500317', 25, 5, 2.25, 1.0, '2026-04-01', 1),

        ('M500329', 4, 8, 2.7, 1.0, '2026-04-01', 4),

        ('M500327', 17, 4, 5.2, 1.0, '2026-04-02', 5),

        ('M500311', 11, 5, 5.2, 1.0, '2026-04-02', 3),

        ('M500328', 9, 4, 2.25, 1.0, '2026-04-02', 2),

    ]

    

    for item_code, demand, capacity, cycle_time, efficiency, due_date, weight in articles:

        scheduler.add_item(item_code, demand, capacity, cycle_time, efficiency, due_date, weight)

    

    print(f"   ✓ {len(articles)} articles ajoutés")

    

    # ===== AJOUTER LES OPÉRATEURS AVEC LEURS CAPABILITÉS ET EFFICIENCE =====

    print("\n👷 Ajout des opérateurs et leurs capabilités...")

    

    # Format: add_operator(nom, [capabilités], efficience)

    # Efficience: 0.0-1.0 (ex: 0.85 = 85%, 1.0 = 100%)

    

    # Configuration réaliste: certains opérateurs ne peuvent pas faire certains articles

    

    # OP1 - Expert série M400 (efficience 100%)

    scheduler.add_operator('OP1', ['M400200', 'M400201', 'M400228', 'M400229'], efficiency=1.00)

    

    # OP2 - Polyvalent M400 + quelques M500 (efficience 95%)

    scheduler.add_operator('OP2', ['M400200', 'M400201', 'M400228', 'M400229', 'M500309', 'M500325'], efficiency=0.95)

    

    # OP3 - Expert série M500 début (efficience 90%)

    scheduler.add_operator('OP3', ['M500309', 'M500325', 'M500304', 'M500324', 'M500319'], efficiency=0.90)

    

    # OP4 - Expert série M500 milieu (efficience 85%)

    scheduler.add_operator('OP4', ['M500324', 'M500319', 'M500317', 'M500329'], efficiency=0.85)

    

    # OP5 - Expert série M500 fin (efficience 80%)

    scheduler.add_operator('OP5', ['M500327', 'M500311', 'M500328', 'M500329'], efficiency=0.80)

    

    # OP6 - Spécialiste M502 uniquement (efficience 75%)

    scheduler.add_operator('OP6', ['M502026'], efficiency=0.75)

    

    # OP7 - Polyvalent M400 + M500 (efficience 70%)

    scheduler.add_operator('OP7', ['M400200', 'M400228', 'M500309', 'M500325', 'M500304'], efficiency=0.70)

    

    # OP8 - Polyvalent M400 + M500 milieu (efficience 65%)

    scheduler.add_operator('OP8', ['M400228', 'M400229', 'M500324', 'M500319'], efficiency=0.65)

    

    # OP9 - Débutant série M500 fin uniquement (efficience 60%)

    scheduler.add_operator('OP9', ['M500327', 'M500311', 'M500328'], efficiency=0.60)

    

    # OP10 - Expert polyvalent (peut tout faire, efficience 100%)

    scheduler.add_operator('OP10', ['M400200', 'M400201', 'M400228', 'M400229', 'M500309', 'M500325', 

                                     'M500304', 'M502026', 'M500324', 'M500319', 'M500317', 'M500329', 

                                     'M500327', 'M500311', 'M500328'], efficiency=1.00)

    

    print(f"   ✓ {len(scheduler.operators)} opérateurs ajoutés")

    

    # ===== AFFICHER LE RÉSUMÉ =====

    scheduler.print_summary(method="both")

    

    # ===== MÉTHODE 1: NOMBRE FIXE D'OPÉRATEURS =====

    print("\n\n")

    print("=" * 100)

    print("MÉTHODE 1: ORDONNANCEMENT AVEC NOMBRE FIXE D'OPÉRATEURS")

    print("=" * 100)

    

    schedule_m1 = scheduler.schedule_with_fixed_operators()

    print("\n📋 Planning détaillé (premiers 30 shifts):")

    print(schedule_m1.head(30).to_string(index=False))

    print(f"\n... Total: {len(schedule_m1)} assignations de shifts")

    

    # Statistiques par opérateur ET par shift

    print("\n📊 Charge par opérateur et par shift:")

    op_shift_stats = schedule_m1.groupby(['Opérateur', 'Shift']).agg({

        'Quantité': 'sum',

        'Jour': 'count'

    }).rename(columns={'Jour': 'Nombre de shifts'})

    print(op_shift_stats.to_string())

    

    # Statistiques globales par opérateur

    print("\n📊 Charge totale par opérateur:")

    op_stats = schedule_m1.groupby('Opérateur').agg({

        'Quantité': 'sum',

        'Shift': 'count'

    }).rename(columns={'Shift': 'Nombre de shifts'})

    print(op_stats.to_string())

    

    # Bilan d'atteinte des objectifs

    print("\n\n")

    print("=" * 100)

    print("BILAN D'ATTEINTE DES OBJECTIFS - MÉTHODE 1")

    print("=" * 100)

    

    # Calculer la production réelle par article

    production_reelle = schedule_m1.groupby('Item')['Quantité'].sum()

    

    bilan_data = []

    all_objectives_met = True

    

    for item_code, data in scheduler.items_data.items():

        objectif = data['weekly_demand']

        produit = production_reelle.get(item_code, 0)

        atteint = produit >= objectif

        ecart = produit - objectif

        taux = (produit / objectif * 100) if objectif > 0 else 0

        

        if not atteint:

            all_objectives_met = False

        

        bilan_data.append({

            'Item': item_code,

            'Objectif': objectif,

            'Produit': produit,

            'Écart': ecart,

            'Taux (%)': taux,

            'Statut': '✓' if atteint else '✗'

        })

    

    bilan_df = pd.DataFrame(bilan_data)

    bilan_df = bilan_df.sort_values('Item')

    

    print("\n📊 Détail par article:")

    print(bilan_df.to_string(index=False))

    

    # Résumé global

    total_objectif = sum([d['weekly_demand'] for d in scheduler.items_data.values()])

    total_produit = production_reelle.sum()

    taux_global = (total_produit / total_objectif * 100) if total_objectif > 0 else 0

    

    print("\n" + "=" * 100)

    print("RÉSUMÉ GLOBAL:")

    print(f"   Total objectif: {total_objectif:.0f} unités")

    print(f"   Total produit: {total_produit:.0f} unités")

    print(f"   Taux d'atteinte: {taux_global:.1f}%")

    

    if all_objectives_met:

        print("\n   ✓✓✓ TOUS LES OBJECTIFS SONT ATTEINTS! ✓✓✓")

    else:

        items_non_atteints = bilan_df[bilan_df['Statut'] == '✗']['Item'].tolist()

        print(f"\n   ✗ ATTENTION: {len(items_non_atteints)} article(s) n'ont pas atteint l'objectif")

        print(f"   Articles concernés: {', '.join(items_non_atteints)}")

    print("=" * 100)

    

    # Sauvegarder en Excel

    with pd.ExcelWriter('planning_methode1_operateurs_fixes.xlsx', engine='openpyxl') as writer:

        schedule_m1.to_excel(writer, sheet_name='Planning', index=False)

        op_shift_stats.to_excel(writer, sheet_name='Charge par Op et Shift')

        op_stats.to_excel(writer, sheet_name='Charge totale par Op')

        bilan_df.to_excel(writer, sheet_name='Bilan Objectifs', index=False)

    print("\n✓ Sauvegardé: planning_methode1_operateurs_fixes.xlsx")

    print("  - Feuille 1: Planning")

    print("  - Feuille 2: Charge par Opérateur et Shift")

    print("  - Feuille 3: Charge totale par Opérateur")

    print("  - Feuille 4: Bilan Objectifs")

    

    # ===== MÉTHODE 2: CALCUL AUTOMATIQUE DES OPÉRATEURS =====

    print("\n\n")

    print("=" * 100)

    print("MÉTHODE 2: CALCUL AUTOMATIQUE DES OPÉRATEURS NÉCESSAIRES")

    print("=" * 100)

    

    schedule_m2, analysis = scheduler.schedule_with_calculated_operators()

    

    print("\n📊 Analyse des besoins:")

    print(f"   Charge totale: {analysis['total_load_hours']:.2f} heures")

    print(f"   Opérateurs minimum nécessaires: {analysis['min_operators_needed']}")

    print(f"   Heures disponibles par opérateur/semaine: {analysis['hours_per_operator_per_week']:.1f}h")

    

    print("\n📋 Besoins par article:")

    print(analysis['operator_requirements'].to_string(index=False))

    

    print("\n📋 Planning détaillé (premiers 30 shifts):")

    print(schedule_m2.head(30).to_string(index=False))

    print(f"\n... Total: {len(schedule_m2)} assignations de shifts")

    

    # Bilan d'atteinte des objectifs

    print("\n\n")

    print("=" * 100)

    print("BILAN D'ATTEINTE DES OBJECTIFS - MÉTHODE 2")

    print("=" * 100)

    

    # Calculer la production réelle par article

    production_reelle_m2 = schedule_m2.groupby('Item')['Quantité'].sum()

    

    bilan_data_m2 = []

    all_objectives_met_m2 = True

    

    for item_code, data in scheduler.items_data.items():

        objectif = data['weekly_demand']

        produit = production_reelle_m2.get(item_code, 0)

        atteint = produit >= objectif

        ecart = produit - objectif

        taux = (produit / objectif * 100) if objectif > 0 else 0

        

        if not atteint:

            all_objectives_met_m2 = False

        

        bilan_data_m2.append({

            'Item': item_code,

            'Objectif': objectif,

            'Produit': produit,

            'Écart': ecart,

            'Taux (%)': taux,

            'Statut': '✓' if atteint else '✗'

        })

    

    bilan_df_m2 = pd.DataFrame(bilan_data_m2)

    bilan_df_m2 = bilan_df_m2.sort_values('Item')

    

    print("\n📊 Détail par article:")

    print(bilan_df_m2.to_string(index=False))

    

    # Résumé global

    total_objectif_m2 = sum([d['weekly_demand'] for d in scheduler.items_data.values()])

    total_produit_m2 = production_reelle_m2.sum()

    taux_global_m2 = (total_produit_m2 / total_objectif_m2 * 100) if total_objectif_m2 > 0 else 0

    

    print("\n" + "=" * 100)

    print("RÉSUMÉ GLOBAL:")

    print(f"   Total objectif: {total_objectif_m2:.0f} unités")

    print(f"   Total produit: {total_produit_m2:.0f} unités")

    print(f"   Taux d'atteinte: {taux_global_m2:.1f}%")

    

    if all_objectives_met_m2:

        print("\n   ✓✓✓ TOUS LES OBJECTIFS SONT ATTEINTS! ✓✓✓")

    else:

        items_non_atteints_m2 = bilan_df_m2[bilan_df_m2['Statut'] == '✗']['Item'].tolist()

        print(f"\n   ✗ ATTENTION: {len(items_non_atteints_m2)} article(s) n'ont pas atteint l'objectif")

        print(f"   Articles concernés: {', '.join(items_non_atteints_m2)}")

    print("=" * 100)

    

    # Sauvegarder en Excel

    with pd.ExcelWriter('planning_methode2_operateurs_calcules.xlsx', engine='openpyxl') as writer:

        schedule_m2.to_excel(writer, sheet_name='Planning', index=False)

        analysis['operator_requirements'].to_excel(writer, sheet_name='Analyse besoins', index=False)

        bilan_df_m2.to_excel(writer, sheet_name='Bilan Objectifs', index=False)

    print("\n✓ Sauvegardé: planning_methode2_operateurs_calcules.xlsx")

    print("  - Feuille 1: Planning")

    print("  - Feuille 2: Analyse besoins")

    print("  - Feuille 3: Bilan Objectifs")

    

    # ===== COMPARAISON =====

    print("\n\n")

    print("=" * 100)

    print("COMPARAISON DES DEUX MÉTHODES")

    print("=" * 100)

    

    days_m1 = schedule_m1['Jour'].max()

    days_m2 = schedule_m2['Jour'].max()

    operators_m1 = schedule_m1['Opérateur'].nunique()

    operators_m2 = schedule_m2['Opérateur'].nunique()

    

    print(f"\nMÉTHODE 1 (Opérateurs fixes):")

    print(f"   - Opérateurs utilisés: {operators_m1}")

    print(f"   - Durée totale: {days_m1} jours")

    print(f"   - Shifts totaux: {len(schedule_m1)}")

    

    print(f"\nMÉTHODE 2 (Opérateurs calculés):")

    print(f"   - Opérateurs nécessaires: {operators_m2}")

    print(f"   - Durée totale: {days_m2} jours")

    print(f"   - Shifts totaux: {len(schedule_m2)}")

    

    print("\n" + "=" * 100)





if __name__ == "__main__":

    main()

