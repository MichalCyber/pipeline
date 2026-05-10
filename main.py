from flask import Flask, g
from uuid import uuid4
from app.app_logger import setup_logging
from app.routes import register_routes
from dotenv import load_dotenv
from app.config import settings
from app.pipeline.storage import StorageManager
from app.engines.foocus import FooocusEngine

setup_logging()
load_dotenv()

storage = StorageManager()
app = Flask(__name__)
engine = FooocusEngine()


@app.before_request
def add_request_id():
    g.request_id = str(uuid4())[:8]

register_routes(app)

if __name__ == "__main__":
    app.run(
        host= settings.HOST,
        port= settings.PORT,
        debug= settings.DEBUG
    )

