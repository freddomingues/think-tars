# Importa o cliente Pinecone
from llm_assistant.pinecone_client import (
    get_pinecone_client_contract,
    get_pinecone_client_faqs,
    get_embedding_model
)

# --- Funções utilitárias para main.py (compatibilidade) ---
def get_chroma_client_contract():
    """Retorna o cliente Pinecone para contratos (compatibilidade)."""
    return get_pinecone_client_contract()

def get_chroma_client_faqs():
    """Retorna o cliente Pinecone para FAQs (compatibilidade)."""
    return get_pinecone_client_faqs()
