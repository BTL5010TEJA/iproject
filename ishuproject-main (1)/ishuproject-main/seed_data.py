"""Database seeder for sample Indian foods."""
from app import create_app
from models import db
from models.food import FoodItem


def seed_foods():
    """Populate database with sample Indian foods."""
    
    foods = [
        {
            'name_english': 'Spinach',
            'name_hindi': 'Palak',
            'category': 'vegetables',
            'nutritional_info': {
                'iron': 2.7,
                'folic_acid': 194,
                'calcium': 99,
                'protein': 2.9,
                'fiber': 2.2,
                'calories': 23,
                'vitamin_a': 9377,
                'vitamin_c': 28
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Rich in iron and folic acid, essential for preventing anemia and supporting fetal neural tube development. High in antioxidants and fiber.',
            'precautions': 'Wash thoroughly. Cook well to reduce oxalate content. Consume in moderation if prone to kidney stones.',
            'preparation_tips': 'Can be made into palak paneer, dal palak, or palak soup. Sauté with garlic for better iron absorption.'
        },
        {
            'name_english': 'Milk',
            'name_hindi': 'Doodh',
            'category': 'dairy',
            'nutritional_info': {
                'calcium': 120,
                'protein': 3.4,
                'vitamin_d': 50,
                'vitamin_b12': 0.5,
                'calories': 61,
                'fat': 3.25
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Excellent source of calcium for bone development. Provides protein and vitamin D. Helps with hydration.',
            'precautions': 'Always boil before consumption. Avoid if lactose intolerant. Choose full-fat or low-fat based on weight goals.',
            'preparation_tips': 'Can be consumed plain, with turmeric (haldi doodh), in smoothies, or with dry fruits.'
        },
        {
            'name_english': 'Rice',
            'name_hindi': 'Chawal',
            'category': 'grains',
            'nutritional_info': {
                'calories': 130,
                'carbohydrates': 28,
                'protein': 2.7,
                'fiber': 0.4,
                'iron': 0.2
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Good source of energy. Easy to digest. Provides essential carbohydrates for mother and baby.',
            'precautions': 'Choose brown rice for more fiber. Control portions if diabetic or gestational diabetes.',
            'preparation_tips': 'Can be eaten plain, as pulao, khichdi, or with dal. Soak before cooking for better digestion.'
        },
        {
            'name_english': 'Papaya',
            'name_hindi': 'Papita',
            'category': 'fruits',
            'nutritional_info': {
                'vitamin_c': 62,
                'vitamin_a': 950,
                'fiber': 1.7,
                'folic_acid': 37,
                'calories': 43
            },
            'trimester_suitability': {
                'trimester_1': False,
                'trimester_2': False,
                'trimester_3': True
            },
            'regional_origin': 'All India',
            'benefits': 'Rich in vitamins and fiber. Aids digestion in third trimester. Helps with constipation.',
            'precautions': 'AVOID unripe papaya in first and second trimester as it can cause contractions. Only ripe papaya in small amounts in third trimester.',
            'preparation_tips': 'Ensure fully ripe. Eat in moderation. Can be eaten fresh or in fruit salads.'
        },
        {
            'name_english': 'Almonds',
            'name_hindi': 'Badam',
            'category': 'dry_fruits',
            'nutritional_info': {
                'protein': 21,
                'fiber': 12.5,
                'vitamin_e': 25.6,
                'calcium': 269,
                'iron': 3.7,
                'calories': 579,
                'omega3': 0.4
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'North India',
            'benefits': 'Excellent source of vitamin E, protein, and healthy fats. Supports brain development. Provides sustained energy.',
            'precautions': 'Consume soaked almonds for better digestion. Limit to 8-10 almonds per day due to high calorie content.',
            'preparation_tips': 'Soak overnight and peel skin. Can be eaten raw, in milk, or ground into almond butter.'
        },
        {
            'name_english': 'Lentils',
            'name_hindi': 'Dal',
            'category': 'lentils',
            'nutritional_info': {
                'protein': 9,
                'iron': 3.3,
                'fiber': 7.9,
                'folic_acid': 181,
                'calories': 116,
                'zinc': 1.3
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Rich plant-based protein. High in iron and folic acid. Essential for vegetarian mothers. Supports healthy blood formation.',
            'precautions': 'May cause gas; cook with asafoetida (hing) to reduce. Soak before cooking for better digestion.',
            'preparation_tips': 'Can be made as dal tadka, dal fry, or sambar. Combine with rice for complete protein.'
        },
        {
            'name_english': 'Yogurt',
            'name_hindi': 'Dahi',
            'category': 'dairy',
            'nutritional_info': {
                'calcium': 121,
                'protein': 3.5,
                'vitamin_b12': 0.4,
                'probiotics': True,
                'calories': 59
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Contains probiotics for gut health. Rich in calcium and protein. Helps with digestion and immunity.',
            'precautions': 'Use fresh, homemade yogurt when possible. Avoid if very sour. Consume at room temperature, not too cold.',
            'preparation_tips': 'Can be eaten plain, as raita, lassi, or with meals. Add fruits for extra nutrition.'
        },
        {
            'name_english': 'Eggs',
            'name_hindi': 'Ande',
            'category': 'proteins',
            'nutritional_info': {
                'protein': 13,
                'vitamin_d': 82,
                'vitamin_b12': 1.1,
                'choline': 147,
                'iron': 1.8,
                'calories': 155
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Complete protein source. Rich in choline for brain development. Provides essential vitamins and minerals.',
            'precautions': 'Always cook fully - avoid runny yolks or raw eggs. Ensure eggs are fresh and properly stored.',
            'preparation_tips': 'Boiled, scrambled, or as omelet. Avoid half-boiled or sunny side up during pregnancy.'
        },
        {
            'name_english': 'Dates',
            'name_hindi': 'Khajoor',
            'category': 'dry_fruits',
            'nutritional_info': {
                'iron': 0.9,
                'fiber': 6.7,
                'potassium': 696,
                'magnesium': 54,
                'calories': 277,
                'natural_sugars': 66
            },
            'trimester_suitability': {
                'trimester_1': False,
                'trimester_2': True,
                'trimester_3': True
            },
            'regional_origin': 'Middle East / North India',
            'benefits': 'Natural energy booster. Rich in iron and fiber. Traditionally consumed in third trimester to support labor.',
            'precautions': 'Avoid in first trimester. Limit to 2-3 dates per day. Monitor if diabetic or gestational diabetes.',
            'preparation_tips': 'Eat fresh, soak in milk, or add to smoothies. Best consumed in evening snacks.'
        },
        {
            'name_english': 'Ghee',
            'name_hindi': 'Ghee',
            'category': 'dairy',
            'nutritional_info': {
                'calories': 112,
                'fat': 12.7,
                'vitamin_a': 118,
                'vitamin_e': 0.3,
                'omega3': 0.15
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Source of healthy fats. Aids nutrient absorption. Provides energy. Traditionally believed to support easy labor.',
            'precautions': 'Use in moderation (1-2 teaspoons per day). High in calories. Choose pure, homemade ghee.',
            'preparation_tips': 'Add to dal, rice, chapati, or vegetables. Can be used for cooking or as topping.'
        },
        {
            'name_english': 'Sweet Potato',
            'name_hindi': 'Shakarkandi',
            'category': 'vegetables',
            'nutritional_info': {
                'vitamin_a': 14187,
                'fiber': 3,
                'vitamin_c': 2.4,
                'potassium': 337,
                'calories': 86,
                'carbohydrates': 20
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'All India',
            'benefits': 'Excellent source of beta-carotene and vitamin A. Good for baby\'s eye development. Provides sustained energy.',
            'precautions': 'Monitor portion size if diabetic. Choose boiled or baked over fried.',
            'preparation_tips': 'Can be boiled, baked, or roasted. Make chaat or add to salads. Avoid deep frying.'
        },
        {
            'name_english': 'Chickpeas',
            'name_hindi': 'Chana',
            'category': 'lentils',
            'nutritional_info': {
                'protein': 19,
                'fiber': 17,
                'iron': 6.2,
                'folic_acid': 557,
                'calcium': 105,
                'calories': 364
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'North India',
            'benefits': 'High in protein and fiber. Rich in folic acid for neural development. Helps maintain blood sugar levels.',
            'precautions': 'May cause gas - cook with spices like cumin and hing. Soak overnight before cooking.',
            'preparation_tips': 'Make as chole, hummus, or chana salad. Sprout for increased nutrition.'
        },
        {
            'name_english': 'Pomegranate',
            'name_hindi': 'Anaar',
            'category': 'fruits',
            'nutritional_info': {
                'vitamin_c': 10.2,
                'folic_acid': 38,
                'fiber': 4,
                'iron': 0.3,
                'antioxidants': True,
                'calories': 83
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'North India',
            'benefits': 'Rich in antioxidants and vitamin C. Helps with iron absorption. Boosts immunity and blood health.',
            'precautions': 'Eat fresh fruit rather than packaged juice. Consume in moderation.',
            'preparation_tips': 'Eat fresh seeds, add to salads, or make fresh juice. Best consumed in morning or evening.'
        },
        {
            'name_english': 'Fenugreek',
            'name_hindi': 'Methi',
            'category': 'vegetables',
            'nutritional_info': {
                'iron': 3.7,
                'fiber': 2.7,
                'calcium': 75,
                'vitamin_c': 3,
                'folic_acid': 57,
                'calories': 49
            },
            'trimester_suitability': {
                'trimester_1': False,
                'trimester_2': False,
                'trimester_3': True
            },
            'regional_origin': 'North India',
            'benefits': 'Known to boost lactation post-delivery. Rich in iron. Helps control blood sugar.',
            'precautions': 'Avoid in first two trimesters as may cause contractions. Consume only in third trimester in moderation.',
            'preparation_tips': 'Use fresh leaves (methi bhaji) or seeds (methi dana). Cook with potatoes or in parathas.'
        },
        {
            'name_english': 'Paneer',
            'name_hindi': 'Paneer',
            'category': 'dairy',
            'nutritional_info': {
                'protein': 18,
                'calcium': 208,
                'fat': 20,
                'vitamin_b12': 0.3,
                'calories': 265
            },
            'trimester_suitability': {
                'trimester_1': True,
                'trimester_2': True,
                'trimester_3': True,
                'all_trimesters': True
            },
            'regional_origin': 'North India',
            'benefits': 'Excellent vegetarian protein source. Rich in calcium for bone development. Provides essential fats.',
            'precautions': 'Ensure fresh, homemade paneer. Avoid store-bought during pregnancy. Consume in moderation due to high fat.',
            'preparation_tips': 'Make palak paneer, paneer bhurji, or grilled paneer. Always cook well - avoid raw paneer.'
        }
    ]
    
    print("Seeding database with sample Indian foods...")
    
    for food_data in foods:
        # Check if food already exists
        existing = FoodItem.query.filter_by(
            name_english=food_data['name_english']
        ).first()
        
        if existing:
            print(f"  - {food_data['name_english']} already exists, skipping")
            continue
        
        food = FoodItem(
            name_english=food_data['name_english'],
            name_hindi=food_data['name_hindi'],
            category=food_data['category'],
            regional_origin=food_data['regional_origin'],
            benefits=food_data['benefits'],
            precautions=food_data['precautions'],
            preparation_tips=food_data['preparation_tips']
        )
        
        food.set_nutritional_info(food_data['nutritional_info'])
        food.set_trimester_suitability(food_data['trimester_suitability'])
        
        db.session.add(food)
        print(f"  + Added {food_data['name_english']} ({food_data['name_hindi']})")
    
    db.session.commit()
    print(f"\nSuccessfully seeded {len(foods)} food items!")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_foods()
