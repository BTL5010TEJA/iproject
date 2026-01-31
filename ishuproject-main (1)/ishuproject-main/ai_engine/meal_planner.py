"""Meal Plan Generator for maternal nutrition."""
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class MealPlanner:
    """Generate personalized meal plans for pregnant women."""
    
    def __init__(self, db, recommender):
        """
        Initialize the meal planner.
        
        Args:
            db: Database instance
            recommender: FoodRecommender instance
        """
        self.db = db
        self.recommender = recommender
        self.meal_types = ['breakfast', 'mid_morning_snack', 'lunch', 'evening_snack', 'dinner']
        
        # Category mapping for meal types
        self.meal_categories = {
            'breakfast': ['grains', 'dairy', 'fruits', 'proteins'],
            'mid_morning_snack': ['fruits', 'dry_fruits', 'dairy'],
            'lunch': ['grains', 'vegetables', 'proteins', 'lentils', 'dairy'],
            'evening_snack': ['fruits', 'dry_fruits', 'dairy', 'vegetables'],
            'dinner': ['grains', 'vegetables', 'lentils', 'dairy']
        }
    
    def generate_meal_plan(
        self,
        user,
        days: int = 7,
        region: Optional[str] = None,
        diet_type: Optional[str] = None
    ) -> Dict:
        """
        Generate a meal plan for the specified number of days.
        
        Args:
            user: User object
            days: Number of days for the meal plan (1-30)
            region: Regional preference (North Indian, South Indian, etc.)
            diet_type: Diet type (vegetarian, non-vegetarian)
            
        Returns:
            Dictionary with meal plan and nutrition summary
        """
        from models.food import FoodItem
        
        # Validate days
        days = max(1, min(days, 30))
        
        # Get all available foods
        query = FoodItem.query
        
        # Filter by region if specified
        if region:
            query = query.filter_by(regional_origin=region)
        
        all_foods = query.all()
        
        # Filter by diet type if needed
        if diet_type:
            all_foods = self._filter_by_diet(all_foods, diet_type)
        
        # Filter by user's dietary preferences
        all_foods = self._filter_by_diet(all_foods, user.dietary_preferences)
        
        # Filter by safety for user's trimester
        safe_foods = self._filter_safe_foods(all_foods, user)
        
        if not safe_foods:
            return {
                'error': 'No suitable foods found for your preferences',
                'meal_plan': [],
                'nutrition_summary': {}
            }
        
        # Generate meal plan
        meal_plan = []
        used_foods = set()  # Track recently used foods
        reset_interval = 3  # Reset used foods every 3 days for variety
        
        for day in range(1, days + 1):
            # Reset used foods periodically for variety
            if day % reset_interval == 0:
                used_foods.clear()
            
            day_meals = self._generate_day_meals(
                safe_foods,
                user,
                used_foods
            )
            
            meal_plan.append({
                'day': day,
                'date': (datetime.now() + timedelta(days=day-1)).strftime('%Y-%m-%d'),
                'meals': day_meals,
                'daily_nutrition': self._calculate_daily_nutrition(day_meals)
            })
        
        # Calculate overall nutrition summary
        nutrition_summary = self._calculate_plan_summary(meal_plan)
        
        return {
            'meal_plan': meal_plan,
            'nutrition_summary': nutrition_summary,
            'table_format': self._format_as_table(meal_plan)
        }
    
    def _filter_by_diet(self, foods: List, diet_type: str) -> List:
        """Filter foods by diet type."""
        if diet_type == 'vegan':
            # Exclude dairy and eggs
            return [f for f in foods if f.category not in ['dairy', 'proteins']]
        elif diet_type == 'vegetarian':
            # Include all foods (assuming all are vegetarian in our dataset)
            # In real implementation, would filter out meat/fish
            return foods
        else:
            return foods
    
    def _filter_safe_foods(self, foods: List, user) -> List:
        """Filter foods that are safe for user's trimester and health."""
        safe_foods = []
        user_health = user.get_health_conditions()
        
        for food in foods:
            # Check trimester suitability
            trimester_suit = food.get_trimester_suitability()
            trimester_key = f'trimester_{user.current_trimester}'
            
            if trimester_suit.get(trimester_key, True) or trimester_suit.get('all_trimesters', False):
                # Check safety with health conditions
                is_safe, warnings = self.recommender.analyzer.check_safety(food, user_health)
                if is_safe:
                    safe_foods.append(food)
        
        return safe_foods
    
    def _generate_day_meals(self, available_foods: List, user, used_foods: set) -> Dict:
        """Generate meals for a single day."""
        day_meals = {}
        
        for meal_type in self.meal_types:
            # Get suitable foods for this meal type
            meal_foods = [
                f for f in available_foods
                if f.category in self.meal_categories[meal_type]
                and f.id not in used_foods
            ]
            
            # If no unused foods, allow reuse
            if not meal_foods:
                meal_foods = [
                    f for f in available_foods
                    if f.category in self.meal_categories[meal_type]
                ]
            
            # Select foods for this meal
            if meal_foods:
                # For main meals, select 2-3 items; for snacks, 1-2 items
                num_items = 2 if 'snack' in meal_type else random.randint(2, 3)
                
                # Score and select foods
                scored_foods = []
                for food in meal_foods:
                    score = self.recommender.analyzer.calculate_nutritional_score(
                        food, user.current_trimester
                    )
                    scored_foods.append((food, score))
                
                # Sort by score and add some randomization
                scored_foods.sort(key=lambda x: x[1], reverse=True)
                top_foods = scored_foods[:num_items * 2]
                
                # Randomly select from top foods for variety
                selected = random.sample(
                    top_foods,
                    min(num_items, len(top_foods))
                )
                
                selected_foods = [f[0] for f in selected]
                
                # Mark as used
                for food in selected_foods:
                    used_foods.add(food.id)
                
                day_meals[meal_type] = [
                    {
                        'id': food.id,
                        'name': food.name_english,
                        'name_hindi': food.name_hindi,
                        'category': food.category,
                        'preparation_tips': food.preparation_tips
                    }
                    for food in selected_foods
                ]
        
        return day_meals
    
    def _calculate_daily_nutrition(self, day_meals: Dict) -> Dict:
        """Calculate total nutrition for a day."""
        from models.food import FoodItem
        
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'iron': 0,
            'calcium': 0,
            'fiber': 0,
            'folic_acid': 0
        }
        
        for meal_type, foods in day_meals.items():
            for food_data in foods:
                food = FoodItem.query.get(food_data['id'])
                if food:
                    nutrition = food.get_nutritional_info()
                    for nutrient in total_nutrition.keys():
                        if nutrient in nutrition:
                            total_nutrition[nutrient] += nutrition[nutrient]
        
        return total_nutrition
    
    def _calculate_plan_summary(self, meal_plan: List) -> Dict:
        """Calculate overall nutrition summary for the meal plan."""
        total_days = len(meal_plan)
        
        summary = {
            'total_days': total_days,
            'avg_daily_calories': 0,
            'avg_daily_protein': 0,
            'avg_daily_iron': 0,
            'avg_daily_calcium': 0,
            'avg_daily_fiber': 0,
            'avg_daily_folic_acid': 0
        }
        
        totals = {
            'calories': 0,
            'protein': 0,
            'iron': 0,
            'calcium': 0,
            'fiber': 0,
            'folic_acid': 0
        }
        
        for day_data in meal_plan:
            daily_nutrition = day_data['daily_nutrition']
            for nutrient in totals.keys():
                totals[nutrient] += daily_nutrition.get(nutrient, 0)
        
        # Calculate averages
        for nutrient in totals.keys():
            summary[f'avg_daily_{nutrient}'] = round(totals[nutrient] / total_days, 2)
        
        return summary
    
    def _format_as_table(self, meal_plan: List) -> List[Dict]:
        """Format meal plan as a table for display."""
        table_data = []
        
        for day_data in meal_plan:
            row = {
                'day': day_data['day'],
                'date': day_data['date'],
                'breakfast': ', '.join([f['name'] for f in day_data['meals'].get('breakfast', [])]),
                'mid_morning_snack': ', '.join([f['name'] for f in day_data['meals'].get('mid_morning_snack', [])]),
                'lunch': ', '.join([f['name'] for f in day_data['meals'].get('lunch', [])]),
                'evening_snack': ', '.join([f['name'] for f in day_data['meals'].get('evening_snack', [])]),
                'dinner': ', '.join([f['name'] for f in day_data['meals'].get('dinner', [])]),
                'calories': day_data['daily_nutrition'].get('calories', 0)
            }
            table_data.append(row)
        
        return table_data
    
    def get_available_preferences(self) -> Dict:
        """Get available preferences for meal planning."""
        from models.food import FoodItem
        
        # Get unique regions
        regions = self.db.session.query(FoodItem.regional_origin).distinct().all()
        regions = [r[0] for r in regions if r[0]]
        
        return {
            'regions': regions,
            'diet_types': ['vegetarian', 'non-vegetarian', 'vegan'],
            'days_range': {'min': 1, 'max': 30}
        }
