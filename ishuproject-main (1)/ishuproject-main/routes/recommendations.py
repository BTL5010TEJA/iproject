"""Recommendation routes."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.recommendation import Recommendation
from ai_engine.recommender import FoodRecommender

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/api/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get personalized recommendations for the current user."""
    meal_type = request.args.get('meal_type')
    max_items = request.args.get('max_items', 10, type=int)
    
    # Initialize recommender
    recommender = FoodRecommender(db)
    
    # Get recommendations
    if meal_type:
        recommendations = recommender.get_meal_specific_recommendations(current_user, meal_type)
    else:
        recommendations = recommender.get_recommendations(current_user, max_items)
    
    # Save recommendation to database
    food_ids = [rec['food'].id for rec in recommendations]
    if food_ids:
        saved_rec = recommender.save_recommendation(
            current_user,
            food_ids,
            f"Personalized recommendations for trimester {current_user.current_trimester}"
        )
        rec_id = saved_rec.id
    else:
        rec_id = None
    
    # Format response
    result = {
        'recommendation_id': rec_id,
        'trimester': current_user.current_trimester,
        'recommendations': [
            {
                'food': rec['food'].to_dict(),
                'score': rec['score'],
                'warnings': rec['warnings'],
                'nutrition_score': rec['nutrition_score'],
                'trimester_score': rec['trimester_score'],
                'preference_score': rec['preference_score']
            }
            for rec in recommendations
        ]
    }
    
    return jsonify(result)


@recommendations_bp.route('/api/recommendations/history', methods=['GET'])
@login_required
def get_recommendation_history():
    """Get user's recommendation history."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    recommendations = Recommendation.query.filter_by(
        user_id=current_user.id
    ).order_by(Recommendation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = {
        'recommendations': [rec.to_dict() for rec in recommendations.items],
        'total': recommendations.total,
        'pages': recommendations.pages,
        'current_page': page
    }
    
    return jsonify(result)


@recommendations_bp.route('/recommendations')
@login_required
def recommendations_page():
    """Recommendations page."""
    return render_template('dashboard/recommendations.html')
