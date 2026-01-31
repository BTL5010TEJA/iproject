"""AI Chatbot Module using BERT and FLAN-T5."""
import re
from typing import Dict, List, Tuple, Optional


class MaternalFoodChatbot:
    """
    AI Chatbot for maternal food recommendations.
    Uses BERT for query understanding and FLAN-T5 for response generation.
    """
    
    def __init__(self):
        """Initialize the chatbot (lazy loading for models)."""
        self._bert_tokenizer = None
        self._bert_model = None
        self._flan_tokenizer = None
        self._flan_model = None
        self._models_loaded = False
    
    def _load_models(self):
        """Lazy load BERT and FLAN-T5 models."""
        if self._models_loaded:
            return
        
        try:
            from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModelForSeq2SeqLM
            import torch
            
            print("Loading BERT model...")
            self._bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self._bert_model = BertModel.from_pretrained('bert-base-uncased')
            
            print("Loading FLAN-T5 model...")
            self._flan_tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')
            self._flan_model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base')
            
            # Set to evaluation mode
            self._bert_model.eval()
            self._flan_model.eval()
            
            self._models_loaded = True
            print("AI models loaded successfully!")
            
        except Exception as e:
            print(f"Warning: Could not load AI models: {e}")
            print("Chatbot will work in fallback mode without AI models.")
    
    def classify_intent(self, question: str) -> str:
        """
        Classify user intent from the question.
        
        Args:
            question: User's question
            
        Returns:
            Intent category
        """
        question_lower = question.lower()
        
        # Intent patterns
        if any(word in question_lower for word in ['can i eat', 'is it safe', 'safe to eat', 'should i avoid']):
            return 'safety_check'
        elif any(word in question_lower for word in ['benefits', 'good for', 'why eat', 'advantages']):
            return 'benefits'
        elif any(word in question_lower for word in ['nutrition', 'nutrients', 'vitamins', 'minerals', 'protein', 'calcium', 'iron']):
            return 'nutritional_info'
        elif any(word in question_lower for word in ['how much', 'quantity', 'how many', 'serving']):
            return 'quantity'
        elif any(word in question_lower for word in ['how to', 'prepare', 'cook', 'recipe']):
            return 'preparation'
        elif any(word in question_lower for word in ['precaution', 'warning', 'avoid', 'risk']):
            return 'precautions'
        elif any(word in question_lower for word in ['trimester', 'first trimester', 'second trimester', 'third trimester']):
            return 'trimester_specific'
        else:
            return 'general'
    
    def extract_food_entities(self, question: str, all_foods: List) -> List:
        """
        Extract food items mentioned in the question.
        
        Args:
            question: User's question
            all_foods: List of FoodItem objects from database
            
        Returns:
            List of matching FoodItem objects
        """
        question_lower = question.lower()
        matched_foods = []
        
        for food in all_foods:
            # Check English name
            if food.name_english.lower() in question_lower:
                matched_foods.append(food)
                continue
            
            # Check Hindi name
            if food.name_hindi and food.name_hindi.lower() in question_lower:
                matched_foods.append(food)
                continue
            
            # Check partial matches (e.g., "palak" in "palak paneer")
            words = question_lower.split()
            for word in words:
                if len(word) > 3:  # Skip very short words
                    if word in food.name_english.lower() or (food.name_hindi and word in food.name_hindi.lower()):
                        matched_foods.append(food)
                        break
        
        return matched_foods
    
    def generate_response(self, question: str, intent: str, foods: List, trimester: int = 1) -> str:
        """
        Generate a response to the user's question.
        
        Args:
            question: User's question
            intent: Classified intent
            foods: List of relevant FoodItem objects
            trimester: User's current trimester
            
        Returns:
            Generated response
        """
        # If no foods found, give general response
        if not foods:
            return self._generate_general_response(question, intent, trimester)
        
        # For single food, give detailed response
        if len(foods) == 1:
            return self._generate_single_food_response(foods[0], intent, trimester)
        
        # For multiple foods, give comparative response
        return self._generate_multi_food_response(foods, intent, trimester)
    
    def _generate_general_response(self, question: str, intent: str, trimester: int) -> str:
        """Generate general response when no specific food is mentioned."""
        responses = {
            'safety_check': f"During your trimester {trimester}, it's important to focus on a balanced diet. Could you please specify which food item you'd like to know about?",
            'benefits': "A healthy pregnancy diet includes fruits, vegetables, whole grains, dairy, and proteins. Each food group offers unique benefits for you and your baby.",
            'nutritional_info': f"In trimester {trimester}, focus on foods rich in iron, calcium, folic acid, and protein. Would you like information about any specific food?",
            'general': "I'm here to help with your pregnancy nutrition questions! You can ask me about specific foods, their safety, benefits, or preparation methods."
        }
        return responses.get(intent, responses['general'])
    
    def _generate_single_food_response(self, food, intent: str, trimester: int) -> str:
        """Generate detailed response for a single food item."""
        trimester_suit = food.get_trimester_suitability()
        trimester_key = f'trimester_{trimester}'
        is_safe = trimester_suit.get(trimester_key, True)
        
        response = f"**{food.name_english}** ({food.name_hindi})\n\n"
        
        if intent == 'safety_check':
            if is_safe:
                response += f"✅ Yes, {food.name_english.lower()} is generally safe during trimester {trimester}.\n\n"
                if food.precautions:
                    response += f"**Precautions:** {food.precautions}\n\n"
            else:
                response += f"⚠️ It's recommended to avoid or limit {food.name_english.lower()} during trimester {trimester}.\n\n"
                if food.precautions:
                    response += f"**Reason:** {food.precautions}\n\n"
        
        elif intent == 'benefits':
            if food.benefits:
                response += f"**Benefits:**\n{food.benefits}\n\n"
        
        elif intent == 'nutritional_info':
            nutrition = food.get_nutritional_info()
            if nutrition:
                response += "**Nutritional Information (per 100g):**\n"
                for nutrient, value in nutrition.items():
                    if nutrient != 'probiotics' and nutrient != 'antioxidants':
                        response += f"- {nutrient.replace('_', ' ').title()}: {value}\n"
                response += "\n"
        
        elif intent == 'preparation':
            if food.preparation_tips:
                response += f"**Preparation Tips:**\n{food.preparation_tips}\n\n"
        
        elif intent == 'precautions':
            if food.precautions:
                response += f"**Precautions:**\n{food.precautions}\n\n"
        
        else:  # General info
            if food.benefits:
                response += f"**Benefits:** {food.benefits}\n\n"
            if is_safe:
                response += f"✅ Safe for trimester {trimester}\n"
            else:
                response += f"⚠️ Use caution in trimester {trimester}\n"
        
        return response.strip()
    
    def _generate_multi_food_response(self, foods: List, intent: str, trimester: int) -> str:
        """Generate response for multiple food items."""
        response = f"I found information about {len(foods)} foods:\n\n"
        
        for i, food in enumerate(foods[:3], 1):  # Limit to 3 foods
            trimester_suit = food.get_trimester_suitability()
            trimester_key = f'trimester_{trimester}'
            is_safe = trimester_suit.get(trimester_key, True)
            
            response += f"{i}. **{food.name_english}** ({food.name_hindi})"
            if is_safe:
                response += " - ✅ Safe for your trimester\n"
            else:
                response += " - ⚠️ Use caution\n"
            
            if intent == 'benefits' and food.benefits:
                response += f"   {food.benefits[:100]}...\n"
            elif intent == 'nutritional_info':
                nutrition = food.get_nutritional_info()
                if nutrition:
                    key_nutrients = list(nutrition.items())[:2]
                    for nutrient, value in key_nutrients:
                        response += f"   - {nutrient}: {value}\n"
            
            response += "\n"
        
        if len(foods) > 3:
            response += f"...and {len(foods) - 3} more. Please ask about a specific food for detailed information.\n"
        
        return response.strip()
    
    def answer_question(self, question: str, all_foods: List, trimester: int = 1) -> Dict:
        """
        Main method to answer a user question.
        
        Args:
            question: User's question
            all_foods: List of all FoodItem objects from database
            trimester: User's current trimester
            
        Returns:
            Dictionary with answer and metadata
        """
        # Load models if needed (lazy loading)
        if not self._models_loaded:
            try:
                self._load_models()
            except Exception as e:
                print(f"Continuing without AI models: {e}")
        
        # Classify intent
        intent = self.classify_intent(question)
        
        # Extract food entities
        foods = self.extract_food_entities(question, all_foods)
        
        # Generate response
        response = self.generate_response(question, intent, foods, trimester)
        
        return {
            'answer': response,
            'intent': intent,
            'foods_mentioned': [food.name_english for food in foods],
            'trimester': trimester,
            'confidence': 'high' if foods else 'medium'
        }
    
    def get_suggested_questions(self, trimester: int = 1) -> List[str]:
        """
        Get suggested questions based on trimester.
        
        Args:
            trimester: Current trimester
            
        Returns:
            List of suggested questions
        """
        suggestions = {
            1: [
                "Can I eat papaya during first trimester?",
                "What are the benefits of spinach?",
                "Is milk safe during pregnancy?",
                "How much folic acid do I need?",
                "Can I eat eggs during pregnancy?"
            ],
            2: [
                "What foods are good for second trimester?",
                "Can I eat dates now?",
                "Benefits of almonds during pregnancy",
                "How to prepare lentils?",
                "Is yogurt good for pregnancy?"
            ],
            3: [
                "Foods to ease labor naturally",
                "Can I eat papaya in third trimester?",
                "How much ghee should I consume?",
                "Benefits of dates for labor",
                "What foods help with constipation?"
            ]
        }
        return suggestions.get(trimester, suggestions[1])


# Global chatbot instance (singleton)
_chatbot_instance = None


def get_chatbot():
    """Get or create chatbot instance (singleton pattern)."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = MaternalFoodChatbot()
    return _chatbot_instance
