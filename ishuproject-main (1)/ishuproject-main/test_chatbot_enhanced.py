#!/usr/bin/env python
"""Test enhanced chatbot with comprehensive Q&A."""

import sys
from app import create_app
from models import db
from models.user import User
from models.food import FoodItem
from ai_engine.chatbot import get_chatbot


def test_chatbot():
    """Test the enhanced chatbot system."""
    app = create_app()
    
    print("\n" + "="*80)
    print(" ENHANCED CHATBOT SYSTEM - Q&A QUALITY TEST")
    print("="*80)
    
    with app.app_context():
        # Get test user and foods
        test_user = User.query.first()
        all_foods = FoodItem.query.all()
        
        print(f"\n👤 Test User: {test_user.username}")
        print(f"📊 Trimester: {test_user.current_trimester}")
        print(f"🍎 Available Foods: {len(all_foods)}")
        
        # Get chatbot
        chatbot = get_chatbot()
        
        # Test various question types
        test_questions = [
            {
                'q': "Can I eat papaya during pregnancy?",
                'type': 'safety_check',
                'description': 'Safety Query'
            },
            {
                'q': "What are the benefits of milk?",
                'type': 'benefits',
                'description': 'Benefits Query'
            },
            {
                'q': "What nutrients does spinach contain?",
                'type': 'nutritional_info',
                'description': 'Nutrition Query'
            },
            {
                'q': "How should I prepare lentils?",
                'type': 'preparation',
                'description': 'Preparation Query'
            },
            {
                'q': "What helps with morning sickness?",
                'type': 'health_condition',
                'description': 'Health Condition Query'
            },
            {
                'q': "General pregnancy nutrition advice",
                'type': 'general',
                'description': 'General Query (no specific food)'
            }
        ]
        
        for i, test in enumerate(test_questions, 1):
            print(f"\n{'─' * 80}")
            print(f"\n📝 Test {i}: {test['description']}")
            print(f"   Question: {test['q']}")
            print(f"   Type: {test['type']}")
            
            try:
                result = chatbot.answer_question(
                    question=test['q'],
                    all_foods=all_foods,
                    trimester=test_user.current_trimester
                )
                
                print(f"\n✅ RESPONSE QUALITY ANALYSIS:")
                print(f"   • Intent Detected: {result['intent']}")
                print(f"   • Confidence: {result['confidence']}")
                print(f"   • Foods Mentioned: {result['foods_mentioned'] if result['foods_mentioned'] else 'None'}")
                
                # Analyze answer quality
                answer = result['answer']
                print(f"\n📋 ANSWER PREVIEW (first 300 characters):")
                preview = answer[:300] + ("..." if len(answer) > 300 else "")
                print(f"   {preview}\n")
                
                # Quality metrics
                answer_length = len(answer)
                has_formatting = '**' in answer or '•' in answer or '✅' in answer
                has_structure = '\n' in answer
                
                print(f"✅ QUALITY METRICS:")
                print(f"   • Answer Length: {answer_length} characters")
                print(f"   • Has Formatting: {'✅ Yes' if has_formatting else '❌ No'}")
                print(f"   • Well-Structured: {'✅ Yes' if has_structure else '❌ No'}")
                
                if answer_length < 100:
                    print(f"   ⚠️ Warning: Answer is quite short")
                else:
                    print(f"   ✅ Good answer length")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Test suggested questions
        print(f"\n{'─' * 80}")
        print(f"\n💡 SUGGESTED QUESTIONS FOR TRIMESTER {test_user.current_trimester}:")
        suggestions = chatbot.get_suggested_questions(test_user.current_trimester)
        for j, suggestion in enumerate(suggestions, 1):
            print(f"   {j}. {suggestion}")
        
    print("\n" + "="*80)
    print(" ✅ CHATBOT ENHANCEMENT TEST COMPLETE")
    print("="*80 + "\n")
    
    return True


if __name__ == '__main__':
    try:
        success = test_chatbot()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
