"""FLAN-T5 based response generation for pregnancy food recommendations."""
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import warnings
warnings.filterwarnings('ignore')


class FlanT5PregnancyGenerator:
    """FLAN-T5 based response generator for pregnancy food questions."""
    
    def __init__(self, model_name='google/flan-t5-base'):
        """Initialize FLAN-T5 model."""
        print("\n" + "="*80)
        print("INITIALIZING FLAN-T5 FOR RESPONSE GENERATION")
        print("="*80)
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"\nUsing device: {self.device}")
        
        print("\nLoading FLAN-T5 tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        print("Loading FLAN-T5 model...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        
        print("✓ FLAN-T5 ready for generation!")
    
    def generate_safety_response(self, food_name, trimester, question):
        """Generate safety information response."""
        prompt = f"""You are a pregnancy nutrition expert. Answer the following question about food safety during pregnancy.

Food: {food_name}
Trimester: {trimester}
Question: {question}

Provide a clear, concise, and evidence-based answer about the safety of {food_name} during {trimester}. Include any precautions or recommendations."""
        
        return self._generate(prompt)
    
    def generate_benefits_response(self, food_name, trimester):
        """Generate benefits information response."""
        prompt = f"""You are a pregnancy nutrition expert. Explain the nutritional benefits of {food_name} for pregnant women in {trimester}.

Highlight:
1. Key nutrients provided
2. Benefits for mother and fetus
3. How much to consume
4. Best preparation methods

Be informative and practical."""
        
        return self._generate(prompt)
    
    def generate_nutrition_response(self, food_name):
        """Generate detailed nutritional information."""
        prompt = f"""You are a pregnancy nutrition expert. Provide detailed nutritional information about {food_name}.

Include:
1. Calorie content
2. Key nutrients (protein, calcium, iron, vitamins)
3. Benefits for pregnancy
4. Recommended serving size
5. Storage tips

Be specific and practical."""
        
        return self._generate(prompt)
    
    def generate_preparation_response(self, food_name):
        """Generate preparation instructions."""
        prompt = f"""You are a pregnancy nutrition expert. Provide practical preparation instructions for {food_name} that are safe and healthy for pregnant women.

Include:
1. Selection/washing tips
2. Cooking method
3. Time and temperature
4. Safety precautions
5. Creative ways to consume

Be detailed and clear."""
        
        return self._generate(prompt)
    
    def generate_trimester_recommendation(self, trimester, food_items=None):
        """Generate trimester-specific recommendations."""
        food_list = ", ".join(food_items) if food_items else "common pregnancy foods"
        
        prompt = f"""You are a pregnancy nutrition expert. Provide comprehensive nutrition recommendations for Trimester {trimester}.

Focus on: {food_list}

Include:
1. Specific nutrient needs for this trimester
2. Best foods to eat
3. Foods to avoid
4. Sample daily meal plan
5. Important tips for health

Be specific to this trimester's needs."""
        
        return self._generate(prompt)
    
    def generate_meal_plan(self, days=7, region='North Indian', trimester=2):
        """Generate a personalized meal plan."""
        prompt = f"""You are a pregnancy nutrition expert. Create a {days}-day healthy meal plan for a pregnant woman in Trimester {trimester}.

Requirements:
- Region: {region}
- Format: Include breakfast, lunch, snacks, dinner
- Must include: Proteins, calcium sources, iron-rich foods, vitamins
- Avoid: Unsafe foods for pregnancy
- Practical: Easy to prepare, locally available foods

Provide detailed meal plan with quantities and nutritional benefits."""
        
        return self._generate(prompt)
    
    def generate_precautions_response(self, food_name, trimester):
        """Generate precautions and warnings."""
        prompt = f"""You are a pregnancy nutrition expert. Provide important precautions and warnings about {food_name} during {trimester}.

Include:
1. Safety concerns
2. When it's safe/unsafe
3. Preparation to make it safe
4. Signs of problems
5. Recommended alternatives

Be clear and cautious."""
        
        return self._generate(prompt)
    
    def generate_personalized_recommendation(self, user_profile, preferences):
        """Generate personalized food recommendations."""
        profile_str = f"""
User Profile:
- Trimester: {user_profile.get('trimester', 'Unknown')}
- Health Conditions: {user_profile.get('conditions', 'None')}
- Dietary Preference: {user_profile.get('diet_type', 'Vegetarian')}
- Regional Origin: {user_profile.get('region', 'North Indian')}
- Recent Foods: {user_profile.get('recent_foods', 'None mentioned')}

Preferences: {preferences}
"""
        
        prompt = f"""You are a pregnancy nutrition expert. Based on the following profile, provide personalized food recommendations:

{profile_str}

Provide:
1. Top 5 recommended foods
2. Foods to prioritize for nutritional needs
3. Foods to avoid
4. Sample daily nutrition plan
5. Tips for healthy eating

Make recommendations practical and culturally appropriate."""
        
        return self._generate(prompt)
    
    def _generate(self, prompt, max_length=512, num_beams=4, temperature=0.7):
        """Generate response using FLAN-T5."""
        input_ids = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_length=max_length,
                num_beams=num_beams,
                temperature=temperature,
                do_sample=False,
                top_k=50,
                top_p=0.95,
                early_stopping=True
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def generate_context_aware_response(self, question, intent, food_items=None, user_data=None):
        """Generate context-aware response based on intent."""
        food_context = ", ".join(food_items) if food_items else "pregnancy foods"
        user_context = f"User is in Trimester {user_data.get('trimester', 2)}" if user_data else ""
        
        base_prompt = f"""You are an experienced pregnancy nutrition counselor and registered dietitian. 
Your goal is to provide safe, accurate, and helpful nutrition advice for pregnant women.

User Question: {question}
Intent: {intent}
Food Context: {food_context}
{user_context}

Guidelines:
1. Always prioritize safety of mother and baby
2. Provide evidence-based information
3. Include specific quantities and frequencies
4. Mention when to consult healthcare provider
5. Be encouraging and supportive

Now answer the user's question with detailed, practical advice:"""
        
        return self._generate(base_prompt, max_length=600)


def test_generation():
    """Test FLAN-T5 response generation."""
    print("\n" + "="*80)
    print("TESTING FLAN-T5 RESPONSE GENERATION")
    print("="*80)
    
    generator = FlanT5PregnancyGenerator()
    
    # Test different response types
    print("\n📝 TEST 1: Safety Response")
    print("-" * 80)
    response = generator.generate_safety_response("Spinach", "First Trimester", "Is it safe to eat raw spinach?")
    print(f"Response:\n{response}\n")
    
    print("\n📝 TEST 2: Benefits Response")
    print("-" * 80)
    response = generator.generate_benefits_response("Almonds", "Second Trimester")
    print(f"Response:\n{response}\n")
    
    print("\n📝 TEST 3: Preparation Response")
    print("-" * 80)
    response = generator.generate_preparation_response("Lentils")
    print(f"Response:\n{response}\n")
    
    print("\n📝 TEST 4: Trimester Recommendations")
    print("-" * 80)
    response = generator.generate_trimester_recommendation(2, ["Milk", "Spinach", "Eggs", "Dal"])
    print(f"Response:\n{response}\n")
    
    print("\n📝 TEST 5: Meal Plan Generation")
    print("-" * 80)
    response = generator.generate_meal_plan(days=3, region="South Indian", trimester=2)
    print(f"Response:\n{response}\n")
    
    print("\n✓ Generation tests complete!")


if __name__ == '__main__':
    test_generation()
