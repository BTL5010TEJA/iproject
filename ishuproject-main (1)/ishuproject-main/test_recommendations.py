#!/usr/bin/env python
"""Test recommendations functionality."""

import sys
from app import create_app
from models import db
from models.user import User
from models.food import FoodItem
from models.recommendation import Recommendation
from ai_engine.recommender import FoodRecommender

def test_recommendations():
    """Test the recommendations system."""
    # Create app in test mode
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        # Check database
        food_count = FoodItem.query.count()
        print(f"✅ Total foods in database: {food_count}")
        
        if food_count == 0:
            print("❌ No foods found in database. Load data first using load_datasets_v2.py")
            return False
        
        # Get a user for testing (use the first one)
        test_user = User.query.first()
        if not test_user:
            print("❌ No users found in database. Create a user first.")
            return False
        
        print(f"✅ Using test user: {test_user.username} (Trimester {test_user.current_trimester})")
        
        # Test recommendation generation
        try:
            recommender = FoodRecommender(db)
            
            # Test general recommendations
            recommendations = recommender.get_recommendations(test_user, max_items=10)
            print(f"✅ Generated {len(recommendations)} recommendations")
            
            if recommendations:
                first_rec = recommendations[0]
                print(f"\n   Sample recommendation:")
                print(f"   - Food: {first_rec['food'].name_english}")
                print(f"   - Score: {first_rec['score']*100:.1f}%")
                print(f"   - Nutrition Score: {first_rec['nutrition_score']*100:.1f}%")
                print(f"   - Trimester Score: {first_rec['trimester_score']*100:.1f}%")
                print(f"   - Preference Score: {first_rec['preference_score']*100:.1f}%")
                print(f"   - Warnings: {first_rec['warnings']}")
            
            # Test meal-specific recommendations
            meal_recommendations = recommender.get_meal_specific_recommendations(test_user, 'breakfast')
            print(f"✅ Generated {len(meal_recommendations)} breakfast recommendations")
            
            # Test saving recommendations
            food_ids = [rec['food'].id for rec in recommendations[:5]]
            saved_rec = recommender.save_recommendation(test_user, food_ids, "Test recommendations")
            print(f"✅ Saved recommendation with ID: {saved_rec.id}")
            
            # Test retrieval from database
            db_rec = Recommendation.query.get(saved_rec.id)
            if db_rec:
                food_list = db_rec.get_food_items()
                print(f"✅ Retrieved recommendation from database: {len(food_list)} foods")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_recommendations()
    sys.exit(0 if success else 1)
