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
        total += self._load_remaining_datasets()
        
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
                df = self._read_csv(full_path)
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
                df = self._read_csv(full_path)
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
                df = self._read_csv(full_path)
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

    def _load_remaining_datasets(self):
        """Load remaining datasets from data/remainingdatasets."""
        print("\n📦 LOADING REMAINING DATASETS...")
        print("-" * 80)

        total_foods = 0
        total_foods += self._load_clean_diet_dataset()
        total_foods += self._load_foods_to_avoid_dataset()
        total_foods += self._load_dos_donts_dataset()

        print(f"\n✓ Remaining Datasets Loaded: {total_foods} items")
        return total_foods

    def _load_clean_diet_dataset(self):
        """Load cleaned diet dataset (eat/avoid list)."""
        file_path = os.path.join(self.base_dir, 'data/remainingdatasets/pregnancy_diet_clean_dataset.csv')
        if not os.path.exists(file_path):
            print(f"  ⚠ File not found: {file_path}")
            return 0

        print("\n  • Processing pregnancy_diet_clean_dataset.csv")
        foods_added = 0

        try:
            df = self._read_csv(file_path)
            for _, row in df.iterrows():
                food_name = str(row.get('Food Item', '')).strip()
                if not food_name or food_name in self.loaded_foods:
                    continue

                food_group = str(row.get('Food Group', '')).strip()
                action_type = str(row.get('Type', '')).strip().lower()
                nutrients = str(row.get('Nutrients', '')).strip()
                benefit = str(row.get('Health Benefit', '')).strip()
                trimester_value = str(row.get('Trimester', '')).strip()
                remarks = str(row.get('Remarks', '')).strip()

                trimester_suitability = self._parse_trimester_value(trimester_value)
                if action_type == 'avoid':
                    trimester_suitability = self._invert_trimester_suitability(trimester_suitability)

                category = food_group.lower() if food_group else self._determine_category(food_name)

                food = FoodItem(
                    name_english=food_name,
                    name_hindi=food_name,
                    category=category,
                    regional_origin='All India',
                    nutritional_info=json.dumps({
                        'source': 'remaining_clean_diet',
                        'nutrients': nutrients
                    }),
                    trimester_suitability=json.dumps(trimester_suitability),
                    benefits=benefit if action_type != 'avoid' else None,
                    precautions=remarks if remarks else benefit,
                    preparation_tips=None
                )

                db.session.add(food)
                self.loaded_foods.add(food_name)
                foods_added += 1

            db.session.commit()
            print(f"    ✓ Added {foods_added} foods")
            return foods_added
        except Exception as e:
            print(f"  ✗ Error processing clean diet dataset: {e}")
            db.session.rollback()
            return 0

    def _load_foods_to_avoid_dataset(self):
        """Load foods to avoid dataset."""
        file_path = os.path.join(self.base_dir, 'data/remainingdatasets/foods_to_avoid_during_pregnancy_dataset.csv')
        if not os.path.exists(file_path):
            print(f"  ⚠ File not found: {file_path}")
            return 0

        print("\n  • Processing foods_to_avoid_during_pregnancy_dataset.csv")
        foods_added = 0

        try:
            df = self._read_csv(file_path)
            for _, row in df.iterrows():
                food_name = str(row.get('Food_Item', '')).strip()
                if not food_name or food_name in self.loaded_foods:
                    continue

                category = str(row.get('Food_Category', '')).strip().lower() or self._determine_category(food_name)
                examples = str(row.get('Examples', '')).strip()
                health_risk = str(row.get('Health_Risk', '')).strip()
                recommendation = str(row.get('Medical_Recommendation', '')).strip()
                applicable_trimester = str(row.get('Applicable_Trimester', '')).strip()

                trimester_suitability = self._parse_trimester_value(applicable_trimester)
                trimester_suitability = self._invert_trimester_suitability(trimester_suitability)

                food = FoodItem(
                    name_english=food_name,
                    name_hindi=food_name,
                    category=category,
                    regional_origin='All India',
                    nutritional_info=json.dumps({
                        'source': 'remaining_foods_to_avoid',
                        'examples': examples
                    }),
                    trimester_suitability=json.dumps(trimester_suitability),
                    benefits=None,
                    precautions=health_risk or recommendation,
                    preparation_tips=recommendation
                )

                db.session.add(food)
                self.loaded_foods.add(food_name)
                foods_added += 1

            db.session.commit()
            print(f"    ✓ Added {foods_added} foods")
            return foods_added
        except Exception as e:
            print(f"  ✗ Error processing foods-to-avoid dataset: {e}")
            db.session.rollback()
            return 0

    def _load_dos_donts_dataset(self):
        """Load pregnancy do's and don'ts dataset."""
        file_path = os.path.join(self.base_dir, 'data/remainingdatasets/pregnancy_dos_donts_dataset.csv')
        if not os.path.exists(file_path):
            print(f"  ⚠ File not found: {file_path}")
            return 0

        print("\n  • Processing pregnancy_dos_donts_dataset.csv")
        foods_added = 0

        try:
            df = self._read_csv(file_path)
            for _, row in df.iterrows():
                item = str(row.get('Item', '')).strip()
                if not item or item in self.loaded_foods:
                    continue

                category = str(row.get('Category', '')).strip().lower() or self._determine_category(item)
                action_type = str(row.get('Type', '')).strip().lower()
                description = str(row.get('Description', '')).strip()
                quantity = str(row.get('Quantity_Limit', '')).strip()
                notes = str(row.get('Notes', '')).strip()
                trimester_value = str(row.get('Trimester', '')).strip()

                trimester_suitability = self._parse_trimester_value(trimester_value)
                if action_type == "don't":
                    trimester_suitability = self._invert_trimester_suitability(trimester_suitability)

                food = FoodItem(
                    name_english=item,
                    name_hindi=item,
                    category=category,
                    regional_origin='All India',
                    nutritional_info=json.dumps({
                        'source': 'remaining_dos_donts',
                        'quantity_limit': quantity
                    }),
                    trimester_suitability=json.dumps(trimester_suitability),
                    benefits=description if action_type != "don't" else None,
                    precautions=notes if notes else description,
                    preparation_tips=None
                )

                db.session.add(food)
                self.loaded_foods.add(item)
                foods_added += 1

            db.session.commit()
            print(f"    ✓ Added {foods_added} items")
            return foods_added
        except Exception as e:
            print(f"  ✗ Error processing dos/donts dataset: {e}")
            db.session.rollback()
            return 0
    
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

    def _parse_trimester_value(self, value):
        """Parse free-form trimester values into suitability mapping."""
        if value is None:
            return self._get_trimester_suitability('all')

        text = str(value).lower().strip()
        if not text or text in {'all', 'all trimesters'}:
            return {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            }

        has_1 = '1st' in text or 'trimester 1' in text or text == '1'
        has_2 = '2nd' in text or 'trimester 2' in text or text == '2'
        has_3 = '3rd' in text or 'trimester 3' in text or text == '3'

        if '1st-3rd' in text or '1-3' in text or '1st to 3rd' in text:
            has_1 = has_2 = has_3 = True
        elif '1st-2nd' in text or '1-2' in text:
            has_1 = has_2 = True
        elif '2nd-3rd' in text or '2-3' in text:
            has_2 = has_3 = True

        suitability = {
            'trimester_1': bool(has_1),
            'trimester_2': bool(has_2),
            'trimester_3': bool(has_3)
        }
        suitability['all_trimesters'] = all(suitability.values())
        return suitability

    def _invert_trimester_suitability(self, suitability):
        """Invert suitability (used for avoid/don't items)."""
        inverted = {
            'trimester_1': not suitability.get('trimester_1', True),
            'trimester_2': not suitability.get('trimester_2', True),
            'trimester_3': not suitability.get('trimester_3', True)
        }
        inverted['all_trimesters'] = all(inverted.values())
        return inverted

    def _read_csv(self, file_path):
        """Read CSV with encoding fallback."""
        try:
            return pd.read_csv(file_path)
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='latin-1')


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
