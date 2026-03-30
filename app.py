from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from models import db, Zone, Projet, Produit, Item, Assemblage, ObjectifMensuel, OrdreFabrication
from config import Config
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pandas as pd
from collections import defaultdict

""" Zohair """
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuration pour les uploads
    app.config['UPLOAD_FOLDER'] = 'static/uploads/items'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Fonctions helper pour les images
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def save_item_image(file):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            return filename
        return None
    
    # ============= ROUTES PRINCIPALES =============
    
    @app.route('/')
    def index():
        return redirect(url_for('dashboard'))
    
    @app.route('/dashboard')
    def dashboard():
        zones = Zone.query.all()
        stats = {
            'zones': Zone.query.count(),
            'projets': Projet.query.count(),
            'produits': Produit.query.count(),
            'items': Item.query.count(),
            'produits_finis': Produit.query.filter_by(type_produit='produit_fini').count(),
            'produits_semi_finis': Produit.query.filter_by(type_produit='produit_semi_fini').count()
        }
        return render_template('dashboard.html', zones=zones, stats=stats)
    
    # ============= ROUTES ZONES =============
    
    @app.route('/zones')
    def liste_zones():
        zones = Zone.query.all()
        return render_template('zones/liste.html', zones=zones)
    
    @app.route('/zone/creer', methods=['GET', 'POST'])
    def creer_zone():
        if request.method == 'POST':
            nom = request.form.get('nom')
            description = request.form.get('description')
            
            if not nom:
                flash('❌ Le nom de la zone est obligatoire', 'danger')
                return render_template('zones/creer.html')
            
            existing = Zone.query.filter_by(nom=nom).first()
            if existing:
                flash(f'❌ Une zone nommée "{nom}" existe déjà', 'danger')
                return render_template('zones/creer.html')
            
            zone = Zone(nom=nom, description=description)
            db.session.add(zone)
            db.session.commit()
            
            flash(f'✅ Zone "{nom}" créée avec succès!', 'success')
            return redirect(url_for('detail_zone', zone_id=zone.id))
        
        return render_template('zones/creer.html')
    
    @app.route('/zone/<int:zone_id>')
    def detail_zone(zone_id):
        zone = Zone.query.get_or_404(zone_id)
        return render_template('zones/detail.html', zone=zone)
    
    @app.route('/zone/<int:zone_id>/supprimer', methods=['POST'])
    def supprimer_zone(zone_id):
        zone = Zone.query.get_or_404(zone_id)
        nom = zone.nom
        db.session.delete(zone)
        db.session.commit()
        flash(f'✅ Zone "{nom}" supprimée avec succès!', 'success')
        return redirect(url_for('liste_zones'))
    
    # ============= ROUTES PROJETS =============
    
    @app.route('/zone/<int:zone_id>/projet/creer', methods=['GET', 'POST'])
    def creer_projet(zone_id):
        zone = Zone.query.get_or_404(zone_id)
        
        if request.method == 'POST':
            nom = request.form.get('nom')
            description = request.form.get('description')
            
            if not nom:
                flash('❌ Le nom du projet est obligatoire', 'danger')
                return render_template('projets/creer.html', zone=zone)
            
            projet = Projet(
                nom=nom,
                description=description,
                zone_id=zone_id
            )
            db.session.add(projet)
            db.session.commit()
            
            flash(f'✅ Projet "{nom}" créé avec succès!', 'success')
            return redirect(url_for('detail_projet', zone_id=zone_id, projet_id=projet.id))
        
        return render_template('projets/creer.html', zone=zone)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>')
    def detail_projet(zone_id, projet_id):
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        return render_template('projets/detail.html', zone=projet.zone, projet=projet)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/supprimer', methods=['POST'])
    def supprimer_projet(zone_id, projet_id):
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        nom = projet.nom
        db.session.delete(projet)
        db.session.commit()
        flash(f'✅ Projet "{nom}" supprimé avec succès!', 'success')
        return redirect(url_for('detail_zone', zone_id=zone_id))
    
    # ============= ROUTES PRODUITS =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/creer', methods=['GET', 'POST'])
    def creer_produit(zone_id, projet_id):
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        if request.method == 'POST':
            reference = request.form.get('reference')
            designation = request.form.get('designation')
            type_produit = request.form.get('type_produit', 'produit_fini')
            
            if not reference or not designation:
                flash('❌ La référence et la désignation sont obligatoires', 'danger')
                return render_template('produits/creer.html', zone=projet.zone, projet=projet)
            
            existing = Produit.query.filter_by(reference=reference).first()
            if existing:
                flash(f'❌ Un produit avec la référence "{reference}" existe déjà', 'danger')
                return render_template('produits/creer.html', zone=projet.zone, projet=projet)
            
            produit = Produit(
                reference=reference,
                designation=designation,
                type_produit=type_produit,
                projet_id=projet_id
            )
            db.session.add(produit)
            db.session.commit()
            
            flash(f'✅ Produit "{reference}" créé avec succès!', 'success')
            
            # Vérifier s'il y a une URL de retour
            retour = request.args.get('retour')
            if retour:
                return redirect(retour)
            
            return redirect(url_for('detail_produit', zone_id=zone_id, projet_id=projet_id, produit_id=produit.id))
        
        # Récupérer le type de produit depuis l'URL (pour pré-sélection)
        type_preselectionne = request.args.get('type', 'produit_fini')
        retour = request.args.get('retour')
        
        return render_template('produits/creer.html', 
                             zone=projet.zone, 
                             projet=projet,
                             type_preselectionne=type_preselectionne,
                             retour=retour)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/<int:produit_id>')
    def detail_produit(zone_id, projet_id, produit_id):
        produit = Produit.query.filter_by(id=produit_id, projet_id=projet_id).first_or_404()
        besoins = produit.calculer_besoins()
        
        # Si c'est un PSF, trouver les PF auxquels il appartient
        produits_finis_parents = []
        if produit.est_produit_semi_fini:
            assemblages_parents = Assemblage.query.filter_by(produit_compose_id=produit_id).all()
            for assemblage in assemblages_parents:
                if assemblage.produit_principal:  # Vérifier que le produit principal existe
                    produits_finis_parents.append({
                        'produit': assemblage.produit_principal,
                        'quantite': assemblage.quantite
                    })
        
        return render_template('produits/detail.html', 
                             zone=produit.projet.zone, 
                             projet=produit.projet, 
                             produit=produit,
                             besoins=besoins,
                             produits_finis_parents=produits_finis_parents)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/<int:produit_id>/supprimer', methods=['POST'])
    def supprimer_produit(zone_id, projet_id, produit_id):
        produit = Produit.query.filter_by(id=produit_id, projet_id=projet_id).first_or_404()
        reference = produit.reference
        db.session.delete(produit)
        db.session.commit()
        flash(f'✅ Produit "{reference}" supprimé avec succès!', 'success')
        return redirect(url_for('detail_projet', zone_id=zone_id, projet_id=projet_id))
    
    # ============= ROUTES ITEMS =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/<int:produit_id>/item/ajouter', methods=['GET', 'POST'])
    def ajouter_item(zone_id, projet_id, produit_id):
        produit = Produit.query.filter_by(id=produit_id, projet_id=projet_id).first_or_404()
        
        if request.method == 'POST':
            reference = request.form.get('reference')
            designation = request.form.get('designation')
            quantite = float(request.form.get('quantite', 1.0))
            unite_mesure = request.form.get('unite_mesure', 'pièce')
            
            if not reference or not designation:
                flash('❌ La référence et la désignation sont obligatoires', 'danger')
                return render_template('items/ajouter.html', zone=produit.projet.zone, projet=produit.projet, produit=produit)
            
            existing = Item.query.filter_by(reference=reference).first()
            if existing:
                flash(f'❌ Un item avec la référence "{reference}" existe déjà', 'danger')
                return render_template('items/ajouter.html', zone=produit.projet.zone, projet=produit.projet, produit=produit)
            
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file.filename:
                    image_filename = save_item_image(file)
            
            item = Item(
                reference=reference,
                designation=designation,
                quantite=quantite,
                unite_mesure=unite_mesure,
                image_path=image_filename,
                produit_id=produit_id
            )
            db.session.add(item)
            db.session.commit()
            
            flash(f'✅ Item "{reference}" ajouté avec succès!', 'success')
            return redirect(url_for('detail_produit', zone_id=zone_id, projet_id=projet_id, produit_id=produit_id))
        
        return render_template('items/ajouter.html', zone=produit.projet.zone, projet=produit.projet, produit=produit)
    
    @app.route('/item/<int:item_id>/supprimer', methods=['POST'])
    def supprimer_item(item_id):
        item = Item.query.get_or_404(item_id)
        produit = item.produit
        reference = item.reference
        db.session.delete(item)
        db.session.commit()
        flash(f'✅ Item "{reference}" supprimé avec succès!', 'success')
        return redirect(url_for('detail_produit', 
                              zone_id=produit.projet.zone_id, 
                              projet_id=produit.projet_id, 
                              produit_id=produit.id))
    
    # ============= ROUTES ASSEMBLAGES =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/<int:produit_id>/assemblage/ajouter', methods=['GET', 'POST'])
    def ajouter_assemblage(zone_id, projet_id, produit_id):
        produit = Produit.query.filter_by(id=produit_id, projet_id=projet_id).first_or_404()
        
        if request.method == 'POST':
            # Récupérer les données du PSF
            reference_psf = request.form.get('reference_psf')
            designation_psf = request.form.get('designation_psf')
            quantite_psf = float(request.form.get('quantite_psf', 1.0))
            
            if not reference_psf or not designation_psf:
                flash('❌ La référence et la désignation du PSF sont obligatoires', 'danger')
                return redirect(url_for('ajouter_assemblage', zone_id=zone_id, projet_id=projet_id, produit_id=produit_id))
            
            # Vérifier si la référence existe déjà
            existing = Produit.query.filter_by(reference=reference_psf).first()
            if existing:
                flash(f'❌ Un produit avec la référence "{reference_psf}" existe déjà', 'danger')
                return redirect(url_for('ajouter_assemblage', zone_id=zone_id, projet_id=projet_id, produit_id=produit_id))
            
            # Créer le PSF
            psf = Produit(
                reference=reference_psf,
                designation=designation_psf,
                type_produit='produit_semi_fini',
                projet_id=projet_id
            )
            db.session.add(psf)
            db.session.flush()  # Pour obtenir l'ID du PSF
            
            # Ajouter les matières premières
            mp_references = request.form.getlist('mp_reference[]')
            mp_designations = request.form.getlist('mp_designation[]')
            mp_quantites = request.form.getlist('mp_quantite[]')
            mp_unites = request.form.getlist('mp_unite[]')
            
            for i in range(len(mp_references)):
                if mp_references[i] and mp_designations[i]:
                    # Vérifier si cette MP existe déjà pour CE PSF spécifiquement
                    existing_mp = Item.query.filter_by(
                        reference=mp_references[i],
                        produit_id=psf.id
                    ).first()
                    
                    if not existing_mp:
                        mp = Item(
                            reference=mp_references[i],
                            designation=mp_designations[i],
                            quantite=float(mp_quantites[i]),
                            unite_mesure=mp_unites[i],
                            produit_id=psf.id
                        )
                        db.session.add(mp)
            
            # Créer l'assemblage
            assemblage = Assemblage(
                produit_principal_id=produit_id,
                produit_compose_id=psf.id,
                quantite=quantite_psf
            )
            db.session.add(assemblage)
            
            db.session.commit()
            
            flash(f'✅ PSF "{reference_psf}" créé avec ses matières premières et ajouté au produit fini!', 'success')
            return redirect(url_for('detail_produit', zone_id=zone_id, projet_id=projet_id, produit_id=produit_id))
        
        return render_template('produits/ajouter_psf.html',
                             zone=produit.projet.zone,
                             projet=produit.projet,
                             produit=produit)
    
    # ============= ROUTE MODIFICATION PSF =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/<int:produit_id>/modifier', methods=['GET', 'POST'])
    def modifier_psf(zone_id, projet_id, produit_id):
        produit = Produit.query.filter_by(id=produit_id, projet_id=projet_id).first_or_404()
        
        if request.method == 'POST':
            # Mettre à jour les informations du PSF
            produit.reference = request.form.get('reference_psf')
            produit.designation = request.form.get('designation_psf')
            
            # Supprimer les anciennes MP si demandé
            mp_ids_a_supprimer = request.form.getlist('mp_supprimer[]')
            for mp_id in mp_ids_a_supprimer:
                if mp_id:
                    mp = Item.query.get(int(mp_id))
                    if mp and mp.produit_id == produit_id:
                        db.session.delete(mp)
            
            # Ajouter les nouvelles MP
            mp_references = request.form.getlist('mp_reference[]')
            mp_designations = request.form.getlist('mp_designation[]')
            mp_quantites = request.form.getlist('mp_quantite[]')
            mp_unites = request.form.getlist('mp_unite[]')
            
            print(f"DEBUG - MP reçues: {len(mp_references)} références")
            print(f"DEBUG - Références: {mp_references}")
            print(f"DEBUG - Désignations: {mp_designations}")
            print(f"DEBUG - Quantités: {mp_quantites}")
            
            mp_ajoutees = 0
            for i in range(len(mp_references)):
                if mp_references[i] and mp_designations[i]:
                    # Vérifier si cette MP existe déjà pour CE produit
                    existing_mp = Item.query.filter_by(
                        reference=mp_references[i],
                        produit_id=produit_id
                    ).first()
                    
                    if not existing_mp:
                        mp = Item(
                            reference=mp_references[i],
                            designation=mp_designations[i],
                            quantite=float(mp_quantites[i]),
                            unite_mesure=mp_unites[i],
                            produit_id=produit_id
                        )
                        db.session.add(mp)
                        mp_ajoutees += 1
            
            db.session.commit()
            
            if mp_ajoutees > 0:
                flash(f'✅ PSF "{produit.reference}" modifié avec succès! {mp_ajoutees} MP ajoutée(s).', 'success')
            else:
                flash(f'✅ PSF "{produit.reference}" modifié avec succès!', 'success')
            
            return redirect(url_for('detail_produit', zone_id=zone_id, projet_id=projet_id, produit_id=produit_id))
        
        return render_template('produits/modifier_psf.html',
                             zone=produit.projet.zone,
                             projet=produit.projet,
                             produit=produit)
    
    # ============= ROUTE NOMENCLATURE =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/produit/<int:produit_id>/nomenclature')
    def nomenclature_produit(zone_id, projet_id, produit_id):
        produit = Produit.query.filter_by(id=produit_id, projet_id=projet_id).first_or_404()
        
        # Construire l'arbre de nomenclature
        def construire_arbre_nomenclature(produit, niveau=0):
            print(f"DEBUG - Niveau {niveau}: Produit {produit.reference}")
            
            # Récupérer les items directement via query
            items_list = Item.query.filter_by(produit_id=produit.id).all()
            print(f"DEBUG - Items trouvés: {len(items_list)}")
            
            arbre = {
                'produit': produit,
                'niveau': niveau,
                'matieres_premieres': items_list,
                'composants': []
            }
            
            # Ajouter les produits semi-finis assemblés
            assemblages_list = Assemblage.query.filter_by(produit_principal_id=produit.id).all()
            print(f"DEBUG - Assemblages trouvés: {len(assemblages_list)}")
            
            for assemblage in assemblages_list:
                if assemblage.produit_compose:  # Vérifier que le produit existe
                    print(f"DEBUG - Assemblage vers: {assemblage.produit_compose.reference}")
                    sous_arbre = construire_arbre_nomenclature(assemblage.produit_compose, niveau + 1)
                    composant = {
                        'assemblage': assemblage,
                        'sous_arbre': sous_arbre
                    }
                    arbre['composants'].append(composant)
                    print(f"DEBUG - Type sous_arbre: {type(sous_arbre)}")
            
            return arbre
        
        nomenclature = construire_arbre_nomenclature(produit)
        
        # Calculer le bilan total
        from collections import defaultdict
        
        # Besoins en PSF
        psf_besoins = []
        assemblages_list = Assemblage.query.filter_by(produit_principal_id=produit.id).all()
        for assemblage in assemblages_list:
            if assemblage.produit_compose:
                psf_besoins.append({
                    'reference': assemblage.produit_compose.reference,
                    'designation': assemblage.produit_compose.designation,
                    'quantite': assemblage.quantite
                })
        
        # Besoins totaux en MP (calculés récursivement)
        mp_totaux = defaultdict(lambda: {'designation': '', 'quantite': 0.0, 'unite': ''})
        
        def calculer_mp_recursif(prod, multiplicateur=1.0, niveau=0):
            indent = "  " * niveau
            print(f"{indent}DEBUG MP - Produit: {prod.reference}, Multiplicateur: {multiplicateur}")
            
            # MP directes de ce produit
            items = Item.query.filter_by(produit_id=prod.id).all()
            print(f"{indent}DEBUG MP - {len(items)} items trouvés pour {prod.reference}")
            
            for item in items:
                qte_avant = mp_totaux[item.reference]['quantite']
                mp_totaux[item.reference]['designation'] = item.designation
                mp_totaux[item.reference]['quantite'] += item.quantite * multiplicateur
                mp_totaux[item.reference]['unite'] = item.unite_mesure
                print(f"{indent}  → {item.reference}: {qte_avant} + ({item.quantite} × {multiplicateur}) = {mp_totaux[item.reference]['quantite']}")
            
            # MP des PSF composants
            assemblages = Assemblage.query.filter_by(produit_principal_id=prod.id).all()
            print(f"{indent}DEBUG MP - {len(assemblages)} assemblages pour {prod.reference}")
            
            for assemblage in assemblages:
                if assemblage.produit_compose:
                    print(f"{indent}  → Descente vers PSF: {assemblage.produit_compose.reference} (qté: {assemblage.quantite})")
                    calculer_mp_recursif(assemblage.produit_compose, multiplicateur * assemblage.quantite, niveau + 1)
        
        calculer_mp_recursif(produit)
        
        print(f"\n=== RÉSUMÉ MP TOTAUX ===")
        for ref, data in mp_totaux.items():
            print(f"{ref}: {data['quantite']} {data['unite']}")
        
        # Convertir en liste triée
        mp_totaux_liste = [
            {
                'reference': ref,
                'designation': data['designation'],
                'quantite': data['quantite'],
                'unite': data['unite']
            }
            for ref, data in sorted(mp_totaux.items())
        ]
        
        return render_template('produits/nomenclature.html',
                             zone=produit.projet.zone,
                             projet=produit.projet,
                             produit=produit,
                             nomenclature=nomenclature,
                             psf_besoins=psf_besoins,
                             mp_totaux=mp_totaux_liste)
    
    # ============= ROUTE IMPORTATION EXCEL BOM =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/importer-bom', methods=['GET', 'POST'])
    def importer_bom_excel(zone_id, projet_id):
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        if request.method == 'POST':
            if 'fichier_excel' not in request.files:
                flash('❌ Aucun fichier sélectionné', 'danger')
                return redirect(request.url)
            
            file = request.files['fichier_excel']
            
            if file.filename == '':
                flash('❌ Aucun fichier sélectionné', 'danger')
                return redirect(request.url)
            
            if not file.filename.endswith(('.xlsx', '.xls')):
                flash('❌ Le fichier doit être au format Excel (.xlsx ou .xls)', 'danger')
                return redirect(request.url)
            
            try:
                # Lire le fichier Excel
                df = pd.read_excel(file)
                
                # Normaliser les noms de colonnes (insensible à la casse)
                df.columns = df.columns.str.strip()
                column_mapping = {}
                for col in df.columns:
                    col_lower = col.lower()
                    if col_lower == 'parentitem':
                        column_mapping[col] = 'ParentItem'
                    elif col_lower == 'childitem':
                        column_mapping[col] = 'ChildItem'
                    elif col_lower == 'name':
                        column_mapping[col] = 'NAME'
                    elif col_lower == 'bomqty':
                        column_mapping[col] = 'BOMQTY'
                    elif col_lower == 'unitid':
                        column_mapping[col] = 'UNITID'
                    elif col_lower == 'level':
                        column_mapping[col] = 'Level'
                
                df = df.rename(columns=column_mapping)
                
                # Vérifier les colonnes requises
                colonnes_requises = ['ParentItem', 'ChildItem', 'NAME', 'BOMQTY', 'UNITID', 'Level']
                colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
                
                if colonnes_manquantes:
                    flash(f'❌ Colonnes manquantes dans le fichier Excel: {", ".join(colonnes_manquantes)}', 'danger')
                    return redirect(request.url)
                
                # Nettoyer les données
                df = df.dropna(subset=['ParentItem', 'ChildItem'])
                
                # Identifier les produits finis (ParentItem qui n'apparaissent jamais comme ChildItem au niveau 1)
                level_1_items = df[df['Level'] == 1]
                finished_goods = level_1_items['ParentItem'].unique()
                
                # Identifier les PSF: ChildItem de niveau 1 qui ont des composants de niveau 2
                # On extrait les codes parents de la colonne NAME au niveau 2
                psf_codes = set()
                level_2_items = df[df['Level'] == 2]
                for _, row in level_2_items.iterrows():
                    name = row['NAME']
                    if pd.notna(name) and '-' in name:
                        parent_code = name.split('-')[0]
                        psf_codes.add(parent_code)
                
                print(f"DEBUG - Produits finis détectés: {list(finished_goods)}")
                print(f"DEBUG - PSF détectés: {list(psf_codes)}")
                
                # Dictionnaire pour stocker les produits créés
                produits_crees = {}
                items_crees = {}
                
                # Statistiques
                stats = {
                    'produits_finis': 0,
                    'produits_semi_finis': 0,
                    'matieres_premieres': 0,
                    'assemblages': 0
                }
                
                # Étape 1: Créer tous les produits finis
                for fg_code in finished_goods:
                    if fg_code not in produits_crees:
                        # Récupérer le nom du produit fini
                        fg_row = df[df['ParentItem'] == fg_code].iloc[0]
                        fg_name = fg_row['NAME'] if pd.notna(fg_row['NAME']) else fg_code
                        
                        # Vérifier si le produit existe déjà
                        existing = Produit.query.filter_by(reference=fg_code, projet_id=projet_id).first()
                        if not existing:
                            produit_fini = Produit(
                                reference=fg_code,
                                designation=fg_name,
                                type_produit='produit_fini',
                                projet_id=projet_id
                            )
                            db.session.add(produit_fini)
                            db.session.flush()
                            produits_crees[fg_code] = produit_fini
                            stats['produits_finis'] += 1
                        else:
                            produits_crees[fg_code] = existing
                
                # Étape 2: Traiter les composants niveau par niveau
                for niveau in sorted(df['Level'].unique()):
                    niveau_data = df[df['Level'] == niveau]
                    
                    for _, row in niveau_data.iterrows():
                        parent_code = row['ParentItem']
                        child_code = row['ChildItem']
                        qty = row['BOMQTY']
                        unit = row['UNITID'] if pd.notna(row['UNITID']) else 'EA'
                        child_name = row['NAME'] if pd.notna(row['NAME']) else child_code
                        
                        # Pour les niveaux 2+, le vrai parent est indiqué dans la colonne NAME
                        # Exemple: NAME = "M308000-01" signifie que le parent est M308000
                        if niveau >= 2:
                            # Extraire le code parent de la colonne NAME (avant le tiret)
                            if pd.notna(child_name) and '-' in child_name:
                                real_parent_code = child_name.split('-')[0]
                                if real_parent_code in produits_crees:
                                    parent_produit = produits_crees[real_parent_code]
                                else:
                                    # Si le parent n'existe pas, ignorer cette ligne
                                    continue
                            else:
                                # Si pas de format reconnu, utiliser ParentItem
                                if parent_code not in produits_crees:
                                    continue
                                parent_produit = produits_crees[parent_code]
                        else:
                            # Pour niveau 1, utiliser ParentItem normalement
                            if parent_code not in produits_crees:
                                continue
                            parent_produit = produits_crees[parent_code]
                        
                        # Déterminer si le child est un PSF ou une MP
                        # Un child est un PSF s'il a été détecté dans psf_codes (via la colonne NAME niveau 2)
                        est_psf = child_code in psf_codes
                        
                        if niveau == 1:
                            print(f"  [Niveau {niveau}] {child_code} → {'PSF' if est_psf else 'MP'}")
                        
                        if est_psf:
                            # Créer ou récupérer le PSF
                            if child_code not in produits_crees:
                                existing_psf = Produit.query.filter_by(reference=child_code, projet_id=projet_id).first()
                                if not existing_psf:
                                    psf = Produit(
                                        reference=child_code,
                                        designation=child_name,
                                        type_produit='produit_semi_fini',
                                        projet_id=projet_id
                                    )
                                    db.session.add(psf)
                                    db.session.flush()
                                    produits_crees[child_code] = psf
                                    stats['produits_semi_finis'] += 1
                                    print(f"    ✓ PSF créé: {child_code} (type: produit_semi_fini)")
                                else:
                                    produits_crees[child_code] = existing_psf
                                    print(f"    ⚠ PSF existe déjà: {child_code}")
                            
                            # Créer l'assemblage
                            child_produit = produits_crees[child_code]
                            existing_assemblage = Assemblage.query.filter_by(
                                produit_principal_id=parent_produit.id,
                                produit_compose_id=child_produit.id
                            ).first()
                            
                            if not existing_assemblage:
                                assemblage = Assemblage(
                                    produit_principal_id=parent_produit.id,
                                    produit_compose_id=child_produit.id,
                                    quantite=qty
                                )
                                db.session.add(assemblage)
                                stats['assemblages'] += 1
                                print(f"    ✓ Assemblage créé: {parent_produit.reference} → {child_code} (qté: {qty})")
                        else:
                            # C'est une matière première
                            item_key = f"{parent_produit.reference}_{child_code}"
                            print(f"  [Niveau {niveau}] MP: {child_code} → Parent: {parent_produit.reference} (Qté: {qty} {unit})")
                            
                            if item_key not in items_crees:
                                existing_item = Item.query.filter_by(
                                    reference=child_code,
                                    produit_id=parent_produit.id
                                ).first()
                                
                                if not existing_item:
                                    item = Item(
                                        reference=child_code,
                                        designation=child_name,
                                        quantite=qty,
                                        unite_mesure=unit,
                                        produit_id=parent_produit.id
                                    )
                                    db.session.add(item)
                                    items_crees[item_key] = item
                                    stats['matieres_premieres'] += 1
                                    print(f"    ✓ MP créée: {child_code} attachée à {parent_produit.reference}")
                                else:
                                    print(f"    ⚠ MP existe déjà: {child_code} pour {parent_produit.reference}")
                            else:
                                print(f"    ⚠ Item key existe déjà: {item_key}")
                
                # Commit toutes les modifications
                db.session.commit()
                
                flash(f'✅ Importation réussie! {stats["produits_finis"]} produits finis, '
                      f'{stats["produits_semi_finis"]} PSF, {stats["matieres_premieres"]} MP, '
                      f'{stats["assemblages"]} assemblages créés.', 'success')
                
                return redirect(url_for('detail_projet', zone_id=zone_id, projet_id=projet_id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Erreur lors de l\'importation: {str(e)}', 'danger')
                return redirect(request.url)
        
        return render_template('projets/importer_bom.html', zone=projet.zone, projet=projet)
    
    # ============= ROUTES MODULE OF =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/of')
    def module_of_projet(zone_id, projet_id):
        """Module de gestion des OF pour un projet spécifique"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        # Récupérer le filtre de statut
        statut_filtre = request.args.get('statut', 'tous')
        
        # Construire la requête
        query = OrdreFabrication.query.filter_by(projet_id=projet_id)
        
        if statut_filtre == 'en_cours':
            query = query.filter_by(statut='en_cours')
        elif statut_filtre == 'termine':
            query = query.filter_by(statut='termine')
        elif statut_filtre == 'en_attente':
            query = query.filter_by(statut='en_attente')
        
        ordres = query.order_by(OrdreFabrication.date_creation.desc()).all()
        
        # Statistiques
        stats = {
            'total': OrdreFabrication.query.filter_by(projet_id=projet_id).count(),
            'en_cours': OrdreFabrication.query.filter_by(projet_id=projet_id, statut='en_cours').count(),
            'termine': OrdreFabrication.query.filter_by(projet_id=projet_id, statut='termine').count(),
            'en_attente': OrdreFabrication.query.filter_by(projet_id=projet_id, statut='en_attente').count()
        }
        
        return render_template('of/liste.html', 
                             zone=projet.zone, 
                             projet=projet, 
                             ordres=ordres,
                             stats=stats,
                             statut_filtre=statut_filtre)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/of/creer', methods=['GET', 'POST'])
    def creer_of(zone_id, projet_id):
        """Créer un nouvel OF"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        if request.method == 'POST':
            try:
                # Générer le numéro d'OF
                dernier_of = OrdreFabrication.query.order_by(OrdreFabrication.id.desc()).first()
                if dernier_of:
                    dernier_num = int(dernier_of.numero_of.split('-')[-1])
                    nouveau_num = dernier_num + 1
                else:
                    nouveau_num = 1
                
                numero_of = f"OF-{datetime.now().year}-{nouveau_num:04d}"
                
                # Créer l'OF
                of = OrdreFabrication(
                    numero_of=numero_of,
                    projet_id=projet_id,
                    produit_id=request.form['produit_id'],
                    quantite_demandee=int(request.form['quantite_demandee']),
                    date_lancement=datetime.strptime(request.form['date_lancement'], '%Y-%m-%d').date() if request.form.get('date_lancement') else None,
                    date_livraison_prevue=datetime.strptime(request.form['date_livraison_prevue'], '%Y-%m-%d').date() if request.form.get('date_livraison_prevue') else None,
                    priorite_edd=int(request.form.get('priorite_edd', 5)),
                    temps_cycle=float(request.form['temps_cycle']) if request.form.get('temps_cycle') else None,
                    capacite_par_operateur=float(request.form['capacite_par_operateur']) if request.form.get('capacite_par_operateur') else None,
                    efficience=float(request.form.get('efficience', 1.0)),
                    commentaire=request.form.get('commentaire', '')
                )
                
                db.session.add(of)
                db.session.commit()
                
                flash(f'✅ OF {numero_of} créé avec succès!', 'success')
                return redirect(url_for('module_of_projet', zone_id=zone_id, projet_id=projet_id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Erreur lors de la création de l\'OF: {str(e)}', 'danger')
        
        # Récupérer les produits du projet pour le formulaire
        produits = Produit.query.filter_by(projet_id=projet_id, type_produit='produit_fini').all()
        
        return render_template('of/creer.html', zone=projet.zone, projet=projet, produits=produits)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/of/importer', methods=['GET', 'POST'])
    def importer_of_excel(zone_id, projet_id):
        """Importer des OF depuis un fichier Excel"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        if request.method == 'POST':
            if 'fichier_excel' not in request.files:
                flash('❌ Aucun fichier sélectionné', 'danger')
                return redirect(request.url)
            
            file = request.files['fichier_excel']
            
            if file.filename == '':
                flash('❌ Aucun fichier sélectionné', 'danger')
                return redirect(request.url)
            
            try:
                df = pd.read_excel(file)
                
                # Colonnes attendues
                colonnes_requises = ['Produit', 'Quantite', 'DateLancement', 'DateLivraison', 'PrioriteEDD']
                colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
                
                if colonnes_manquantes:
                    flash(f'❌ Colonnes manquantes: {", ".join(colonnes_manquantes)}', 'danger')
                    return redirect(request.url)
                
                stats = {'crees': 0, 'erreurs': 0}
                
                for _, row in df.iterrows():
                    try:
                        # Trouver le produit
                        produit = Produit.query.filter_by(reference=row['Produit'], projet_id=projet_id).first()
                        
                        if not produit:
                            stats['erreurs'] += 1
                            continue
                        
                        # Générer numéro OF
                        dernier_of = OrdreFabrication.query.order_by(OrdreFabrication.id.desc()).first()
                        if dernier_of:
                            dernier_num = int(dernier_of.numero_of.split('-')[-1])
                            nouveau_num = dernier_num + 1
                        else:
                            nouveau_num = 1
                        
                        numero_of = f"OF-{datetime.now().year}-{nouveau_num:04d}"
                        
                        of = OrdreFabrication(
                            numero_of=numero_of,
                            projet_id=projet_id,
                            produit_id=produit.id,
                            quantite_demandee=int(row['Quantite']),
                            date_lancement=pd.to_datetime(row['DateLancement']).date() if pd.notna(row['DateLancement']) else None,
                            date_livraison_prevue=pd.to_datetime(row['DateLivraison']).date() if pd.notna(row['DateLivraison']) else None,
                            priorite_edd=int(row['PrioriteEDD']) if pd.notna(row['PrioriteEDD']) else 5,
                            temps_cycle=float(row['TempsCycle']) if 'TempsCycle' in row and pd.notna(row['TempsCycle']) else None,
                            capacite_par_operateur=float(row['CapaciteOperateur']) if 'CapaciteOperateur' in row and pd.notna(row['CapaciteOperateur']) else None
                        )
                        
                        db.session.add(of)
                        stats['crees'] += 1
                        
                    except Exception as e:
                        print(f"Erreur ligne: {e}")
                        stats['erreurs'] += 1
                        continue
                
                db.session.commit()
                flash(f'✅ {stats["crees"]} OF importés, {stats["erreurs"]} erreurs', 'success')
                return redirect(url_for('module_of_projet', zone_id=zone_id, projet_id=projet_id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Erreur: {str(e)}', 'danger')
        
        return render_template('of/importer.html', zone=projet.zone, projet=projet)
    
    # ============= ROUTES ORDONNANCEMENT =============
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/ordonnancement')
    def projet_ordonnancement(zone_id, projet_id):
        """Page dédiée au projet avec les 3 options d'ordonnancement"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        # Statistiques rapides
        nb_of_total = OrdreFabrication.query.filter_by(projet_id=projet_id).count()
        nb_of_en_cours = OrdreFabrication.query.filter_by(projet_id=projet_id, statut='en_cours').count()
        
        # Vérifier si un planning existe
        from flask import session
        planning_existe = f'planning_projet_{projet_id}' in session
        
        return render_template('ordonnancement/projet.html',
                             zone=projet.zone,
                             projet=projet,
                             nb_of_total=nb_of_total,
                             nb_of_en_cours=nb_of_en_cours,
                             planning_existe=planning_existe)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/ordonnancement/config', methods=['GET', 'POST'])
    def config_ordonnancement(zone_id, projet_id):
        """Configuration des paramètres d'ordonnancement"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        # Récupérer les OF sélectionnables (en attente ou en cours)
        ordres_disponibles = OrdreFabrication.query.filter_by(projet_id=projet_id)\
            .filter(OrdreFabrication.statut.in_(['en_attente', 'en_cours'])).all()
        
        return render_template('ordonnancement/config.html', 
                             zone=projet.zone, 
                             projet=projet,
                             ordres_disponibles=ordres_disponibles)
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/ordonnancement/generer', methods=['POST'])
    def generer_ordonnancement(zone_id, projet_id):
        """Générer le planning d'ordonnancement avec la méthode 1"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        try:
            # Récupérer les OF sélectionnés
            of_ids = request.form.getlist('of_ids')
            
            if not of_ids:
                flash('❌ Veuillez sélectionner au moins un OF à ordonnancer', 'danger')
                return redirect(url_for('config_ordonnancement', zone_id=zone_id, projet_id=projet_id))
            
            # Convertir en entiers
            of_ids = [int(id) for id in of_ids]
            
            # Récupérer les paramètres des shifts
            operators_per_shift = {
                1: int(request.form.get('shift1_operators', 8)),
                2: int(request.form.get('shift2_operators', 9)),
                3: int(request.form.get('shift3_operators', 10))
            }
            
            absences_per_shift = {
                1: int(request.form.get('shift1_absences', 0)),
                2: int(request.form.get('shift2_absences', 0)),
                3: int(request.form.get('shift3_absences', 0))
            }
            
            params = {
                'operators_per_shift': operators_per_shift,
                'absences_per_shift': absences_per_shift
            }
            
            # Générer le planning
            from ordonnancement_engine import generer_planning_depuis_of
            planning_data = generer_planning_depuis_of(projet_id, of_ids, params)
            
            # Sauvegarder dans la session Flask
            from flask import session
            session[f'planning_projet_{projet_id}'] = {
                'assignments': planning_data['assignments'],
                'stats': planning_data['stats'],
                'of_details': planning_data['of_details'],
                'params': params,
                'date_generation': datetime.now().isoformat()
            }
            
            flash(f'✅ Planning généré avec succès! {planning_data["stats"]["nb_shifts"]} shifts planifiés sur {planning_data["stats"]["duree_jours"]} jours', 'success')
            return redirect(url_for('voir_ordonnancement', zone_id=zone_id, projet_id=projet_id))
            
        except Exception as e:
            flash(f'❌ Erreur lors de la génération du planning: {str(e)}', 'danger')
            return redirect(url_for('config_ordonnancement', zone_id=zone_id, projet_id=projet_id))
    
    @app.route('/zone/<int:zone_id>/projet/<int:projet_id>/ordonnancement/planning')
    def voir_ordonnancement(zone_id, projet_id):
        """Afficher le planning d'ordonnancement généré"""
        projet = Projet.query.filter_by(id=projet_id, zone_id=zone_id).first_or_404()
        
        # Charger les résultats depuis la session
        from flask import session
        planning_data = session.get(f'planning_projet_{projet_id}')
        
        return render_template('ordonnancement/planning.html', 
                             zone=projet.zone, 
                             projet=projet,
                             planning_data=planning_data)
    
    @app.route('/ordonnancement')
    def ordonnancement():
        zones = Zone.query.all()
        return render_template('ordonnancement/index.html', zones=zones)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
