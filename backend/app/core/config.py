import os


def get_ollama_host() -> str:
	return os.getenv("OLLAMA_HOST", "http://localhost:11434")


def get_ollama_model() -> str:
	return os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def get_cors_origins() -> list[str]:
	raw_origins = os.getenv(
		"CORS_ORIGINS",
		"http://localhost:5173,http://127.0.0.1:5173",
	)

	return [
		origin.strip()
		for origin in raw_origins.split(",")
		if origin.strip()
	]
