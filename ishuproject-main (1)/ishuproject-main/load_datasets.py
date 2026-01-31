"""Data loader for pregnancy diet datasets from CSV files."""
import pandas as pd
import os
from app import create_app
from models import db
from models.food import FoodItem
from models.recommendation import Recommendation
import json

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def load_regional_foods():
    """Load foods from regional datasets (data_1)."""
    print("\n📍 Loading Regional Foods (North/South Indian)...")
    
    files = [
        ('data/data_1/northveg_cleaned.csv', 'North Indian', 'vegetarian'),
        ('data/data_1/northnonveg_cleaned.csv', 'North Indian', 'non-vegetarian'),
        ('data/data_1/southveg_cleaned.csv', 'South Indian', 'vegetarian'),
        ('data/data_1/southnonveg_cleaned.csv', 'South Indian', 'non-vegetarian'),
    ]
    
    food_count = 0
    for file_path, region, diet_type in files:
        full_path = os.path.join(BASE_DIR, file_path)
        
        if not os.path.exists(full_path):
            print(f"  ⚠ File not found: {file_path}")
            continue
        
        try:
            df = pd.read_csv(full_path)
            print(f"\n  Processing: {region} - {diet_type} ({len(df)} entries)")
            
            # Extract unique foods
            unique_foods = df[['Food']].drop_duplicates()
            
            for _, row in unique_foods.iterrows():
                food_name = row['Food'].strip()
                
                # Check if food already exists
                existing = FoodItem.query.filter_by(name_english=food_name).first()
                if existing:
                    continue
                
                # Determine category from food name
                category = determine_category(food_name)
                
                # Create food item
                food = FoodItem(
                    name_english=food_name,
                    name_hindi=food_name,  # Would need translation for proper Hindi
                    category=category,
                    regional_origin=region,
                    dietary_type=diet_type,
                    nutritional_info={
                        'energy': 0,
                        'protein': 0,
                        'fat': 0,
                        'carbohydrates': 0,
                        'fiber': 0,
                        'calcium': 0,
                        'iron': 0,
                        'folic_acid': 0
                    },
                    trimester_suitability={
                        'trimester_1': True,
                        'trimester_2': True,
                        'trimester_3': True,
                        'all_trimesters': True
                    },
                    benefits=f"Traditional {region} food",
                    precautions="Cook well before consumption",
                    preparation_tips=f"Popular in {region} cuisine"
                )
                
                db.session.add(food)
                food_count += 1
            
            db.session.commit()
            print(f"  ✓ Added {food_count} unique foods from {region}")
            
        except Exception as e:
            print(f"  ✗ Error reading {file_path}: {e}")
    
    return food_count


def load_trimester_diet():
    """Load trimester-wise diet plans (data_2)."""
    print("\n🤰 Loading Trimester-Wise Diet Plans...")
    
    file_path = os.path.join(BASE_DIR, 'data/data_2/Trimester_Wise_Diet_Plan.csv')
    
    if not os.path.exists(file_path):
        print(f"  ⚠ File not found: {file_path}")
        return 0
    
    try:
        df = pd.read_csv(file_path)
        print(f"  Processing trimester data ({len(df)} entries)...")
        
        food_count = 0
        for _, row in df.iterrows():
            food_name = row['Food item'].strip()
            trimester = row['Trimester'].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').strip()
            
            # Check if food already exists
            existing = FoodItem.query.filter_by(name_english=food_name).first()
            if existing:
                continue
            
            # Determine trimester suitability
            trimester_map = {
                '1': {'trimester_1': True, 'trimester_2': False, 'trimester_3': False},
                '2': {'trimester_1': False, 'trimester_2': True, 'trimester_3': False},
                '3': {'trimester_1': False, 'trimester_2': False, 'trimester_3': True},
            }
            
            trimester_suitability = trimester_map.get(trimester, {
                'trimester_1': True, 'trimester_2': True, 'trimester_3': True
            })
            trimester_suitability['all_trimesters'] = all(trimester_suitability.values())
            
            category = determine_category(food_name)
            
            food = FoodItem(
                name_english=food_name,
                name_hindi=food_name,
                category=category,
                regional_origin='North India',  # Default from data
                dietary_type='vegetarian',  # Default
                nutritional_info={
                    'benefits': str(row.get('Nutritional benefit', 'Rich in nutrients'))
                },
                trimester_suitability=trimester_suitability,
                benefits=str(row.get('Nutritional benefit', 'Part of pregnancy diet')),
                precautions="Follow recommended quantity",
                preparation_tips=f"Part of Trimester {trimester} diet plan"
            )
            
            db.session.add(food)
            food_count += 1
        
        db.session.commit()
        print(f"  ✓ Added {food_count} trimester-specific foods")
        return food_count
        
    except Exception as e:
        print(f"  ✗ Error reading trimester data: {e}")
        return 0


def load_seasonal_diet():
    """Load seasonal pregnancy diet (data_3)."""
    print("\n🌞 Loading Seasonal Pregnancy Diet...")
    
    files = [
        ('data/data_3/summer_pregnancy_diet.csv', 'Summer'),
        ('data/data_3/Winter_Pregnancy_Diet.csv', 'Winter'),
        ('data/data_3/monsoon_diet_pregnant_women.csv', 'Monsoon'),
    ]
    
    food_count = 0
    for file_path, season in files:
        full_path = os.path.join(BASE_DIR, file_path)
        
        if not os.path.exists(full_path):
            print(f"  ⚠ File not found: {file_path}")
            continue
        
        try:
            df = pd.read_csv(full_path)
            print(f"\n  Processing {season} diet ({len(df)} entries)...")
            
            for _, row in df.iterrows():
                if pd.isna(row.get('Food / Drink')):
                    continue
                
                food_name = str(row['Food / Drink']).strip()
                category = row.get('Category', 'other').lower()
                
                # Check if food already exists
                existing = FoodItem.query.filter_by(name_english=food_name).first()
                if existing:
                    continue
                
                # Determine safety from 'Effect on Pregnancy'
                effect = str(row.get('Effect on Pregnancy', '')).lower()
                is_safe = 'avoid' not in effect and 'not recommended' not in effect
                
                food = FoodItem(
                    name_english=food_name,
                    name_hindi=food_name,
                    category=category,
                    regional_origin='All India',
                    dietary_type='vegetarian' if 'non-veg' not in food_name.lower() else 'non-vegetarian',
                    nutritional_info={
                        'nutrients': str(row.get('Nutrient / Benefit', 'Seasonal food'))
                    },
                    trimester_suitability={
                        'trimester_1': is_safe,
                        'trimester_2': is_safe,
                        'trimester_3': is_safe,
                        'all_trimesters': is_safe
                    },
                    benefits=str(row.get('Nutrient / Benefit', f'{season} food')),
                    precautions=str(row.get('Precaution / Limitation', 'Consume safely')),
                    preparation_tips=str(row.get('Additional Notes', f'Good for {season}')),
                    seasonal_availability=season
                )
                
                db.session.add(food)
                food_count += 1
            
            db.session.commit()
            print(f"  ✓ Added {food_count} foods from {season}")
            
        except Exception as e:
            print(f"  ✗ Error reading {file_path}: {e}")
    
    return food_count


def determine_category(food_name):
    """Determine food category from name."""
    food_lower = food_name.lower()
    
    if any(word in food_lower for word in ['milk', 'yogurt', 'dahi', 'paneer', 'cheese', 'curd', 'lassi']):
        return 'dairy'
    elif any(word in food_lower for word in ['spinach', 'palak', 'methi', 'okra', 'bhindi', 'cabbage', 'cauliflower', 'cucumber', 'tomato', 'carrot', 'potato', 'zucchini']):
        return 'vegetables'
    elif any(word in food_lower for word in ['apple', 'banana', 'orange', 'mango', 'papaya', 'guava', 'watermelon', 'berry', 'cherry', 'lemon', 'avocado', 'sapodilla', 'chikoo']):
        return 'fruits'
    elif any(word in food_lower for word in ['rice', 'roti', 'chapati', 'paratha', 'bread', 'wheat', 'daliya']):
        return 'grains'
    elif any(word in food_lower for word in ['dal', 'lentil', 'pulse', 'chickpea', 'chana', 'beans']):
        return 'lentils'
    elif any(word in food_lower for word in ['almond', 'badam', 'nut', 'raisin', 'date', 'dry fruit']):
        return 'dry_fruits'
    elif any(word in food_lower for word in ['egg', 'chicken', 'meat', 'fish']):
        return 'proteins'
    elif any(word in food_lower for word in ['ghee', 'oil', 'butter']):
        return 'fats'
    elif any(word in food_lower for word in ['water', 'juice', 'coconut water', 'lemonade', 'nimbu pani', 'buttermilk']):
        return 'beverages'
    else:
        return 'other'


def print_summary():
    """Print database summary."""
    print("\n" + "="*70)
    print("DATABASE SUMMARY")
    print("="*70)
    
    total_foods = FoodItem.query.count()
    print(f"\n✓ Total Foods in Database: {total_foods}")
    
    # Count by category
    categories = db.session.query(FoodItem.category, db.func.count(FoodItem.id)).group_by(FoodItem.category).all()
    print("\n📊 Foods by Category:")
    for category, count in sorted(categories):
        print(f"   • {category.title()}: {count}")
    
    # Count by region
    regions = db.session.query(FoodItem.regional_origin, db.func.count(FoodItem.id)).group_by(FoodItem.regional_origin).all()
    print("\n🌍 Foods by Region:")
    for region, count in sorted(regions):
        print(f"   • {region}: {count}")
    
    print("\n" + "="*70)


def main():
    """Main function to load all datasets."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("LOADING PREGNANCY DIET DATASETS")
        print("="*70)
        
        # Clear existing foods from seed (keeping test user)
        print("\n🗑️  Clearing previous food items...")
        FoodItem.query.delete()
        db.session.commit()
        print("✓ Cleared previous foods")
        
        total = 0
        
        # Load all datasets
        total += load_regional_foods()
        total += load_trimester_diet()
        total += load_seasonal_diet()
        
        print_summary()
        
        print(f"\n✅ Successfully loaded {total} food items from datasets!")
        print("\nYour application now has:")
        print("  ✓ Regional foods (North & South Indian)")
        print("  ✓ Trimester-wise diet recommendations")
        print("  ✓ Seasonal pregnancy diet guidance")
        print("\n" + "="*70)


if __name__ == '__main__':
    main()
