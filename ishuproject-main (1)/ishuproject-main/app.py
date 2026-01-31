"""Main Flask application entry point."""
import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from config import config
from models import db
from models.user import User

# Import blueprints
from routes.auth import auth_bp, bcrypt as auth_bcrypt
from routes.foods import foods_bp
from routes.recommendations import recommendations_bp
from routes.interactions import interactions_bp


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    auth_bcrypt.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register existing blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(foods_bp, url_prefix='/foods')
    app.register_blueprint(recommendations_bp, url_prefix='/recommendations')
    app.register_blueprint(interactions_bp, url_prefix='/interactions')
    
    # Import and register new blueprints (lazy import to avoid circular dependencies)
    try:
        from routes.chatbot import chatbot_bp
        app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    except ImportError:
        pass  # Chatbot blueprint not yet created
    
    try:
        from routes.meal_plans import meal_plans_bp
        app.register_blueprint(meal_plans_bp, url_prefix='/meal-plans')
    except ImportError:
        pass  # Meal plans blueprint not yet created
    
    # Main routes
    @app.route('/')
    def index():
        """Landing page."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Main dashboard page."""
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return render_template('dashboard/index.html')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = app.config['PORT']
    print(f"Starting {app.config['APP_NAME']}...")
    print(f"Server running on http://localhost:{port}")
    # Only use debug mode in development
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='127.0.0.1', port=port, debug=debug_mode)
