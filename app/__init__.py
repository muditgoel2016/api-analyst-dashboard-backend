import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()
# Initialize Migrate
migrate = Migrate()

def create_app():
    # Set timezone
    os.environ['TZ'] = os.getenv('TZ', 'UTC')  # Default to UTC if TZ environment variable is not set
    time.tzset()

    app = Flask(__name__)


    # Configure CORS
    cors = CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000"]
        }
    })

    # Access environment variables
    db_username = os.getenv('DB_USERNAME', 'default_user')
    db_password = os.getenv('DB_PASSWORD', 'default_password')
    db_endpoint = os.getenv('DB_ENDPOINT', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@{db_endpoint}:{db_port}/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app configuration
    db.init_app(app)
    migrate.init_app(app, db)

    try:
        with app.app_context():
            # Try to connect to the database
            db.engine.connect()
        logging.info("Successfully connected to the database.")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")

    from .models import LogEntry
    from .routes import main
    app.register_blueprint(main)

    return app
