from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from models import db, Zone, Projet, Produit, Item, Assemblage, ObjectifMensuel
from config import Config
from datetime import datetime
import os
from werkzeug.utils import secure_filename

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
        
        def calculer_mp_recursif(prod, multiplicateur=1.0):
            # MP directes de ce produit
            items = Item.query.filter_by(produit_id=prod.id).all()
            for item in items:
                mp_totaux[item.reference]['designation'] = item.designation
                mp_totaux[item.reference]['quantite'] += item.quantite * multiplicateur
                mp_totaux[item.reference]['unite'] = item.unite_mesure
            
            # MP des PSF composants
            assemblages = Assemblage.query.filter_by(produit_principal_id=prod.id).all()
            for assemblage in assemblages:
                if assemblage.produit_compose:
                    calculer_mp_recursif(assemblage.produit_compose, multiplicateur * assemblage.quantite)
        
        calculer_mp_recursif(produit)
        
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
    
    # ============= ROUTE ORDONNANCEMENT =============
    
    @app.route('/ordonnancement')
    def ordonnancement():
        zones = Zone.query.all()
        return render_template('ordonnancement/index.html', zones=zones)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
