import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    model_name: str
    provider: str  # 'gemini', 'huggingface', 'bert'
    api_key: Optional[str] = None
    model_path: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.7
    
class ModelsManager:
    """Manages different AI models for chatbot responses"""
    
    def __init__(self):
        self.models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize available models"""
        return {
            'gemini': ModelConfig(
                model_name='gemini-pro',
                provider='gemini',
                api_key=os.getenv('GOOGLE_GEMINI_API_KEY'),
                max_tokens=512,
                temperature=0.7
            ),
            'bert': ModelConfig(
                model_name='bert-base-uncased',
                provider='huggingface',
                model_path='bert-base-uncased',
                max_tokens=512,
                temperature=0.5
            ),
            'mistral': ModelConfig(
                model_name='mistral-7b',
                provider='huggingface',
                model_path='mistralai/Mistral-7B-Instruct-v0.1',
                max_tokens=512,
                temperature=0.7
            ),
            'llama': ModelConfig(
                model_name='llama-2-13b',
                provider='huggingface',
                model_path='meta-llama/Llama-2-13b-chat-hf',
                max_tokens=512,
                temperature=0.7
            )
        }
    
    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """Get model configuration by name"""
        return self.models.get(model_name)
    
    def get_all_models(self) -> Dict[str, ModelConfig]:
        """Get all available models"""
        return self.models
    
    def add_model(self, name: str, config: ModelConfig) -> None:
        """Add a new model configuration"""
        self.models[name] = config