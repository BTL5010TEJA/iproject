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
    try:
        meal_type = request.args.get('meal_type')
        max_items = request.args.get('max_items', 10, type=int)
        
        # Validate input
        if max_items < 1 or max_items > 50:
            max_items = 10
        
        # Initialize recommender
        recommender = FoodRecommender(db)
        
        # Get recommendations
        if meal_type:
            recommendations = recommender.get_meal_specific_recommendations(current_user, meal_type)
        else:
            recommendations = recommender.get_recommendations(current_user, max_items)
        
        if not recommendations:
            return jsonify({
                'error': 'No recommendations available',
                'recommendations': [],
                'trimester': current_user.current_trimester
            }), 200
        
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
        
        # Format response with complete food data
        result = {
            'recommendation_id': rec_id,
            'trimester': current_user.current_trimester,
            'dietary_preference': current_user.dietary_preferences,
            'recommendations': [
                {
                    'food': rec['food'].to_dict(),
                    'score': round(rec['score'] * 100, 1),
                    'warnings': rec['warnings'] if rec['warnings'] else [],
                    'nutrition_score': round(rec['nutrition_score'] * 100, 1),
                    'trimester_score': round(rec['trimester_score'] * 100, 1),
                    'preference_score': round(rec['preference_score'] * 100, 1)
                }
                for rec in recommendations
            ]
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendations_bp.route('/api/recommendations/by-category', methods=['GET'])
@login_required
def get_recommendations_by_category():
    """Get recommendations grouped by food category."""
    try:
        recommender = FoodRecommender(db)
        recommendations = recommender.get_recommendations(current_user, max_items=20)
        
        if not recommendations:
            return jsonify({'error': 'No recommendations available', 'categories': {}}), 200
        
        # Group by category
        by_category = {}
        for rec in recommendations:
            category = rec['food'].category or 'other'
            if category not in by_category:
                by_category[category] = []
            
            by_category[category].append({
                'food': rec['food'].to_dict(),
                'score': round(rec['score'] * 100, 1),
                'warnings': rec['warnings'] if rec['warnings'] else []
            })
        
        return jsonify({
            'trimester': current_user.current_trimester,
            'categories': by_category
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendations_bp.route('/api/recommendations/feedback', methods=['POST'])
@login_required
def submit_recommendation_feedback():
    """Submit feedback on a recommendation."""
    try:
        data = request.json
        food_id = data.get('food_id')
        feedback = data.get('feedback')  # 'helpful', 'not_helpful', 'tried'
        notes = data.get('notes', '')
        
        if not food_id or not feedback:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Save interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            food_id=food_id,
            interaction_type=f'recommendation_feedback_{feedback}',
            details={'notes': notes}
        )
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feedback saved'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendations_bp.route('/api/recommendations/history', methods=['GET'])
@login_required
def get_recommendations_history():
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


@recommendations_bp.route('/')
@login_required
def recommendations_page():
    """Recommendations page."""
    return render_template('dashboard/recommendations.html')
