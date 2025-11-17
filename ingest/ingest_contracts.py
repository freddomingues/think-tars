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

def list_pdfs_in_bucket(prefix: str = None) -> list[str]:
    """Lista todos os PDFs do bucket com prefixo opcional."""
    paginator = s3_client.get_paginator("list_objects_v2")
    pdf_keys = []

    paginate_params = {"Bucket": settings.S3_BUCKET_NAME}
    if prefix:
        paginate_params["Prefix"] = prefix

    for page in paginator.paginate(**paginate_params):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".pdf") and not key.endswith("/"):
                pdf_keys.append(key)
    return pdf_keys

def index_pdf_from_s3(s3_key: str):
    """Baixa PDF do S3, extrai texto e indexa no Pinecone."""
    response = s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
    file_bytes = response['Body'].read()

    text = extract_text_from_pdf_bytes(file_bytes)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)

    embeddings = pinecone_client.embedding_model.embed_documents(chunks)
    metadatas = [{"source": s3_key, "chunk": i} for i in range(len(chunks))]
    ids = [f"{s3_key}_{i}" for i in range(len(chunks))]

    pinecone_client.add_documents(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
        namespace="contracts"
    )

    logger.info(f"📄 [INGEST] Arquivo '{s3_key}' indexado em Contracts com {len(chunks)} chunks.")


def index_all_contracts():
    """Indexa todos os contratos da raiz do bucket S3."""
    # Busca PDFs na raiz (sem prefixo) e exclui os da pasta faqs/
    all_pdfs = list_pdfs_in_bucket()  # Sem prefixo = busca na raiz
    pdf_keys = [pdf for pdf in all_pdfs if not pdf.startswith('faqs/')]
    logger.info(f"📄 [INGEST] Encontrados {len(pdf_keys)} contratos no S3...")
    
    # Filtra apenas documentos não processados
    unprocessed_keys = document_cache.get_unprocessed_docs(pdf_keys)
    logger.info(f"📄 [INGEST] Processando {len(unprocessed_keys)} contratos novos/atualizados...")
    
    for key in unprocessed_keys:
        try:
            logger.info(f"📄 [INGEST] Processando contrato: {key}")
            index_pdf_from_s3(key)
            document_cache.mark_processed(key)
        except Exception as e:
            logger.error(f"❌ [INGEST] Erro ao processar {key}: {e}")
            continue
    
    logger.info("✅ [INGEST] Processamento de contratos concluído!")
    logger.info(f"📊 [INGEST] Cache: {document_cache.get_cache_stats()}")

def search_contracts(query: str, k: int = 5) -> str:
    """Busca trechos de contratos via Pinecone."""
    results = pinecone_client.search(query=query, k=k, namespace="contracts")
    docs = [r for r in results['documents'][0]]
    return "\n".join(docs) if docs else "Nenhum trecho relevante de contrato encontrado."
