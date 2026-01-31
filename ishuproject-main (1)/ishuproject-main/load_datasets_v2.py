"""Enhanced data loader for pregnancy diet datasets with proper processing."""
import pandas as pd
import os
import json
from app import create_app
from models import db
from models.food import FoodItem
import warnings
warnings.filterwarnings('ignore')


class DatasetLoader:
    """Load and process pregnancy diet datasets."""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data')
        self.loaded_foods = set()
    
    def load_all_datasets(self):
        """Load all datasets in sequence."""
        print("\n" + "="*80)
        print("LOADING COMPREHENSIVE PREGNANCY DIET DATASETS")
        print("="*80)
        
        total = 0
        total += self._load_regional_foods()
        total += self._load_trimester_diet()
        total += self._load_seasonal_diet()
        total += self._load_seasonal_specific()
        
        return total
    
    def _load_regional_foods(self):
        """Load regional foods from data_1."""
        print("\n📍 LOADING REGIONAL FOODS (Data Set 1)...")
        print("-" * 80)
        
        files = [
            ('data/data_1/northveg_cleaned.csv', 'North Indian', 'vegetarian'),
            ('data/data_1/northnonveg_cleaned.csv', 'North Indian', 'non-vegetarian'),
            ('data/data_1/southveg_cleaned.csv', 'South Indian', 'vegetarian'),
            ('data/data_1/southnonveg_cleaned.csv', 'South Indian', 'non-vegetarian'),
        ]
        
        total_foods = 0
        
        for file_path, region, diet_type in files:
            full_path = os.path.join(self.base_dir, file_path)
            
            if not os.path.exists(full_path):
                print(f"  ⚠ File not found: {file_path}")
                continue
            
            try:
                df = pd.read_csv(full_path)
                print(f"\n  Processing {region} - {diet_type}:")
                print(f"    Total entries: {len(df)}")
                
                # Extract unique foods from 'Food' column
                unique_foods = df['Food'].str.strip().unique()
                foods_added = 0
                
                for food_name in unique_foods:
                    if pd.isna(food_name) or food_name in self.loaded_foods:
                        continue
                    
                    food_name = food_name.strip()
                    if not food_name or len(food_name) < 2:
                        continue
                    
                    # Extract trimester from data
                    food_data = df[df['Food'].str.strip() == food_name].iloc[0]
                    trimester_str = food_data.get('Trimester', 'Trimester 1')
                    trimester_num = trimester_str.replace('Trimester ', '').strip()
                    
                    # Create food item
                    food = FoodItem(
                        name_english=food_name,
                        name_hindi=food_name,
                        category=self._determine_category(food_name),
                        regional_origin=region,
                        nutritional_info=json.dumps({
                            'source': 'regional_dataset',
                            'meal_types': list(df[df['Food'].str.strip() == food_name]['Meal Type'].unique())
                        }),
                        trimester_suitability=json.dumps(self._get_trimester_suitability(trimester_num)),
                        benefits=f"Traditional {region} food, suitable for pregnancy nutrition",
                        precautions="Ensure fresh and properly cooked",
                        preparation_tips=f"Popular in {region} cuisine"
                    )
                    
                    db.session.add(food)
                    self.loaded_foods.add(food_name)
                    foods_added += 1
                
                db.session.commit()
                print(f"    ✓ Added {foods_added} unique foods")
                total_foods += foods_added
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db.session.rollback()
        
        print(f"\n✓ Regional Foods Loaded: {total_foods} items")
        return total_foods
    
    def _load_trimester_diet(self):
        """Load trimester-wise diet plans from data_2."""
        print("\n🤰 LOADING TRIMESTER-WISE DIET PLANS (Data Set 2)...")
        print("-" * 80)
        
        files = [
            'data/data_2/Trimester_Wise_Diet_Plan.csv',
            'data/data_2/pregnancy_diet_1st_2nd_3rd_trimester.xlsx.csv'
        ]
        
        total_foods = 0
        
        for file_path in files:
            full_path = os.path.join(self.base_dir, file_path)
            
            if not os.path.exists(full_path):
                print(f"  ⚠ File not found: {file_path}")
                continue
            
            try:
                df = pd.read_csv(full_path)
                print(f"\n  Processing {os.path.basename(file_path)}:")
                print(f"    Total entries: {len(df)}")
                
                foods_added = 0
                
                for _, row in df.iterrows():
                    food_name = str(row.get('Food item', row.get('Food Item', ''))).strip()
                    
                    if not food_name or food_name in self.loaded_foods or len(food_name) < 2:
                        continue
                    
                    trimester = str(row.get('Trimester', '')).strip()
                    trimester_num = trimester.replace('1st', '1').replace('2nd', '2').replace('3rd', '3')
                    
                    region = str(row.get('Region', 'North India')).strip()
                    benefits = str(row.get('Nutritional benefit', row.get('Nutritional Benefit', '')))
                    meal_type = str(row.get('Meal type', row.get('Meal Type', '')))
                    
                    food = FoodItem(
                        name_english=food_name,
                        name_hindi=food_name,
                        category=self._determine_category(food_name),
                        regional_origin=region,
                        nutritional_info=json.dumps({
                            'source': 'trimester_dataset',
                            'meal_type': meal_type,
                            'benefits': benefits
                        }),
                        trimester_suitability=json.dumps(self._get_trimester_suitability(trimester_num)),
                        benefits=benefits,
                        precautions="Follow recommended quantity",
                        preparation_tips=f"Part of Trimester {trimester_num} diet plan"
                    )
                    
                    db.session.add(food)
                    self.loaded_foods.add(food_name)
                    foods_added += 1
                
                db.session.commit()
                print(f"    ✓ Added {foods_added} foods")
                total_foods += foods_added
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db.session.rollback()
        
        print(f"\n✓ Trimester Diet Plans Loaded: {total_foods} items")
        return total_foods
    
    def _load_seasonal_diet(self):
        """Load seasonal pregnancy diet from data_3."""
        print("\n🌞 LOADING SEASONAL PREGNANCY DIET (Data Set 3)...")
        print("-" * 80)
        
        files = [
            ('data/data_3/summer_pregnancy_diet.csv', 'Summer'),
            ('data/data_3/Winter_Pregnancy_Diet.csv', 'Winter'),
            ('data/data_3/monsoon_diet_pregnant_women.csv', 'Monsoon'),
        ]
        
        total_foods = 0
        
        for file_path, season in files:
            full_path = os.path.join(self.base_dir, file_path)
            
            if not os.path.exists(full_path):
                print(f"  ⚠ File not found: {file_path}")
                continue
            
            try:
                df = pd.read_csv(full_path)
                print(f"\n  Processing {season} ({len(df)} entries):")
                
                foods_added = 0
                
                for _, row in df.iterrows():
                    # Handle different column names
                    food_name = str(row.get('Food / Drink', row.get('Specific Foods (Winter)', 
                                           row.get('Item', '')))).strip()
                    
                    if not food_name or food_name in self.loaded_foods or len(food_name) < 2:
                        continue
                    
                    # Parse multiple foods if comma-separated
                    for single_food in food_name.split(','):
                        single_food = single_food.strip()
                        if not single_food or single_food in self.loaded_foods:
                            continue
                        
                        category = str(row.get('Category', 'other')).lower()
                        benefits = str(row.get('Nutrient / Benefit', row.get('Benefits', row.get('Nutrients Provided', ''))))
                        
                        # Determine safety
                        effect = str(row.get('Effect on Pregnancy', '')).lower()
                        is_safe = 'avoid' not in effect and 'risk' not in effect or 'benefits' in effect
                        
                        food = FoodItem(
                            name_english=single_food,
                            name_hindi=single_food,
                            category=category if category != 'other' else self._determine_category(single_food),
                            regional_origin='All India',
                            nutritional_info=json.dumps({
                                'source': 'seasonal_dataset',
                                'season': season,
                                'benefits': benefits
                            }),
                            trimester_suitability=json.dumps({
                                'trimester_1': is_safe,
                                'trimester_2': is_safe,
                                'trimester_3': is_safe,
                                'all_trimesters': is_safe
                            }),
                            benefits=benefits,
                            precautions=str(row.get('Precaution / Limitation', row.get('Foods to Avoid / Limit', ''))),
                            preparation_tips=str(row.get('Additional Notes', row.get('Recommended Preparations', ''))),
                            seasonal_availability=season
                        )
                        
                        db.session.add(food)
                        self.loaded_foods.add(single_food)
                        foods_added += 1
                
                db.session.commit()
                print(f"    ✓ Added {foods_added} foods for {season}")
                total_foods += foods_added
                
            except Exception as e:
                print(f"  ✗ Error processing {season}: {e}")
                db.session.rollback()
        
        print(f"\n✓ Seasonal Diet Loaded: {total_foods} items")
        return total_foods
    
    def _load_seasonal_specific(self):
        """Extract and load seasonal-specific recommendations."""
        print("\n❄️ LOADING SEASONAL SPECIFIC RECOMMENDATIONS...")
        print("-" * 80)
        
        total_foods = 0
        
        # Winter superfoods
        winter_superfoods = [
            ('Amla', 'fruits', 'Vitamin C, immunity booster', 'Winter'),
            ('Jaggery', 'other', 'Iron, warming food', 'Winter'),
            ('Sesame Seeds', 'seeds', 'Calcium, warming', 'Winter'),
            ('Fenugreek Leaves', 'vegetables', 'Iron, lactation support', 'Winter'),
            ('Ginger', 'vegetables', 'Anti-inflammatory, digestion', 'Winter'),
            ('Turmeric Milk', 'beverages', 'Anti-inflammatory, antibacterial', 'Winter'),
        ]
        
        # Summer superfoods
        summer_superfoods = [
            ('Watermelon', 'fruits', 'Hydration, electrolytes', 'Summer'),
            ('Coconut Water', 'beverages', 'Electrolytes, hydration', 'Summer'),
            ('Cucumber', 'vegetables', 'Hydration, cooling', 'Summer'),
            ('Buttermilk', 'dairy', 'Probiotics, cooling', 'Summer'),
        ]
        
        all_superfoods = winter_superfoods + summer_superfoods
        
        for food_name, category, benefits, season in all_superfoods:
            if food_name in self.loaded_foods:
                continue
            
            food = FoodItem(
                name_english=food_name,
                name_hindi=food_name,
                category=category,
                regional_origin='All India',
                nutritional_info=json.dumps({
                    'source': 'seasonal_superfoods',
                    'season': season
                }),
                trimester_suitability=json.dumps({
                    'trimester_1': True,
                    'trimester_2': True,
                    'trimester_3': True,
                    'all_trimesters': True
                }),
                benefits=benefits,
                precautions='Consume in moderation',
                preparation_tips=f'Recommended for {season}',
                seasonal_availability=season
            )
            
            db.session.add(food)
            self.loaded_foods.add(food_name)
            total_foods += 1
        
        db.session.commit()
        print(f"  ✓ Added {total_foods} seasonal superfoods")
        return total_foods
    
    def _determine_category(self, food_name):
        """Determine food category from name."""
        food_lower = food_name.lower()
        
        categories = {
            'dairy': ['milk', 'yogurt', 'dahi', 'paneer', 'cheese', 'curd', 'lassi', 'ghee', 'butter'],
            'vegetables': ['spinach', 'palak', 'methi', 'okra', 'bhindi', 'cabbage', 'cauliflower', 
                          'cucumber', 'tomato', 'carrot', 'potato', 'zucchini', 'gourd', 'broccoli',
                          'leafy', 'green', 'pumpkin', 'beet', 'radish', 'bean', 'pea'],
            'fruits': ['apple', 'banana', 'orange', 'mango', 'papaya', 'guava', 'watermelon', 
                      'berry', 'cherry', 'lemon', 'avocado', 'sapodilla', 'chikoo', 'lime', 'grape',
                      'pomegranate', 'anaar', 'apricot', 'fig', 'date', 'kiwi', 'peach', 'plum'],
            'grains': ['rice', 'roti', 'chapati', 'paratha', 'bread', 'wheat', 'daliya', 'poha',
                      'millet', 'bajra', 'ragi', 'oats', 'flour', 'semolina', 'rava'],
            'lentils': ['dal', 'lentil', 'pulse', 'chickpea', 'chana', 'beans', 'moong', 'urad', 'arhar'],
            'dry_fruits': ['almond', 'badam', 'nut', 'raisin', 'date', 'walnut', 'akhrot', 'cashew'],
            'proteins': ['egg', 'chicken', 'meat', 'fish', 'tofu', 'soya'],
            'beverages': ['water', 'juice', 'coconut water', 'lemonade', 'nimbu pani', 'buttermilk',
                         'tea', 'coffee', 'milk', 'lassi', 'soup', 'broth'],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in food_lower:
                    return category
        
        return 'other'
    
    def _get_trimester_suitability(self, trimester_str):
        """Get trimester suitability dictionary."""
        trimester_map = {
            '1': {'trimester_1': True, 'trimester_2': False, 'trimester_3': False},
            '2': {'trimester_1': False, 'trimester_2': True, 'trimester_3': False},
            '3': {'trimester_1': False, 'trimester_2': False, 'trimester_3': True},
        }
        
        suitability = trimester_map.get(trimester_str, {
            'trimester_1': True, 'trimester_2': True, 'trimester_3': True
        })
        
        suitability['all_trimesters'] = all(suitability.values())
        return suitability


def main():
    """Main function to load all datasets."""
    app = create_app()
    
    with app.app_context():
        # Clear existing foods
        print("\n🗑️  Clearing previous food items...")
        FoodItem.query.delete()
        db.session.commit()
        print("✓ Cleared")
        
        # Load datasets
        base_dir = os.path.dirname(os.path.abspath(__file__))
        loader = DatasetLoader(base_dir)
        total = loader.load_all_datasets()
        
        # Print summary
        print("\n" + "="*80)
        print("DATABASE SUMMARY")
        print("="*80)
        
        total_foods = FoodItem.query.count()
        print(f"\n✅ Total Foods Loaded: {total_foods}")
        
        # Statistics
        categories = db.session.query(FoodItem.category, db.func.count(FoodItem.id)).group_by(FoodItem.category).all()
        print("\n📊 Foods by Category:")
        for category, count in sorted(categories, key=lambda x: x[1], reverse=True):
            print(f"   • {category.title()}: {count}")
        
        regions = db.session.query(FoodItem.regional_origin, db.func.count(FoodItem.id)).group_by(FoodItem.regional_origin).all()
        print("\n🌍 Foods by Region:")
        for region, count in sorted(regions):
            print(f"   • {region}: {count}")
        
        print("\n" + "="*80)
        print(f"✅ Successfully loaded {total_foods} food items from datasets!")
        print("="*80 + "\n")


if __name__ == '__main__':
    main()
