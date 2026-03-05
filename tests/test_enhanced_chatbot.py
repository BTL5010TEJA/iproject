import unittest

class TestEnhancedChatbot(unittest.TestCase):

    def setUp(self):
        # Setup code to initialize chatbot
        self.chatbot = Chatbot()

    def tearDown(self):
        # Cleanup code
        pass

    def test_basic_response(self):
        response = self.chatbot.get_response('Hello!')
        self.assertEqual(response, 'Hi there! How can I assist you today?')

    def test_farewell_response(self):
        response = self.chatbot.get_response('Goodbye!')
        self.assertEqual(response, 'Goodbye! Have a great day!')

    def test_edge_case_empty_input(self):
        response = self.chatbot.get_response('')
        self.assertEqual(response, 'I didn’t understand that. Can you please rephrase?')

    def test_unexpected_input(self):
        response = self.chatbot.get_response('What is the meaning of life?')
        self.assertIn(response, ['That’s an interesting question!', 'Let’s talk about something else.'])

    def test_conversation_flow(self):
        self.chatbot.get_response('Hello!')  # Initial greeting
        response = self.chatbot.get_response('Tell me a joke.')
        self.assertEqual(response, 'Why did the chicken cross the road? To get to the other side!')

if __name__ == '__main__':
    unittest.main()