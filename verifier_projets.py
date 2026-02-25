"""
Script pour vérifier les projets dans la base de données
"""
from app import create_app, db
from models import Projet, ProduitFini, Article

def verifier_projets():
    app = create_app()
    with app.app_context():
        print("\n" + "="*70)
        print("📊 VÉRIFICATION DES PROJETS DANS LA BASE DE DONNÉES")
        print("="*70 + "\n")
        
        # Compter les projets
        nb_projets = Projet.query.count()
        print(f"Nombre total de projets : {nb_projets}\n")
        
        if nb_projets == 0:
            print("❌ Aucun projet trouvé dans la base de données.")
            print("\n💡 Suggestions :")
            print("  1. Créez un nouveau projet via l'interface web")
            print("  2. Vérifiez que la base de données 'database.db' existe")
            print("  3. Vérifiez que l'application utilise la bonne base de données\n")
        else:
            print(f"✅ {nb_projets} projet(s) trouvé(s) :\n")
            
            # Lister tous les projets
            projets = Projet.query.all()
            for i, projet in enumerate(projets, 1):
                print(f"{i}. Projet : {projet.nom}")
                print(f"   ID : {projet.id}")
                print(f"   Description : {projet.description or 'Aucune'}")
                print(f"   Date de création : {projet.date_creation.strftime('%d/%m/%Y %H:%M')}")
                
                # Compter les produits finis
                nb_produits = projet.produits_finis.count()
                print(f"   Produits finis : {nb_produits}")
                
                if nb_produits > 0:
                    for produit in projet.produits_finis.all():
                        print(f"      - {produit.reference} : {produit.designation}")
                        nb_articles = produit.articles.count()
                        print(f"        Articles : {nb_articles}")
                
                print()
        
        # Statistiques globales
        print("="*70)
        print("📈 STATISTIQUES GLOBALES")
        print("="*70)
        print(f"Projets : {Projet.query.count()}")
        print(f"Produits finis : {ProduitFini.query.count()}")
        print(f"Articles : {Article.query.count()}")
        print("="*70 + "\n")

if __name__ == '__main__':
    verifier_projets()
