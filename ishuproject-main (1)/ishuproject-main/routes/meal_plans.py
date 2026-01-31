"""Meal plan routes for generating personalized meal plans."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.interaction import UserInteraction
from ai_engine.recommender import FoodRecommender
from ai_engine.meal_planner import MealPlanner

meal_plans_bp = Blueprint('meal_plans', __name__)


@meal_plans_bp.route('/')
@login_required
def meal_plans_page():
    """Render meal plans generator page."""
    return render_template('dashboard/meal_plans.html')


@meal_plans_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_meal_plan():
    """
    Generate a personalized meal plan.
    
    Expects JSON:
        {
            "days": 7,
            "region": "North Indian" (optional),
            "diet_type": "vegetarian" (optional)
        }
    
    Returns:
        {
            "success": true,
            "meal_plan": [...],
            "nutrition_summary": {...},
            "table_format": [...]
        }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Get parameters
        days = data.get('days', 7)
        region = data.get('region')
        diet_type = data.get('diet_type')
        
        # Validate days
        try:
            days = int(days)
            if days < 1 or days > 30:
                return jsonify({'error': 'Days must be between 1 and 30'}), 400
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid days value'}), 400
        
        # Create recommender and meal planner
        recommender = FoodRecommender(db)
        meal_planner = MealPlanner(db, recommender)
        
        # Generate meal plan
        result = meal_planner.generate_meal_plan(
            user=current_user,
            days=days,
            region=region,
            diet_type=diet_type
        )
        
        # Check for errors
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # Log interaction to database
        interaction = UserInteraction(
            user_id=current_user.id,
            interaction_type='meal_plan_generation'
        )
        interaction.set_details({
            'days': days,
            'region': region,
            'diet_type': diet_type,
            'trimester': current_user.current_trimester,
            'total_meals': len(result['meal_plan']) * 5  # 5 meals per day
        })
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'meal_plan': result['meal_plan'],
            'nutrition_summary': result['nutrition_summary'],
            'table_format': result['table_format']
        })
        
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'An error occurred generating the meal plan. Please try again.'
        }), 500


@meal_plans_bp.route('/api/preferences', methods=['GET'])
@login_required
def get_preferences():
    """
    Get available preferences for meal planning.
    
    Returns:
        {
            "success": true,
            "regions": [...],
            "diet_types": [...],
            "days_range": {"min": 1, "max": 30}
        }
    """
    try:
        recommender = FoodRecommender(db)
        meal_planner = MealPlanner(db, recommender)
        
        preferences = meal_planner.get_available_preferences()
        
        return jsonify({
            'success': True,
            'regions': preferences['regions'],
            'diet_types': preferences['diet_types'],
            'days_range': preferences['days_range']
        })
        
    except Exception as e:
        print(f"Error getting preferences: {e}")
        # Return 500 with defaults as fallback
        return jsonify({
            'success': False,
            'error': 'Could not load preferences, showing defaults',
            'regions': ['All India', 'North Indian', 'South Indian'],
            'diet_types': ['vegetarian', 'non-vegetarian', 'vegan'],
            'days_range': {'min': 1, 'max': 30}
        }), 500
