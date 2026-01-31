"""BERT-based intent classification for pregnancy food questions."""
import json
import os
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.optim import AdamW
import warnings
warnings.filterwarnings('ignore')


class PregnancyFoodDataset(Dataset):
    """Dataset for pregnancy food questions and intents."""
    
    def __init__(self, questions, labels, tokenizer, max_length=128):
        self.questions = questions
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.questions)
    
    def __getitem__(self, idx):
        question = self.questions[idx]
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            question,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class BertPregnancyIntentClassifier:
    """BERT-based classifier for pregnancy food questions."""
    
    # Intent labels
    INTENTS = {
        'safety_check': 0,      # Is food safe?
        'benefits': 1,          # What are benefits?
        'nutrition': 2,         # Nutritional info
        'preparation': 3,       # How to prepare?
        'quantity': 4,          # How much to eat?
        'precautions': 5,       # Warnings/precautions
        'trimester_specific': 6, # Trimester advice
        'general': 7            # General question
    }
    
    INTENT_NAMES = {v: k for k, v in INTENTS.items()}
    
    def __init__(self, model_path='bert-base-uncased'):
        self.model_path = model_path
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(
            model_path, 
            num_labels=len(self.INTENTS)
        )
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def get_training_data(self):
        """Get training data for pregnancy food intent classification."""
        questions = [
            # Safety check
            "Can I eat spinach during pregnancy?",
            "Is papaya safe in first trimester?",
            "Are raw vegetables safe?",
            "Can pregnant women eat fish?",
            "Is milk safe during pregnancy?",
            "Are eggs safe to eat while pregnant?",
            "Can I consume uncooked foods?",
            "Is caffeine bad for pregnancy?",
            
            # Benefits
            "What are the benefits of almonds?",
            "Why should I eat dates during pregnancy?",
            "What does milk provide to baby?",
            "Benefits of leafy vegetables?",
            "Advantages of eating dates?",
            "Why is folic acid important?",
            "What does calcium do for fetus?",
            
            # Nutrition
            "Nutritional information about spinach?",
            "What nutrients are in milk?",
            "Iron content in lentils?",
            "Calcium sources for pregnancy?",
            "Protein requirements during pregnancy?",
            "What vitamins do I need?",
            "How much folic acid do I need?",
            
            # Preparation
            "How to prepare spinach for pregnancy?",
            "Best way to cook lentils?",
            "How should I prepare eggs?",
            "How to make healthy smoothies?",
            "Recipe for dal?",
            "How to cook rice properly?",
            "Method to prepare vegetables?",
            
            # Quantity
            "How much milk should I drink?",
            "How many almonds per day?",
            "Serving size for vegetables?",
            "How much protein needed daily?",
            "Portion control during pregnancy?",
            "Daily fruit intake?",
            "How many eggs can I eat?",
            
            # Precautions
            "Warnings about papaya?",
            "Risks of raw meat?",
            "Dangers of unpasteurized dairy?",
            "Precautions with seafood?",
            "Foods to avoid during pregnancy?",
            "What causes food poisoning?",
            "Risks of certain foods?",
            
            # Trimester specific
            "First trimester diet plan?",
            "What should I eat in second trimester?",
            "Third trimester nutrition?",
            "Trimester 1 morning sickness?",
            "Best foods for each trimester?",
            "Trimester-wise requirements?",
            
            # General
            "Tell me about pregnancy nutrition",
            "What is a healthy diet?",
            "General advice for pregnant women?",
            "How to maintain health?",
            "What should I know about eating?",
        ]
        
        labels = [
            # Safety
            0, 0, 0, 0, 0, 0, 0, 0,
            # Benefits
            1, 1, 1, 1, 1, 1, 1,
            # Nutrition
            2, 2, 2, 2, 2, 2, 2,
            # Preparation
            3, 3, 3, 3, 3, 3, 3,
            # Quantity
            4, 4, 4, 4, 4, 4, 4,
            # Precautions
            5, 5, 5, 5, 5, 5, 5,
            # Trimester specific
            6, 6, 6, 6, 6, 6,
            # General
            7, 7, 7, 7, 7
        ]
        
        return questions, labels
    
    def train(self, epochs=3, batch_size=8, learning_rate=2e-5):
        """Train the BERT model."""
        print("\n" + "="*80)
        print("TRAINING BERT FOR PREGNANCY FOOD INTENT CLASSIFICATION")
        print("="*80)
        
        # Get training data
        questions, labels = self.get_training_data()
        
        # Create dataset
        dataset = PregnancyFoodDataset(questions, labels, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Optimizer
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        self.model.train()
        total_steps = len(dataloader) * epochs
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            total_loss = 0
            
            for batch_idx, batch in enumerate(dataloader):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                
                if (batch_idx + 1) % 5 == 0:
                    print(f"  Batch {batch_idx + 1}/{len(dataloader)}, Loss: {loss.item():.4f}")
            
            avg_loss = total_loss / len(dataloader)
            print(f"  Average Loss: {avg_loss:.4f}")
        
        print("\n✓ Training complete!")
        return self.model
    
    def classify_intent(self, question):
        """Classify intent of a question."""
        self.model.eval()
        
        encoding = self.tokenizer(
            question,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
        
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        intent_id = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][intent_id].item()
        
        return {
            'intent': self.INTENT_NAMES[intent_id],
            'confidence': confidence,
            'probabilities': {self.INTENT_NAMES[i]: float(p) 
                            for i, p in enumerate(probabilities[0])}
        }
    
    def save_model(self, save_path='models/bert_pregnancy_intent'):
        """Save trained model."""
        os.makedirs(save_path, exist_ok=True)
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        print(f"✓ Model saved to {save_path}")
    
    def load_model(self, model_path='models/bert_pregnancy_intent'):
        """Load trained model."""
        if os.path.exists(model_path):
            self.model = BertForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            self.model.to(self.device)
            print(f"✓ Model loaded from {model_path}")
            return True
        return False


def main():
    """Main training function."""
    print("\nInitializing BERT Intent Classifier...")
    classifier = BertPregnancyIntentClassifier()
    
    # Train model
    classifier.train(epochs=3, batch_size=8)
    
    # Save model
    classifier.save_model()
    
    # Test classification
    print("\n" + "="*80)
    print("TESTING INTENT CLASSIFICATION")
    print("="*80)
    
    test_questions = [
        "Can I eat papaya during pregnancy?",
        "What are the benefits of milk?",
        "How much protein do I need?",
        "How to prepare spinach?",
        "What should I avoid in first trimester?"
    ]
    
    print("\nTesting intent classification:\n")
    for question in test_questions:
        result = classifier.classify_intent(question)
        print(f"Q: {question}")
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.2%})")
        print()


if __name__ == '__main__':
    main()
