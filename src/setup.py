"""
Enhanced AgriBot Setup Script
Run this to install all dependencies and initialize the system
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    requirements = [
        'flask',
        'flask-sqlalchemy', 
        'flask-migrate',
        'psycopg2-binary',  # PostgreSQL support
        'nltk',             # Natural Language Processing
        'spacy',            # Advanced NLP
        'requests',         # API calls
        'python-dotenv'     # Environment variables
    ]
    
    print("Installing required packages...")
    for req in requirements:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
    
    print("Downloading NLTK data...")
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords') 
    nltk.download('vader_lexicon')
    nltk.download('wordnet')
    
    print("✅ All requirements installed!")

def setup_directories():
    """Create necessary directories"""
    dirs = ['database', 'templates', 'logs', 'data']
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def initialize_database():
    """Initialize database"""
    print("🗃️ Initializing database...")
    
    try:
        from database.init_db import initialize_database
        initialize_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

def main():
    """Main setup function"""
    print("🌱 Setting up Enhanced AgriBot...")
    print("=" * 50)
    
    try:
        install_requirements()
        setup_directories() 
        initialize_database()
        
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python flaskapp.py")
        print("2. Visit: http://localhost:5000")
        print("3. Start chatting with your enhanced AgriBot!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error and try again.")

if __name__ == '__main__':
    main()