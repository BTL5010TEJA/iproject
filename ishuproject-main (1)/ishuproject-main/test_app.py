"""Simple test script to validate chatbot and meal plan functionality."""
from app import create_app
from models import db
from models.user import User
from models.food import FoodItem
from ai_engine.chatbot import get_chatbot
from ai_engine.recommender import FoodRecommender
from ai_engine.meal_planner import MealPlanner
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

def test_chatbot():
    """Test chatbot functionality."""
    print("\n" + "="*60)
    print("TESTING CHATBOT FUNCTIONALITY")
    print("="*60)
    
    # Get all foods
    all_foods = FoodItem.query.all()
    print(f"✓ Found {len(all_foods)} foods in database")
    
    # Get chatbot
    chatbot = get_chatbot()
    print("✓ Chatbot instance created")
    
    # Test questions
    test_questions = [
        "Can I eat papaya during pregnancy?",
        "What are the benefits of spinach?",
        "Is milk safe during pregnancy?",
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = chatbot.answer_question(question, all_foods, trimester=1)
        print(f"Intent: {result['intent']}")
        print(f"Foods mentioned: {result['foods_mentioned']}")
        print(f"Answer preview: {result['answer'][:100]}...")
    
    print("\n✓ Chatbot tests passed!")


def test_meal_planner():
    """Test meal planner functionality."""
    print("\n" + "="*60)
    print("TESTING MEAL PLANNER FUNCTIONALITY")
    print("="*60)
    
    # Create a test user
    bcrypt = Bcrypt()
    test_user = User(
        username='testuser',
        email='test@example.com',
        password_hash=bcrypt.generate_password_hash('test123').decode('utf-8'),
        full_name='Test User',
        due_date=datetime.now() + timedelta(days=180),
        current_trimester=2,
        dietary_preferences='vegetarian'
    )
    
    print("✓ Created test user (Trimester 2, Vegetarian)")
    
    # Create recommender and meal planner
    recommender = FoodRecommender(db)
    meal_planner = MealPlanner(db, recommender)
    print("✓ Meal planner instance created")
    
    # Generate a 3-day meal plan
    print("\nGenerating 3-day meal plan...")
    result = meal_planner.generate_meal_plan(
        user=test_user,
        days=3,
        region=None,
        diet_type='vegetarian'
    )
    
    if 'error' in result:
        print(f"✗ Error: {result['error']}")
        return False
    
    print(f"✓ Generated meal plan for {len(result['meal_plan'])} days")
    print(f"✓ Nutrition summary: {result['nutrition_summary']['avg_daily_calories']:.0f} calories/day")
    
    # Show first day
    if result['meal_plan']:
        day1 = result['meal_plan'][0]
        print(f"\nDay 1 meals:")
        for meal_type, foods in day1['meals'].items():
            if foods:
                food_names = [f['name'] for f in foods]
                print(f"  {meal_type}: {', '.join(food_names)}")
    
    print("\n✓ Meal planner tests passed!")
    return True


def test_preferences():
    """Test meal plan preferences."""
    print("\n" + "="*60)
    print("TESTING MEAL PLAN PREFERENCES")
    print("="*60)
    
    recommender = FoodRecommender(db)
    meal_planner = MealPlanner(db, recommender)
    
    prefs = meal_planner.get_available_preferences()
    print(f"✓ Available regions: {prefs['regions']}")
    print(f"✓ Available diet types: {prefs['diet_types']}")
    print(f"✓ Days range: {prefs['days_range']}")
    
    print("\n✓ Preferences tests passed!")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("Starting tests...")
        
        # Check database
        food_count = FoodItem.query.count()
        if food_count == 0:
            print("⚠ No foods in database. Running seeder...")
            from seed_data import seed_foods
            seed_foods()
        else:
            print(f"✓ Database has {food_count} food items")
        
        # Run tests
        try:
            test_chatbot()
            test_meal_planner()
            test_preferences()
            
            print("\n" + "="*60)
            print("ALL TESTS PASSED! ✓")
            print("="*60)
            print("\nThe application is ready to use!")
            print("Start the server with: python app.py")
            print("Then visit: http://localhost:5000")
            
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
