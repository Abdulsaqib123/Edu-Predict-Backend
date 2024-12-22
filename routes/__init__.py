from .auth_routes import auth_bp
from .user_routes import user_bp
from .upload_routes import upload_bp
from .summary_routes import summary_bp
from .role_routes import role_bp
from .dashboard_routes import dashboard_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(upload_bp, url_prefix='/uploads')
    app.register_blueprint(summary_bp, url_prefix='/summary')
    app.register_blueprint(role_bp, url_prefix='/roles')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')