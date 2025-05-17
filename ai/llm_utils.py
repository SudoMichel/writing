import os
import google.generativeai as genai


def configure_llm():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("Google API key not found in environment variables")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')


def generate_llm_response(prompt):
    model = configure_llm()
    response = model.generate_content(prompt)
    return response.text 