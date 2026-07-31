import os
import sys
import asyncio
from dotenv import load_dotenv
from app.core.config import settings
from app.services.llm_reasoning.groq_provider import GroqLLMProvider

def test_groq():
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not found in environment.")
        print("Please add GROQ_API_KEY=your_key to backend/.env")
        sys.exit(1)
        
    print(f"Testing GroqLLMProvider using model: {settings.groq_model}")
    print("-" * 50)
    
    try:
        provider = GroqLLMProvider(api_key=api_key, model_name=settings.groq_model)
        
        # We send a tiny prompt to minimize token usage during test
        prompt = "Explain me the process of levitation how does it actually works and is it possible to achieve levitation on earth. ONLY output valid JSON like {\"response\": \"...\"}."
        print(f"Prompt: {prompt}")
        print("Waiting for response...")
        
        response = provider.generate(prompt)
        print("-" * 50)
        print("SUCCESS! Received response from Groq API:")
        print(response)
        
    except Exception as e:
        print("-" * 50)
        print(f"FAILED: Could not generate response.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_groq()
