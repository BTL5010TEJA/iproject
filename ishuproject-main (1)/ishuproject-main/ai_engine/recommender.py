"""Main recommendation engine."""
import random
from datetime import datetime, timedelta
from models.food import FoodItem
from models.recommendation import Recommendation
from models.interaction import UserInteraction
from ai_engine.nutritional_analyzer import NutritionalAnalyzer


class FoodRecommender:
    """Main recommendation engine for suggesting foods to users."""
    
    def __init__(self, db):
        """Initialize the recommender."""
        self.db = db
        self.analyzer = NutritionalAnalyzer()
    
    def get_recommendations(self, user, max_items=10):
        """
        Get personalized food recommendations for a user.
        
        Args:
            user: User object
            max_items: Maximum number of recommendations
            
        Returns:
            list: List of recommended food items with scores
        """
        # Get all available foods
        all_foods = FoodItem.query.all()
        
        if not all_foods:
            return []
        
        # Score each food
        scored_foods = []
        user_health = user.get_health_conditions()
        
        for food in all_foods:
            # Calculate base nutritional score
            nutrition_score = self.analyzer.calculate_nutritional_score(
                food, user.current_trimester
            )
            
            # Check safety
            is_safe, warnings = self.analyzer.check_safety(food, user_health)
            if not is_safe:
                continue  # Skip unsafe foods
            
            # Check dietary preferences
            if not self._matches_dietary_preference(food, user.dietary_preferences):
                continue
            
            # Check trimester suitability
            trimester_score = self._get_trimester_score(food, user.current_trimester)
            
            # Get user preference score (based on past interactions)
            preference_score = self._get_user_preference_score(food, user)
            
            # Combine scores
            final_score = (
                nutrition_score * 0.4 +
                trimester_score * 0.3 +
                preference_score * 0.3
            )
            
            scored_foods.append({
                'food': food,
                'score': final_score,
                'warnings': warnings,
                'nutrition_score': nutrition_score,
                'trimester_score': trimester_score,
                'preference_score': preference_score
            })
        
        # Sort by score
        scored_foods.sort(key=lambda x: x['score'], reverse=True)
        
        # Add some randomization to avoid always showing the same items
        top_foods = scored_foods[:max_items * 2]
        
        # Ensure variety by category
        selected_foods = self._ensure_variety(top_foods, max_items)
        
        return selected_foods[:max_items]
    
    def _matches_dietary_preference(self, food, preference):
        """Check if food matches dietary preference."""
        if preference == 'vegan':
            non_vegan_categories = ['dairy', 'proteins']
            if food.category in non_vegan_categories:
                # Check if it's actually non-vegan
                if 'paneer' in food.name_english.lower() or 'dahi' in food.name_english.lower():
                    return False
        
        if preference == 'vegetarian':
            # All foods are acceptable for vegetarian
            # Would need to mark specific foods as non-veg in real implementation
            pass
        
        return True
    
    def _get_trimester_score(self, food, trimester):
        """Get score based on trimester suitability."""
        suitability = food.get_trimester_suitability()
        
        if not suitability:
            return 0.5  # Default score
        
        trimester_key = f'trimester_{trimester}'
        if trimester_key in suitability:
            # Higher score if specifically beneficial for this trimester
            return 0.9
        
        # Check if beneficial for all trimesters
        if suitability.get('all_trimesters', False):
            return 0.7
        
        return 0.5
    
    def _get_user_preference_score(self, food, user):
        """Calculate preference score based on user's past interactions."""
        # Get recent interactions with this food
        recent_interactions = UserInteraction.query.filter_by(
            user_id=user.id,
            food_item_id=food.id
        ).order_by(UserInteraction.timestamp.desc()).limit(10).all()
        
        if not recent_interactions:
            return 0.5  # Neutral score for new foods
        
        # Calculate score based on interaction types
        score = 0.5
        for interaction in recent_interactions:
            if interaction.interaction_type == 'like':
                score += 0.1
            elif interaction.interaction_type == 'dislike':
                score -= 0.2
            elif interaction.interaction_type == 'bookmark':
                score += 0.05
            elif interaction.interaction_type == 'view':
                score += 0.01
        
        return max(0.0, min(1.0, score))
    
    def _ensure_variety(self, scored_foods, max_items):
        """Ensure variety in categories among recommendations."""
        selected = []
        category_counts = {}
        max_per_category = max(2, max_items // 4)
        
        for item in scored_foods:
            category = item['food'].category
            count = category_counts.get(category, 0)
            
            if count < max_per_category:
                selected.append(item)
                category_counts[category] = count + 1
            
            if len(selected) >= max_items:
                break
        
        # If we don't have enough, add more regardless of category
        if len(selected) < max_items:
            for item in scored_foods:
                if item not in selected:
                    selected.append(item)
                if len(selected) >= max_items:
                    break
        
        return selected
    
    def save_recommendation(self, user, food_items, reason="Personalized recommendation"):
        """
        Save a recommendation to the database.
        
        Args:
            user: User object
            food_items: List of food item IDs
            reason: Reason for recommendation
            
        Returns:
            Recommendation object
        """
        recommendation = Recommendation(
            user_id=user.id,
            trimester=user.current_trimester,
            reason=reason
        )
        recommendation.set_food_items(food_items)
        
        self.db.session.add(recommendation)
        self.db.session.commit()
        
        return recommendation
    
    def get_meal_specific_recommendations(self, user, meal_type):
        """Get recommendations for specific meal types."""
        meal_categories = {
            'breakfast': ['grains', 'dairy', 'fruits'],
            'lunch': ['grains', 'vegetables', 'proteins', 'lentils'],
            'dinner': ['grains', 'vegetables', 'lentils'],
            'snacks': ['fruits', 'dry_fruits', 'traditional']
        }
        
        categories = meal_categories.get(meal_type, [])
        
        # Get all foods in these categories
        if categories:
            foods = FoodItem.query.filter(FoodItem.category.in_(categories)).all()
        else:
            foods = FoodItem.query.all()
        
        # Score and filter
        all_recommendations = self.get_recommendations(user)
        
        # Filter to only foods in the meal categories
        meal_recommendations = [
            rec for rec in all_recommendations
            if rec['food'].category in categories or not categories
        ]
        
        return meal_recommendations[:5]
