from ollama import Client
from app.core.config import get_ollama_host, get_ollama_model

client = Client(host=get_ollama_host())


def generate_response(prompt: str) -> str:
    response = client.chat(
        model=get_ollama_model(),
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]