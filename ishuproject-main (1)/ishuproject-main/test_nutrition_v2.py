#!/usr/bin/env python3
"""Test nutrition summary with full details"""

from app import create_app
from models import db
from models.user import User
from ai_engine.meal_planner import MealPlanner
from ai_engine.recommender import FoodRecommender
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

app = create_app('development')
bcrypt = Bcrypt(app)

with app.app_context():
    # Delete existing test user if it exists
    existing_user = User.query.filter_by(email='test_nutrition@test.com').first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
    
    # Create test user
    test_user = User(
        username='test_nutrition',
        email='test_nutrition@test.com',
        full_name='Test Nutrition',
        password_hash=bcrypt.generate_password_hash('test123').decode('utf-8'),
        current_trimester=2,
        dietary_preferences='vegetarian',
        due_date=datetime.now() + timedelta(days=120)
    )
    db.session.add(test_user)
    db.session.commit()
    
    # Create recommender and meal planner
    recommender = FoodRecommender(db)
    planner = MealPlanner(db, recommender)
    
    # Generate meal plan
    meal_plan = planner.generate_meal_plan(
        user=test_user,
        days=3, 
        diet_type='vegetarian', 
        region='North Indian'
    )
    
    print("=" * 60)
    print("NUTRITION SUMMARY TEST")
    print("=" * 60)
    print(f"\nMeal Plan for {len(meal_plan['meal_plan'])} days")
    
    summary = meal_plan['nutrition_summary']
    print("\nNutrition Summary:")
    print(f"  • Total Days: {summary.get('total_days', len(meal_plan['meal_plan']))}")
    print(f"  • Avg Daily Calories: {summary.get('avg_daily_calories')}")
    print(f"  • Avg Daily Protein: {summary.get('avg_daily_protein')}")
    print(f"  • Avg Daily Iron: {summary.get('avg_daily_iron')}")
    print(f"  • Avg Daily Calcium: {summary.get('avg_daily_calcium')}")
    print(f"  • Avg Daily Fiber: {summary.get('avg_daily_fiber')}")
    print(f"  • Avg Daily Folic Acid: {summary.get('avg_daily_folic_acid')}")
    
    note = summary.get('note')
    if note:
        print(f"  • Note: {note}")
    
    print("\nDay-by-Day Nutrition:")
    for day_data in meal_plan['meal_plan']:
        day_num = day_data.get('day', 'N/A')
        daily_nutrition = day_data.get('daily_nutrition', {})
        print(f"\n  Day {day_num}:")
        print(f"    - Calories: {daily_nutrition.get('calories', 'N/A')}")
        print(f"    - Protein: {daily_nutrition.get('protein', 'N/A')}g")
        print(f"    - Iron: {daily_nutrition.get('iron', 'N/A')}mg")
        print(f"    - Calcium: {daily_nutrition.get('calcium', 'N/A')}mg")
        print(f"    - Fiber: {daily_nutrition.get('fiber', 'N/A')}g")
        print(f"    - Folic Acid: {daily_nutrition.get('folic_acid', 'N/A')}mcg")
    
    print("\n" + "=" * 60)
    print("✓ Nutrition summary test completed!")
    print("=" * 60)
    
    # Clean up
    db.session.delete(test_user)
    db.session.commit()
