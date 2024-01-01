import os
import time
import logging
import asyncio
from quart import Quart
from quart_cors import cors

# Import async engine, session factory, and DATABASE_URL from database module
from .database import test_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app():
    # Set timezone
    os.environ['TZ'] = os.getenv('TZ', 'UTC')
    time.tzset()

    app = Quart(__name__)

    # Configure CORS
    app = cors(app, allow_origin="http://localhost:3000")

    # Import models and routes
    from .models import LogEntry
    from .routes import main
    app.register_blueprint(main)
    logging.info("Application created.")

    return app