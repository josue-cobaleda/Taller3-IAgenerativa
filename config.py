"""
Factoría de proveedores: LLM (Gemini, OpenAI u Ollama) y embeddings.

Variables de entorno relevantes (ver .env.example):
- LLM_PROVIDER: "gemini" (default) | "openai" | "ollama"
- GOOGLE_API_KEY, GEMINI_MODEL
- OPENAI_API_KEY, OPENAI_MODEL
- OLLAMA_MODEL, OLLAMA_BASE_URL
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
CHROMA_PERSIST_DIR = str(ROOT_DIR / "chroma_db_ecomarket")


def get_llm():
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY no está definida. Crea un archivo .env "
                "a partir de .env.example y agrega tu key de Google AI Studio."
            )
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            temperature=0.3,
            google_api_key=api_key,
        )

    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY no está definida. Agrégala en .env."
            )
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3,
            api_key=api_key,
        )

    if LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.3,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    raise ValueError(f"LLM_PROVIDER desconocido: {LLM_PROVIDER!r}")


def get_embeddings():
    """Replica la configuración del Taller 2 para que el índice persistente
    en `chroma_db_ecomarket/` siga matcheando sin re-indexar."""
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
