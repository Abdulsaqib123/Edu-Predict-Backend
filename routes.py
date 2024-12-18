from flask import Flask
from routes.auth_routes import auth_bp
from routes.role_routes import role_bp
from routes.user_routes import user_bp
from routes.upload_routes import upload_bp
from routes.summary_routes import summary_bp

def register_routes(app: Flask):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(role_bp, url_prefix='/roles')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(upload_bp, url_prefix='/uploads')
    app.register_blueprint(summary_bp, url_prefix='/summary')
