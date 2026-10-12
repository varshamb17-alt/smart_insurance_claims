# Smart Insurance Claims

An AI-powered insurance claims management web application built using Python, Flask, SQLite, and Google Gemini AI.

## Features
- Submit insurance claims
- AI-powered claim analysis using Gemini
- Store claims in an SQLite database
- View all insurance claims
- Search claims by name
- Edit and delete claims
- Display total claims and total claim amount

## Technologies Used
- Python
- Flask
- SQLite
- Google Gemini API
- HTML and CSS

## How to Run
1. Install Python.
2. Install the required packages:
   `pip install flask python-dotenv google-genai`
3. Create a `.env` file and add your Gemini API key:
   `GEMINI_API_KEY=your_api_key_here`
4. Run the application:
   `python app.py`
5. Open `http://127.0.0.1:5000` in your browser.

## Security
Keep your API key private. Do not upload `.env` or private API keys to GitHub.