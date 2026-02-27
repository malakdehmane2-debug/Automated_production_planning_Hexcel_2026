import os
from pathlib import Path

# Chemin absolu vers le dossier du projet
BASEDIR = Path(__file__).parent.absolute()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-cle-secrete-tres-longue'
    # Chemin absolu vers la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + str(BASEDIR / 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration pour les uploads d'images
    UPLOAD_FOLDER = str(BASEDIR / 'static' / 'uploads' / 'articles')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# zohairrrrr - PFE