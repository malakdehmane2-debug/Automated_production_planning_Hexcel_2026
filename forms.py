from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from models import Projet, ProduitFini, Article, ObjectifMensuel, db

class ProjetForm(FlaskForm):
    nom = StringField('Nom du projet', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Enregistrer')

class ProduitFiniForm(FlaskForm):
    reference = StringField('Référence', validators=[DataRequired(), Length(max=50)])
    designation = StringField('Désignation', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Enregistrer')

class ArticleForm(FlaskForm):
    reference = StringField('Référence', validators=[DataRequired(), Length(max=50)])
    designation = StringField('Désignation', validators=[DataRequired(), Length(max=200)])
    quantite_par_produit = FloatField('Quantité par produit', 
                                    validators=[NumberRange(min=0.01)], 
                                    default=1.0)
    est_semi_fini = BooleanField('Article semi-fini', default=False)
    unite_mesure = StringField('Unité de mesure', 
                             validators=[DataRequired()], 
                             default='pièce')
    produit_fini_id = SelectField('Produit fini', coerce=int)
    parent_id = SelectField('Article parent', 
                          coerce=int, 
                          validators=[Optional()],
                          choices=[])
    quantite_necessaire = FloatField('Quantité nécessaire', 
                                   validators=[NumberRange(min=0.01)], 
                                   default=1.0)
    image = FileField('Image de l\'article', 
                     validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images uniquement!')])
    submit = SubmitField('Enregistrer')

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        # Mettre à jour les choix pour produit_fini_id
        self.produit_fini_id.choices = [(0, 'Sélectionner un produit fini')] + [
            (p.id, f"{p.reference} - {p.designation}") 
            for p in ProduitFini.query.all()
        ]
        # Mettre à jour les choix pour parent_id
        self.parent_id.choices = [(0, 'Aucun (article principal)')] + [
            (a.id, f"{a.reference} - {a.designation}") 
            for a in Article.query.filter(Article.est_semi_fini == True).all()
        ]

class ObjectifMensuelForm(FlaskForm):
    mois = IntegerField('Mois', validators=[DataRequired(), NumberRange(min=1, max=12)])
    annee = IntegerField('Année', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    quantite = IntegerField('Quantité', validators=[DataRequired(), NumberRange(min=1)])
    produit_fini_id = SelectField('Produit fini', coerce=int)
    submit = SubmitField('Enregistrer')

    def __init__(self, *args, **kwargs):
        super(ObjectifMensuelForm, self).__init__(*args, **kwargs)
        self.produit_fini_id.choices = [(0, 'Sélectionner un produit fini')] + [
            (p.id, f"{p.reference} - {p.designation}") 
            for p in ProduitFini.query.all()
        ]
