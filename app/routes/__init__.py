from .health import bp as health_bp
from .generate import bp as generate_bp
from .stats import bp as stats_bp

def register_routes(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(stats_bp)
