from ollama import Client

client = Client(host="http://localhost:11434")


def generate_response(prompt: str) -> str:
    response = client.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]