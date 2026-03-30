from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Zone(db.Model):
    """Une zone de travail (ex: A320 DAHER)"""
    __tablename__ = 'zones'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    projets = db.relationship('Projet', backref='zone', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Zone {self.nom}>'


class Projet(db.Model):
    """Un projet dans une zone (ex: BF, FF, DF, leg, hing)"""
    __tablename__ = 'projets'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Un projet contient plusieurs produits
    produits = db.relationship('Produit', backref='projet', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Projet {self.nom}>'


class Produit(db.Model):
    """Un produit dans un projet
    Chaque produit peut être soit un Produit Fini, soit un Produit Semi-Fini"""
    __tablename__ = 'produits'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    designation = db.Column(db.String(200), nullable=False)
    projet_id = db.Column(db.Integer, db.ForeignKey('projets.id'), nullable=False)
    
    # Type de produit : 'produit_fini' ou 'produit_semi_fini'
    type_produit = db.Column(db.String(20), nullable=False, default='produit_fini')
    
    # Relation avec les items
    items = db.relationship('Item', backref='produit', lazy='dynamic', cascade='all, delete-orphan')
    
    # Assemblages : un produit fini peut être composé de produits semi-finis
    assemblages = db.relationship(
        'Assemblage',
        foreign_keys='Assemblage.produit_principal_id',
        backref='produit_principal',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def est_produit_fini(self):
        return self.type_produit == 'produit_fini'
    
    @property
    def est_produit_semi_fini(self):
        return self.type_produit == 'produit_semi_fini'
    
    def get_produits_assembles(self):
        """Retourne la liste des produits semi-finis assemblés avec ce produit"""
        return [assemblage.produit_compose for assemblage in self.assemblages.all()]
    
    def calculer_besoins(self):
        """Calcule les besoins totaux en items pour ce produit"""
        from collections import defaultdict
        
        besoins = defaultdict(float)
        items_info = {}
        
        # Ajouter les items directs de ce produit
        for item in self.items.all():
            besoins[item.id] += item.quantite
            items_info[item.id] = item
        
        # Si c'est un produit fini composé de semi-finis, ajouter leurs items
        if self.est_produit_fini:
            for assemblage in self.assemblages.all():
                produit_compose = assemblage.produit_compose
                if produit_compose:  # Vérifier que le produit existe
                    for item in produit_compose.items.all():
                        quantite_totale = item.quantite * assemblage.quantite
                        besoins[item.id] += quantite_totale
                        items_info[item.id] = item
        
        # Préparer le résultat
        resultat = []
        for item_id, quantite in besoins.items():
            item = items_info[item_id]
            resultat.append({
                'item': item,
                'quantite': quantite,
                'unite': item.unite_mesure
            })
        
        return sorted(resultat, key=lambda x: x['item'].reference)
    
    def __repr__(self):
        return f'<Produit {self.reference} - {self.designation}>'


class Assemblage(db.Model):
    """Table d'association pour l'assemblage de produits semi-finis"""
    __tablename__ = 'assemblages'
    
    id = db.Column(db.Integer, primary_key=True)
    produit_principal_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    produit_compose_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    quantite = db.Column(db.Float, default=1.0, nullable=False)
    
    produit_compose = db.relationship('Produit', foreign_keys=[produit_compose_id])
    
    def __repr__(self):
        return f'<Assemblage {self.produit_principal_id} <- {self.produit_compose_id}>'


class Item(db.Model):
    """Un item (article) appartient à un produit"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(200), nullable=False)
    quantite = db.Column(db.Float, nullable=False, default=1.0)
    unite_mesure = db.Column(db.String(20), default='pièce')
    image_path = db.Column(db.String(255), nullable=True)
    
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def image_url(self):
        if self.image_path:
            return f'/static/uploads/items/{self.image_path}'
        return '/static/img/no-image.png'
    
    def __repr__(self):
        return f'<Item {self.reference} - {self.designation}>'


class ObjectifMensuel(db.Model):
    """Objectifs mensuels pour un produit"""
    __tablename__ = 'objectifs_mensuels'
    
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    mois = db.Column(db.Date, nullable=False)
    quantite_objectif = db.Column(db.Integer, nullable=False)
    quantite_realisee = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('produit_id', 'mois', name='_produit_mois_uc'),
    )
    
    def __repr__(self):
        return f'<ObjectifMensuel {self.produit_id} - {self.mois}>'


class OrdreFabrication(db.Model):
    """Ordre de Fabrication (OF) pour un projet"""
    __tablename__ = 'ordres_fabrication'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_of = db.Column(db.String(50), unique=True, nullable=False)  # Production order number
    projet_id = db.Column(db.Integer, db.ForeignKey('projets.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    
    # Informations de base
    item_number = db.Column(db.String(50), nullable=True)  # Item number
    name = db.Column(db.String(200), nullable=True)  # Name
    property_field = db.Column(db.String(100), nullable=True)  # Property
    unit = db.Column(db.String(20), default='EA', nullable=True)  # Unit (EA, KG, etc.)
    category = db.Column(db.String(50), nullable=True)  # Category
    
    # Quantités
    quantite_demandee = db.Column(db.Integer, nullable=False)  # Quantity
    quantite_produite = db.Column(db.Integer, default=0)  # Reported as finished
    report_remainder_as_finished = db.Column(db.Boolean, default=False)
    
    # Dates et heures
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)  # Created date and time
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Modified date and time
    date_lancement = db.Column(db.Date, nullable=True)  # Start date
    date_livraison_prevue = db.Column(db.Date, nullable=True)  # End date
    date_livraison_reelle = db.Column(db.Date, nullable=True)  # Delivery
    
    # Dates planifiées originales
    original_scheduled_start_date = db.Column(db.Date, nullable=True)
    original_scheduled_start_time = db.Column(db.Time, nullable=True)
    original_scheduled_end_date = db.Column(db.Date, nullable=True)
    original_scheduled_end_time = db.Column(db.Time, nullable=True)
    
    # Statuts
    statut = db.Column(db.String(20), default='en_attente', nullable=False)  # Status
    remain_status = db.Column(db.String(20), nullable=True)  # Remain status
    quality_order_status = db.Column(db.String(50), nullable=True)  # Quality order status
    
    # Planification
    master_plan = db.Column(db.String(100), nullable=True)  # Master plan
    master_production_line = db.Column(db.String(100), nullable=True)  # Master production line
    production_group = db.Column(db.String(50), nullable=True)  # Production group
    pool = db.Column(db.String(50), nullable=True)  # Pool
    locked_for_rescheduling = db.Column(db.Boolean, default=False)  # Locked for rescheduling
    
    # Priorité
    priorite_edd = db.Column(db.Integer, default=5)  # Priority (1=Lundi, 5=Vendredi)
    priority_reason = db.Column(db.String(200), nullable=True)  # Priority reason
    
    # Informations techniques pour ordonnancement
    temps_cycle = db.Column(db.Float, nullable=True)  # Temps cycle en heures
    capacite_par_operateur = db.Column(db.Float, nullable=True)  # Unités/shift
    efficience = db.Column(db.Float, default=1.0)  # 0.0 à 1.0
    
    # Références et traçabilité
    reference_type = db.Column(db.String(50), nullable=True)  # Reference type
    created_by = db.Column(db.String(100), nullable=True)  # Created by
    regrade = db.Column(db.String(50), nullable=True)  # Regrade
    
    # Commentaires
    commentaire = db.Column(db.Text, nullable=True)
    
    # Relations
    projet = db.relationship('Projet', backref='ordres_fabrication')
    produit = db.relationship('Produit', backref='ordres_fabrication')
    
    @property
    def taux_completion(self):
        """Calcule le taux de complétion en pourcentage"""
        if self.quantite_demandee == 0:
            return 0
        return round((self.quantite_produite / self.quantite_demandee) * 100, 1)
    
    @property
    def est_termine(self):
        return self.statut == 'termine'
    
    @property
    def est_en_cours(self):
        return self.statut == 'en_cours'
    
    @property
    def est_en_retard(self):
        """Vérifie si l'OF est en retard par rapport à la date de livraison prévue"""
        if self.date_livraison_prevue and not self.est_termine:
            return datetime.now().date() > self.date_livraison_prevue
        return False
    
    def __repr__(self):
        return f'<OrdreFabrication {self.numero_of}>'
