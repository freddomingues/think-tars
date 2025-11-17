import boto3
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from llm_assistant.pinecone_client import pinecone_client
from data_ingestion.pdf_processor import extract_text_from_pdf_bytes
from config import settings
from ingest.cache_manager import document_cache

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Inicializa cliente S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def index_pdf_bytes(file_bytes, source_name):
    """Indexa PDF na coleção de FAQ."""
    text = extract_text_from_pdf_bytes(file_bytes)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,   # menor
        chunk_overlap=50  # menor overlap
    )
    chunks = splitter.split_text(text)

    # Gera embeddings em batch (muito mais eficiente)
    embeddings = pinecone_client.embedding_model.embed_documents(chunks)

    metadatas = [{"source": source_name, "chunk": i} for i in range(len(chunks))]
    ids = [f"{source_name}_{i}" for i in range(len(chunks))]

    pinecone_client.add_documents(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
        namespace="faqs"
    )
    logger.info(f"❓ [INGEST] Arquivo '{source_name}' indexado em FAQs com {len(chunks)} chunks.")

def list_faqs_in_bucket() -> list[str]:
    """Lista todos os PDFs de FAQs na subpasta faqs/ do bucket."""
    paginator = s3_client.get_paginator("list_objects_v2")
    pdf_keys = []

    for page in paginator.paginate(Bucket=settings.S3_BUCKET_NAME, Prefix=settings.S3_FAQS_PREFIX):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".pdf") and not key.endswith("/"):
                pdf_keys.append(key)
    return pdf_keys

def index_faq_from_s3(s3_key: str):
    """Baixa PDF de FAQ do S3, extrai texto e indexa no ChromaDB."""
    response = s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
    file_bytes = response['Body'].read()
    
    index_pdf_bytes(file_bytes, s3_key)

def index_all_faqs():
    """Indexa todos os FAQs da pasta faqs/ no S3."""
    pdf_keys = list_faqs_in_bucket()
    logger.info(f"❓ [INGEST] Encontrados {len(pdf_keys)} FAQs no S3...")
    
    # Filtra apenas documentos não processados
    unprocessed_keys = document_cache.get_unprocessed_docs(pdf_keys)
    logger.info(f"❓ [INGEST] Processando {len(unprocessed_keys)} FAQs novos/atualizados...")
    
    for key in unprocessed_keys:
        try:
            logger.info(f"❓ [INGEST] Processando FAQ: {key}")
            index_faq_from_s3(key)
            document_cache.mark_processed(key)
        except Exception as e:
            logger.error(f"❌ [INGEST] Erro ao processar {key}: {e}")
            continue
    
    logger.info("✅ [INGEST] Processamento de FAQs concluído!")
    logger.info(f"📊 [INGEST] Cache: {document_cache.get_cache_stats()}")

def search_faqs(query: str, k: int = 5) -> str:
    """Busca trechos de FAQs via Pinecone."""
    results = pinecone_client.search(query=query, k=k, namespace="faqs")
    docs = [r for r in results['documents'][0]]
    return "\n".join(docs) if docs else "Nenhum trecho relevante de FAQ encontrado."
