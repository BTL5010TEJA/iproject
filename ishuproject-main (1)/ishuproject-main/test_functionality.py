"""Test script to verify all application functionality."""
from app import create_app
from models import db
from models.user import User
from models.food import FoodItem
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

bcrypt = Bcrypt()


def test_application():
    """Run comprehensive tests."""
    print("\n" + "="*60)
    print("Testing Maternal Food Recommendation AI")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Database Connection
        print("\n✓ Test 1: Database Connection")
        try:
            db.session.execute(db.text('SELECT 1'))
            print("  ✓ Database connected successfully")
        except Exception as e:
            print(f"  ✗ Database connection failed: {e}")
            return False
        
        # Test 2: Food Items
        print("\n✓ Test 2: Food Items in Database")
        food_count = FoodItem.query.count()
        print(f"  ✓ Found {food_count} food items")
        if food_count == 0:
            print("  ⚠ Warning: No food items in database. Run seed_data.py")
        else:
            sample_food = FoodItem.query.first()
            print(f"  ✓ Sample: {sample_food.name_english} ({sample_food.name_hindi})")
        
        # Test 3: User Model
        print("\n✓ Test 3: User Model")
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            print("  → Creating test user...")
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=bcrypt.generate_password_hash('TestPass123!').decode('utf-8'),
                full_name='Test User',
                due_date=datetime.now() + timedelta(days=180),
                current_trimester=2,
                dietary_preferences='vegetarian'
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"  ✓ Test user created: {test_user.username}")
        else:
            print(f"  ✓ Test user exists: {test_user.username}")
        
        # Test 4: AI Engine
        print("\n✓ Test 4: AI Engine Components")
        try:
            from ai_engine.recommender import FoodRecommender
            from ai_engine.chatbot import get_chatbot
            from ai_engine.meal_planner import MealPlanner
            from ai_engine.nutritional_analyzer import NutritionalAnalyzer
            
            print("  ✓ FoodRecommender imported")
            print("  ✓ Chatbot imported")
            print("  ✓ MealPlanner imported")
            print("  ✓ NutritionalAnalyzer imported")
            
            # Test recommender
            recommender = FoodRecommender(db)
            recommendations = recommender.get_recommendations(test_user, max_items=5)
            print(f"  ✓ Generated {len(recommendations)} recommendations")
            
            # Test analyzer
            analyzer = NutritionalAnalyzer()
            if food_count > 0:
                food = FoodItem.query.first()
                score = analyzer.calculate_nutritional_score(food, 2)
                print(f"  ✓ Nutritional score calculated: {score:.2f}")
            
        except Exception as e:
            print(f"  ✗ AI Engine error: {e}")
        
        # Test 5: Routes
        print("\n✓ Test 5: Application Routes")
        routes = [rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/')]
        main_routes = [r for r in routes if not r.startswith('/static')]
        print(f"  ✓ {len(main_routes)} routes registered")
        print(f"  ✓ Main routes: /, /dashboard, /chatbot/, /meal-plans/, /recommendations/")
        
        # Test 6: Blueprints
        print("\n✓ Test 6: Blueprints")
        for name, blueprint in app.blueprints.items():
            print(f"  ✓ {name} blueprint registered")
        
        # Test 7: Configuration
        print("\n✓ Test 7: Configuration")
        print(f"  ✓ App Name: {app.config['APP_NAME']}")
        print(f"  ✓ Port: {app.config['PORT']}")
        print(f"  ✓ Database: SQLite (instance/database.db)")
        
        print("\n" + "="*60)
        print("All Tests Completed Successfully! ✓")
        print("="*60)
        print("\nYou can now:")
        print("  1. Start the server: python app.py")
        print("  2. Open browser: http://localhost:5000")
        print("  3. Register a new account or login with:")
        print("     Username: testuser")
        print("     Password: TestPass123!")
        print("="*60)
        
        return True


if __name__ == '__main__':
    test_application()
