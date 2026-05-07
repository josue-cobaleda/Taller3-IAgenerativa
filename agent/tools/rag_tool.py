"""Tool de consulta a la base de conocimiento (RAG) — encapsula el Taller 2."""
from pathlib import Path
from typing import List

from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from config import CHROMA_PERSIST_DIR, get_embeddings, get_llm

ROOT_DIR = Path(__file__).resolve().parents[2]
PROMPT_TEMPLATE_PATH = ROOT_DIR / "prompts" / "prompt_general.txt"

_RETRIEVER = None
_LLM = None
_PROMPT = None


def _get_retriever():
    global _RETRIEVER
    if _RETRIEVER is None:
        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=get_embeddings(),
        )
        _RETRIEVER = vectorstore.as_retriever(search_kwargs={"k": 4})
    return _RETRIEVER


def _get_llm_singleton():
    global _LLM
    if _LLM is None:
        _LLM = get_llm()
    return _LLM


def _get_prompt():
    global _PROMPT
    if _PROMPT is None:
        template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
        _PROMPT = PromptTemplate.from_template(template)
    return _PROMPT


class _RagInput(BaseModel):
    query: str = Field(..., description="Pregunta del cliente en lenguaje natural.")


@tool("consultar_politica_o_faq", args_schema=_RagInput)
def consultar_politica_o_faq(query: str) -> dict:
    """Consulta la base de conocimiento de EcoMarket (políticas, catálogo y FAQ) por
    similitud semántica. Úsala para preguntas generales del cliente que NO involucran
    un número de pedido ni una intención de devolver un producto específico.

    Args:
        query: Pregunta del cliente en lenguaje natural.

    Returns:
        dict con `respuesta` (str) y `fuentes` (lista de strings con la metadata de
        los documentos recuperados).
    """
    retriever = _get_retriever()
    docs = retriever.invoke(query)

    if not docs:
        return {
            "respuesta": (
                "No tengo información sobre eso en los documentos de EcoMarket. "
                "Te recomiendo contactar a soporte humano en soporte@ecomarket.com."
            ),
            "fuentes": [],
        }

    contexto = "\n\n".join(d.page_content for d in docs)
    fuentes: List[str] = []
    for d in docs:
        src = d.metadata.get("source") or d.metadata.get("tipo") or "documento"
        if src not in fuentes:
            fuentes.append(str(src))

    chain = _get_prompt() | _get_llm_singleton()
    raw = chain.invoke({"contexto": contexto, "pregunta": query})
    respuesta = getattr(raw, "content", str(raw)).strip()

    return {"respuesta": respuesta, "fuentes": fuentes}
