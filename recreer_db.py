"""
Script pour recréer la base de données avec le nouveau modèle OrdreFabrication
ATTENTION: Ce script supprime toutes les données existantes!
"""

from app import create_app
from models import db

print("🔄 Recréation de la base de données...")
print("⚠️  ATTENTION: Toutes les données existantes seront supprimées!")

app = create_app()

with app.app_context():
    print("📦 Suppression des anciennes tables...")
    db.drop_all()
    
    print("🏗️  Création des nouvelles tables...")
    db.create_all()
    
    print("✅ Base de données recréée avec succès!")
    print("\n📊 Tables créées:")
    print("   - zones")
    print("   - projets")
    print("   - produits")
    print("   - items")
    print("   - assemblages")
    print("   - objectifs_mensuels")
    print("   - ordres_fabrication (avec tous les nouveaux attributs)")
    print("\n🚀 Vous pouvez maintenant lancer l'application avec: python app.py")
