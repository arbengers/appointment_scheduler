def register_blueprints(app):
    from app.health_check import component_blueprint as health_check_bp
    from app.admin import component_blueprint as admin_bp
    from app.appointment import component_blueprint as appointment_bp
    from app.auth import component_blueprint as authenticate_bp

    app.register_blueprint(health_check_bp())
    app.register_blueprint(authenticate_bp())
    app.register_blueprint(admin_bp())
    app.register_blueprint(appointment_bp())
