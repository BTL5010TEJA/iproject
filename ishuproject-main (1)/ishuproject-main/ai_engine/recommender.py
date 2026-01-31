"""Main recommendation engine."""
import re
from datetime import datetime
from models.food import FoodItem
from models.recommendation import Recommendation
from models.interaction import UserInteraction
from ai_engine.nutritional_analyzer import NutritionalAnalyzer


class FoodRecommender:
    """Main recommendation engine for suggesting foods to users."""
    NON_FOOD_CATEGORIES = {
        'avoid', 'foods to avoid', 'street food', 'processed foods', 'fatty foods',
        'sugary foods', 'leftovers', 'medical', 'supplements', 'exercise',
        'lifestyle', 'tips', 'hydration', 'diet', 'foods in moderation', 'prepared foods'
    }

    NON_VEG_KEYWORDS = {
        'chicken', 'mutton', 'fish', 'prawn', 'shrimp', 'beef', 'pork', 'meat',
        'seafood', 'egg', 'eggs'
    }

    VEGAN_EXCLUDE_KEYWORDS = {
        'milk', 'dahi', 'curd', 'yogurt', 'paneer', 'cheese', 'ghee', 'butter',
        'cream', 'egg', 'eggs'
    }

    CATEGORY_NORMALIZATION = {
        'proteins': 'protein',
        'protein': 'protein',
        'meat': 'protein',
        'seafood': 'protein',
        'seafood & fish': 'protein',
        'eggs': 'protein',
        'dry_fruits': 'nuts',
        'nuts & sprouts': 'nuts',
        'seeds': 'nuts',
        'fruits & vegetables': 'fruits',
        'fruits to include': 'fruits',
        'carbohydrates': 'grains',
        'soups/broths': 'soups',
        'beverages': 'beverages',
        'drinks': 'beverages'
    }

    _recommendation_cache = {}
    _nutrition_score_cache = {}
    _name_cache = {}

    _RECOMMENDATION_TTL_SECONDS = 180
    _NUTRITION_TTL_SECONDS = 12 * 60 * 60
    
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
        cache_key = (
            user.id,
            user.current_trimester,
            (user.dietary_preferences or '').lower(),
            max_items
        )
        cached = self._get_cached_recommendations(cache_key)
        if cached is not None:
            return cached

        # Get all available foods with basic DB-side filtering
        base_query = FoodItem.query.filter(FoodItem.name_english.isnot(None))
        if self.NON_FOOD_CATEGORIES:
            base_query = base_query.filter(~FoodItem.category.in_(self.NON_FOOD_CATEGORIES))

        all_foods = base_query.all()
        
        if not all_foods:
            return []
        
        # Preload user preference scores to avoid per-food queries
        preference_scores = self._get_user_interaction_scores(user.id)

        # Score each food
        scored_foods = []
        user_health = user.get_health_conditions()
        
        seen_names = set()

        for food in all_foods:
            if not self._is_recommendable_food(food):
                continue

            normalized_name = self._get_cached_normalized_name(food)
            if normalized_name in seen_names:
                continue
            # Calculate base nutritional score
            nutrition_score = self._get_cached_nutrition_score(food, user.current_trimester)
            
            # Check safety
            if not user_health and not food.precautions:
                is_safe, warnings = True, []
            else:
                is_safe, warnings = self.analyzer.check_safety(food, user_health)
            if not is_safe:
                continue  # Skip unsafe foods
            
            # Check dietary preferences
            if not self._matches_dietary_preference(food, user.dietary_preferences):
                continue
            
            # Check trimester suitability
            trimester_score = self._get_trimester_score(food, user.current_trimester)
            
            # Get user preference score (based on past interactions)
            preference_score = self._get_user_preference_score(food, preference_scores)
            
            # Add bonus for seasonal availability
            season_bonus = self._get_season_bonus(food)

            # Add bonus for richer info
            info_bonus = 0.0
            if food.benefits:
                info_bonus += 0.03
            if food.preparation_tips:
                info_bonus += 0.02

            # Combine scores
            final_score = (
                nutrition_score * 0.4 +
                trimester_score * 0.3 +
                preference_score * 0.3
            )
            final_score = min(1.0, final_score + season_bonus + info_bonus)
            
            scored_foods.append({
                'food': food,
                'score': final_score,
                'warnings': warnings,
                'nutrition_score': nutrition_score,
                'trimester_score': trimester_score,
                'preference_score': preference_score
            })

            seen_names.add(normalized_name)
        
        # Sort by score
        scored_foods.sort(key=lambda x: x['score'], reverse=True)
        
        # Add some randomization to avoid always showing the same items
        top_foods = scored_foods[:max_items * 3]
        
        # Ensure variety by category
        selected_foods = self._ensure_variety(top_foods, max_items)
        
        result = selected_foods[:max_items]
        self._set_cached_recommendations(cache_key, result)
        return result
    
    def _matches_dietary_preference(self, food, preference):
        """Check if food matches dietary preference."""
        preference = (preference or '').lower()
        food_name = food.name_english.lower()
        category = self._normalize_category(food.category)

        if preference in {'vegetarian', 'veg'}:
            if category in {'protein'} and any(keyword in food_name for keyword in self.NON_VEG_KEYWORDS):
                return False

        if preference in {'vegan'}:
            if category in {'dairy', 'protein'}:
                return False
            if any(keyword in food_name for keyword in self.VEGAN_EXCLUDE_KEYWORDS):
                return False

        return True
    
    def _get_trimester_score(self, food, trimester):
        """Get score based on trimester suitability."""
        suitability = food.get_trimester_suitability()
        
        if not suitability:
            return 0.5  # Default score
        
        trimester_key = f'trimester_{trimester}'
        if trimester_key in suitability:
            value = suitability.get(trimester_key)
            if isinstance(value, bool):
                return 0.9 if value else 0.2
            if isinstance(value, str) and value.lower() in {'yes', 'true', 'recommended'}:
                return 0.9
            if isinstance(value, (int, float)):
                return max(0.2, min(1.0, float(value)))
            return 0.8
        
        # Check if beneficial for all trimesters
        if suitability.get('all_trimesters', False):
            return 0.7
        
        return 0.5

    def _get_season_bonus(self, food):
        """Add a small bonus if the food is in season."""
        season = (food.seasonal_availability or '').lower()
        if not season or season == 'all':
            return 0.02

        month = datetime.utcnow().month
        if month in {3, 4, 5, 6}:
            current = 'summer'
        elif month in {7, 8, 9}:
            current = 'monsoon'
        else:
            current = 'winter'

        return 0.04 if current in season else 0.0

    def _is_recommendable_food(self, food):
        """Filter out non-food items and unsafe categories."""
        category = self._normalize_category(food.category)
        name = (food.name_english or '').lower().strip()

        if not name or len(name) < 3:
            return False

        if category in self.NON_FOOD_CATEGORIES:
            return False

        if 'avoid' in category or 'foods to avoid' in category:
            return False

        if any(bad in name for bad in ['alcohol', 'beer', 'wine', 'smoked', 'raw']):
            return False

        return True

    def _normalize_category(self, category):
        """Normalize category labels into a standard set."""
        if not category:
            return ''
        category_key = category.lower().strip()
        return self.CATEGORY_NORMALIZATION.get(category_key, category_key)

    def _get_cached_normalized_name(self, food):
        """Cache normalized food names to reduce repeated regex work."""
        cached = self._name_cache.get(food.id)
        if cached:
            return cached
        normalized = self._normalize_food_name(food.name_english)
        self._name_cache[food.id] = normalized
        return normalized

    def _get_cached_nutrition_score(self, food, trimester):
        """Cache nutrition scores per food and trimester."""
        cache_key = (food.id, trimester)
        cached = self._nutrition_score_cache.get(cache_key)
        if cached:
            score, ts = cached
            if (datetime.utcnow() - ts).total_seconds() <= self._NUTRITION_TTL_SECONDS:
                return score

        score = self.analyzer.calculate_nutritional_score(food, trimester)
        self._nutrition_score_cache[cache_key] = (score, datetime.utcnow())
        return score

    def _get_cached_recommendations(self, cache_key):
        """Return cached recommendations when available."""
        cached = self._recommendation_cache.get(cache_key)
        if not cached:
            return None

        data, ts = cached
        if (datetime.utcnow() - ts).total_seconds() > self._RECOMMENDATION_TTL_SECONDS:
            self._recommendation_cache.pop(cache_key, None)
            return None

        return data

    def _set_cached_recommendations(self, cache_key, data):
        """Store recommendations in cache."""
        self._recommendation_cache[cache_key] = (data, datetime.utcnow())

    def _normalize_food_name(self, name):
        """Normalize food name for deduplication."""
        if not name:
            return ''
        name = name.lower()
        name = re.sub(r'\([^)]*\)', '', name)
        name = re.sub(r'[^a-z0-9\s]+', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def _get_user_preference_score(self, food, preference_scores):
        """Calculate preference score based on user's past interactions."""
        if not preference_scores:
            return 0.5

        score = preference_scores.get(food.id, 0.5)
        return max(0.0, min(1.0, score))

    def _get_user_interaction_scores(self, user_id):
        """Aggregate preference scores for all foods for a user."""
        interactions = UserInteraction.query.filter_by(user_id=user_id).order_by(
            UserInteraction.timestamp.desc()
        ).limit(500).all()

        if not interactions:
            return {}

        scores = {}
        for interaction in interactions:
            food_id = interaction.food_item_id
            if not food_id:
                continue

            score = scores.get(food_id, 0.5)

            if interaction.interaction_type == 'like':
                score += 0.1
            elif interaction.interaction_type == 'dislike':
                score -= 0.2
            elif interaction.interaction_type == 'bookmark':
                score += 0.05
            elif interaction.interaction_type == 'view':
                score += 0.01
            elif interaction.interaction_type == 'feedback':
                score += 0.02

            scores[food_id] = max(0.0, min(1.0, score))

        return scores
    
    def _ensure_variety(self, scored_foods, max_items):
        """Ensure variety in categories among recommendations."""
        selected = []
        category_counts = {}
        max_per_category = max(2, max_items // 4)
        
        for item in scored_foods:
            category = self._normalize_category(item['food'].category)
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
    
    def get_meal_specific_recommendations(self, user, meal_type, max_items=5):
        """Get recommendations for specific meal types."""
        meal_categories = {
            'breakfast': {'grains', 'dairy', 'fruits', 'nuts', 'beverages'},
            'lunch': {'grains', 'vegetables', 'protein', 'lentils'},
            'dinner': {'grains', 'vegetables', 'lentils', 'soups'},
            'snacks': {'fruits', 'nuts', 'dairy', 'beverages'}
        }
        
        categories = meal_categories.get(meal_type, set())

        # Score and filter
        all_recommendations = self.get_recommendations(user, max_items=max_items * 3)

        # Filter to only foods in the meal categories
        meal_recommendations = [
            rec for rec in all_recommendations
            if self._normalize_category(rec['food'].category) in categories or not categories
        ]

        return meal_recommendations[:max_items]
