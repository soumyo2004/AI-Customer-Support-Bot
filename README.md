# AI Customer Support Bot

## Table of Contents

- [1. Objective](#1-objective)
- [2. Features](#2-features)
- [3. Technical Stack](#3-technical-stack)
- [4. Project Structure](#4-project-structure)

---

## 1. Objective

This project aims to simulate customer support interactions using an AI-powered chatbot. It handles frequently asked questions (FAQs), maintains conversational context, and intelligently simulates escalation to a human agent when it cannot confidently answer a query or when explicitly requested.

## 2. Features

*   **FAQ Handling:** Answers common questions from a predefined dataset.
*   **Contextual Memory:** Retains the history of the conversation to provide relevant and coherent responses.
*   **Escalation Simulation:** Automatically identifies when a query cannot be answered by the bot or when the user requests human assistance, triggering a simulated escalation process.
*   **RESTful API:** A clean backend API to power chat interactions.
*   **Interactive Frontend (Optional):** A simple, responsive web-based chat interface for user interaction.

## 3. Technical Stack

*   **Backend:** Python 3.x, Flask (Web Framework)
*   **LLM Integration:** OpenAI GPT-3.5 Turbo (via `openai` Python client)
*   **Database:** SQLite3 (for session and message tracking)
*   **FAQ Matching:** TF-IDF Vectorization & Cosine Similarity (using `scikit-learn`)
*   **Environment Management:** `python-dotenv`
*   **Frontend (Optional)::** HTML, CSS, JavaScript (Fetch API)

## 4. Project Structure
```
ai_chatbot_support/
├── .env.example # Template for environment variables
├── .gitignore # Specifies intentionally untracked files to ignore
├── app.py # Flask application, API endpoints
├── chat_service.py # Core chatbot logic: LLM integration, FAQ management, context handling
├── database.py # Database (SQLite) initialization and utility functions
├── faqs.json # Dataset for Frequently Asked Questions
├── requirements.txt # Python dependencies
└── static/ # Frontend static files (HTML, CSS, JS)
└── index.html # Main chat interface HTML file
```
