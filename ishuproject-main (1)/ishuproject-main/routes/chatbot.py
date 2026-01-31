"""Chatbot routes for AI-powered food recommendations."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db
from models.food import FoodItem
from models.interaction import UserInteraction

# Lazy load chatbot to avoid startup delay
_chatbot = None


def get_chatbot():
    """Get chatbot instance (lazy loading)."""
    global _chatbot
    if _chatbot is None:
        from ai_engine.chatbot import get_chatbot as get_chatbot_instance
        _chatbot = get_chatbot_instance()
    return _chatbot


chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/')
@login_required
def chatbot_page():
    """Render chatbot interface page."""
    return render_template('dashboard/chatbot.html')


@chatbot_bp.route('/api/ask', methods=['POST'])
@login_required
def ask_question():
    """
    Answer user questions using AI chatbot.
    
    Expects JSON:
        {
            "question": "Can I eat papaya during pregnancy?"
        }
    
    Returns:
        {
            "answer": "...",
            "intent": "safety_check",
            "foods_mentioned": ["Papaya"],
            "confidence": "high"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get all foods from database
        all_foods = FoodItem.query.all()
        
        # Get chatbot instance
        chatbot = get_chatbot()
        
        # Get answer from chatbot
        result = chatbot.answer_question(
            question=question,
            all_foods=all_foods,
            trimester=current_user.current_trimester
        )
        
        # Log interaction to database
        interaction = UserInteraction(
            user_id=current_user.id,
            interaction_type='chatbot_query'
        )
        interaction.set_details({
            'question': question,
            'intent': result['intent'],
            'foods_mentioned': result['foods_mentioned'],
            'trimester': current_user.current_trimester
        })
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'intent': result['intent'],
            'foods_mentioned': result['foods_mentioned'],
            'confidence': result['confidence'],
            'trimester': current_user.current_trimester
        })
        
    except Exception as e:
        print(f"Error in chatbot ask: {e}")
        return jsonify({
            'error': 'An error occurred processing your question. Please try again.'
        }), 500


@chatbot_bp.route('/api/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """
    Get suggested questions based on user's trimester.
    
    Returns:
        {
            "suggestions": ["Question 1", "Question 2", ...]
        }
    """
    try:
        chatbot = get_chatbot()
        suggestions = chatbot.get_suggested_questions(current_user.current_trimester)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'trimester': current_user.current_trimester
        })
        
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return jsonify({
            'error': 'Could not load suggestions',
            'suggestions': []
        }), 500


@chatbot_bp.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """
    Get user's chat history.
    
    Query params:
        limit: Number of recent interactions (default: 20)
    
    Returns:
        {
            "history": [
                {
                    "id": 1,
                    "question": "...",
                    "timestamp": "2024-01-01T12:00:00",
                    "foods_mentioned": [...]
                },
                ...
            ]
        }
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)  # Max 100 items
        
        # Get user's chatbot interactions
        interactions = UserInteraction.query.filter_by(
            user_id=current_user.id,
            interaction_type='chatbot_query'
        ).order_by(
            UserInteraction.timestamp.desc()
        ).limit(limit).all()
        
        history = []
        for interaction in interactions:
            details = interaction.get_details()
            history.append({
                'id': interaction.id,
                'question': details.get('question', ''),
                'intent': details.get('intent', ''),
                'foods_mentioned': details.get('foods_mentioned', []),
                'timestamp': interaction.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        })
        
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({
            'error': 'Could not load chat history',
            'history': []
        }), 500
