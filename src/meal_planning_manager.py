from typing import Dict, List, Optional

class MealPlanningManager:
    """Manages personalized meal planning based on trimester and dietary needs"""
    
    def __init__(self):
        self.trimester_meal_plans = self._create_trimester_plans()
    
    def _create_trimester_plans(self) -> Dict[int, Dict]:
        """Create meal plans for each trimester"""
        return {
            1: {
                'name': 'First Trimester (Weeks 1-13)',
                'focus': ['folic acid', 'calcium', 'iron'],
                'sample_meals': [
                    'Breakfast: Oatmeal with berries and nuts',
                    'Lunch: Spinach salad with grilled chicken',
                    'Dinner: Baked salmon with sweet potato'
                ],
                'key_nutrients': {
                    'folic_acid': '400-800 mcg',
                    'calcium': '1000 mg',
                    'iron': '27 mg'
                }
            },
            2: {
                'name': 'Second Trimester (Weeks 14-27)',
                'focus': ['protein', 'calcium', 'iron'],
                'key_nutrients': {
                    'protein': '70-75g',
                    'calcium': '1000 mg',
                    'iron': '27 mg'
                }
            },
            3: {
                'name': 'Third Trimester (Weeks 28-40)',
                'focus': ['protein', 'calcium', 'fiber'],
                'key_nutrients': {
                    'protein': '75-100g',
                    'calcium': '1000 mg',
                    'fiber': '25-30g'
                }
            }
        }
    
    def get_meal_plan(self, trimester: int) -> Optional[Dict]:
        return self.trimester_meal_plans.get(trimester)
    
    def get_personalized_plan(self, trimester: int, restrictions: List[str] = None) -> Optional[Dict]:
        plan = self.get_meal_plan(trimester)
        if plan and restrictions:
            modified_plan = plan.copy()
            modified_plan['restrictions'] = restrictions
            return modified_plan
        return plan
