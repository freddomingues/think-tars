import io
import logging
from pypdf import PdfReader
from openai import OpenAI
from config.settings import OPENAI_API_KEY

logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extrai texto de bytes de um arquivo PDF."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text


def create_vector_store_from_pdf(
    client: OpenAI,
    pdf_bytes: bytes,
    filename: str,
    conversation_id: str
) -> str | None:
    """
    Cria um vector store no OpenAI a partir de um PDF.
    
    Args:
        client: Cliente OpenAI
        pdf_bytes: Bytes do arquivo PDF
        filename: Nome do arquivo
        conversation_id: ID da conversa (usado para nomear o vector store)
    
    Returns:
        ID do vector store criado ou None em caso de erro
    """
    try:
        # Cria o vector store
        vector_store = client.beta.vector_stores.create(
            name=f"Knowledge Base - {conversation_id[:8]}"
        )
        logger.info(f"Vector store criado: {vector_store.id}")
        
        # Faz upload do arquivo PDF diretamente
        file_stream = io.BytesIO(pdf_bytes)
        file_stream.name = filename
        
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[file_stream]
        )
        
        logger.info(f"Arquivo {filename} indexado no vector store {vector_store.id}")
        logger.info(f"Status: {file_batch.status}, File counts: {file_batch.file_counts}")
        
        return vector_store.id
    except Exception as e:
        logger.error(f"Erro ao criar vector store: {e}")
        return None
