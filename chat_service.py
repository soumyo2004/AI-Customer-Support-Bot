import json
import openai
import os
import uuid
from datetime import datetime
from database import get_db_connection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import sqlite3

load_dotenv() # Load environment variables from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatService:
    def __init__(self, faqs_file='faqs.json', max_history_turns=5):
        self.faqs = self._load_faqs(faqs_file)
        self.vectorizer = TfidfVectorizer()
        self.faq_embeddings = self._generate_faq_embeddings()
        self.max_history_turns = max_history_turns
        self.system_prompt = (
            "You are an AI Customer Support Bot for ExampleCorp. "
            "Your goal is to provide accurate, concise, and helpful answers to customer questions. "
            "Prioritize information from the provided FAQs or conversation history. "
            "If you cannot confidently answer a question or if the user asks to speak to a human, "
            "explicitly state that you are escalating the request to a human agent and ask for their name and preferred contact method (email/phone). "
            "Maintain a friendly and professional tone. Avoid making up information."
        )

    def _load_faqs(self, faqs_file):
        with open(faqs_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _generate_faq_embeddings(self):
        # We'll vectorize the FAQ questions for similarity search
        faq_questions = [faq['question'] for faq in self.faqs]
        if not faq_questions:
            return None
        self.vectorizer.fit(faq_questions) # Fit the vectorizer on FAQ questions
        return self.vectorizer.transform(faq_questions)

    def _find_relevant_faq(self, user_query):
        if not self.faq_embeddings is None:
            user_query_embedding = self.vectorizer.transform([user_query])
            similarities = cosine_similarity(user_query_embedding, self.faq_embeddings)[0]
            max_similarity_index = similarities.argmax()

            if similarities[max_similarity_index] > 0.6:  # Threshold for relevance
                return self.faqs[max_similarity_index]
        return None

    def _get_conversation_history(self, session_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT sender, text FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, self.max_history_turns * 2) # Get up to N turns (user+bot)
        )
        history = cursor.fetchall()
        conn.close()
        # Reverse to get chronological order and format for LLM
        formatted_history = []
        for msg in reversed(history):
            formatted_history.append({"role": "user" if msg['sender'] == 'user' else "assistant", "content": msg['text']})
        return formatted_history

    def _save_message(self, session_id, sender, text):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, sender, text) VALUES (?, ?, ?)",
            (session_id, sender, text)
        )
        conn.commit()
        conn.close()

    def get_bot_response(self, session_id, user_query):
        self._save_message(session_id, 'user', user_query)

        conversation_history = self._get_conversation_history(session_id)
        relevant_faq = self._find_relevant_faq(user_query)

        # Build messages for the LLM
        messages = [{"role": "system", "content": self.system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        if relevant_faq:
            # Inject FAQ directly into the prompt for direct LLM usage
            messages.append({"role": "system", "content":
                f"Here is a relevant FAQ that might answer the user's question:\n"
                f"Question: {relevant_faq['question']}\n"
                f"Answer: {relevant_faq['answer']}\n"
                f"Please use this information if it directly answers the user's query."
            })

        messages.append({"role": "user", "content": user_query})

        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # Or "gpt-4" if you have access
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            bot_response = response.choices[0].message['content'].strip()

            # Simple escalation trigger based on bot's generated response
            if "escalat" in bot_response.lower() or "human agent" in bot_response.lower() or "specialist" in bot_response.lower():
                escalation_message = (
                    "I understand this is a complex issue. "
                    "I'm escalating your request to a human agent who will get back to you shortly. "
                    "Could you please provide your name and preferred contact method (email or phone number)?"
                )
                self._save_message(session_id, 'bot', escalation_message)
                return escalation_message
            else:
                self._save_message(session_id, 'bot', bot_response)
                return bot_response

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            error_response = "I'm sorry, I'm having trouble connecting right now. Please try again later."
            self._save_message(session_id, 'bot', error_response)
            return error_response

# Initialize the chat service
chat_service = ChatService()
