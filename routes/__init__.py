from .auth_routes import auth_bp
from .user_routes import user_bp
from .upload_routes import upload_bp
from .summary_routes import summary_bp
from .role_routes import role_bp
from .dashboard_routes import dashboard_bp
from .student_routes import students_bp
from .teacher_routes import teacher_bp
from .notification_routes import notifications_bp
from .report_routes import reports_bp
from .contact_routes import contact_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(upload_bp, url_prefix='/uploads')
    app.register_blueprint(summary_bp, url_prefix='/summary')
    app.register_blueprint(role_bp, url_prefix='/roles')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(contact_bp, url_prefix='/contacts')