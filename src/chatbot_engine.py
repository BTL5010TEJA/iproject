# chatbot_engine.py

class ChatbotEngine:
    def __init__(self):
        self.context = {}
        self.model = self.load_model()

    def load_model(self):
        # Load the AI model for generating responses
        pass  # Placeholder for model loading logic

    def get_response(self, user_input):
        # Generate response based on user input and context
        response = self.model.generate(user_input, self.context)
        return response

    def update_context(self, user_input, bot_response):
        # Update the context based on the latest user input and bot response
        self.context['last_user_input'] = user_input
        self.context['last_bot_response'] = bot_response

    def two_way_communication(self):
        while True:
            user_input = input("You: ")
            bot_response = self.get_response(user_input)
            print(f"Bot: {bot_response}")
            self.update_context(user_input, bot_response)