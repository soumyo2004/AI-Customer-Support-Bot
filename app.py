from flask import Flask, request, jsonify
from chat_service import chat_service
from database import init_db, get_db_connection
import uuid
import os
from flask import Flask, request, jsonify, send_from_directory # Add send_from_directory

from dotenv import load_dotenv

load_dotenv() # Load environment variables


app = Flask(__name__)

# Initialize the database on app start
with app.app_context():
    init_db()

@app.route('/')
def health_check():
    return jsonify({"status": "running", "message": "AI Chatbot Support API is active!"})

@app.route('/chat_ui')
def serve_chat_ui():
    return app.send_static_file('index.html') # Flask finds 'index.html' in the 'static' folder

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_query = data.get('query')
    session_id = data.get('session_id')

    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    if not session_id:
        # Generate a new session ID if not provided
        session_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (session_id) VALUES (?)", (session_id,))
        conn.commit()
        conn.close()
        print(f"New session created: {session_id}")

    bot_response = chat_service.get_bot_response(session_id, user_query)

    return jsonify({
        "session_id": session_id,
        "response": bot_response
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
