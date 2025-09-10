# ollama_service.py
import os
import ollama
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class OllamaService:

    def __init__(self, model: str = MODEL_NAME, gemini_api_key: str = GEMINI_API_KEY):
        self.model = model

        # Configure Gemini if API key is provided
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            self.gemini_model = None

    def generate_answer(self, prompt: str, provider: str = "ollama", system_instruction: str = None) -> str:
        """
        Unified entry point to generate answers.
        provider = "ollama" | "gemini"
        Returns response["message"]["content"] format.
        """
        if provider == "gemini":
            return self._generate_with_gemini(prompt, system_instruction)["message"]["content"]
        else:
            return self._generate_with_ollama(prompt)["message"]["content"]

    def _generate_with_ollama(self, prompt: str) -> dict:
        """
        Calls Ollama API.
        Returns dict in Ollama format.
        """
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return {"message": {"content": response["message"]["content"]}}

    def _generate_with_gemini(self, prompt: str, system_instruction: str = None) -> dict:
        """
        Calls Gemini API.
        Returns dict wrapped in Ollama-like format.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API not configured. Provide GEMINI_API_KEY in .env")

        if system_instruction:
            response = self.gemini_model.generate_content(
                [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ]
            )
        else:
            response = self.gemini_model.generate_content(prompt)

        return {"message": {"content": response.text}}
