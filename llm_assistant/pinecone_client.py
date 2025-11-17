from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from config.settings import (
    PINECONE_API_KEY, 
    PINECONE_INDEX_NAME, 
    EMBEDDING_MODEL, 
    OPENAI_API_KEY
)
import logging

logger = logging.getLogger(__name__)

class PineconeClient:
    def __init__(self):
        """Inicializa o cliente Pinecone."""
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY não definida no ambiente ou no arquivo .env")
        
        # Inicializa Pinecone com a nova API
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Conecta ao índice
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        
        # Embeddings OpenAI
        embedding_model = EMBEDDING_MODEL or "text-embedding-ada-002"
        self.embedding_model = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=OPENAI_API_KEY
        )
        
        logger.info(f"✅ Pinecone conectado ao índice: {PINECONE_INDEX_NAME}")

    def add_documents(self, documents: list, embeddings: list, metadatas: list, ids: list, namespace: str = "contracts"):
        """Adiciona documentos ao Pinecone."""
        try:
            # Prepara os vetores para inserção
            vectors = []
            for i, (doc, embedding, metadata, doc_id) in enumerate(zip(documents, embeddings, metadatas, ids)):
                vectors.append({
                    'id': doc_id,
                    'values': embedding,
                    'metadata': {
                        **metadata,
                        'text': doc  # Armazena o texto no metadata
                    }
                })
            
            # Insere em lotes de 100 (limite do Pinecone)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                logger.info(f"📄 Inseridos {len(batch)} vetores no namespace '{namespace}'")
            
            logger.info(f"✅ Total de {len(vectors)} documentos inseridos no namespace '{namespace}'")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir documentos no Pinecone: {e}")
            raise

    def search(self, query: str, k: int = 5, namespace: str = "contracts", filter_dict: dict = None):
        """Busca documentos no Pinecone."""
        try:
            # Gera embedding da query
            query_embedding = self.embedding_model.embed_query(query)
            
            # Realiza a busca
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Formata os resultados para compatibilidade com ChromaDB
            documents = []
            metadatas = []
            distances = []
            ids = []
            
            for match in results.matches:
                documents.append(match.metadata.get('text', ''))
                metadatas.append({k: v for k, v in match.metadata.items() if k != 'text'})
                distances.append(match.score)
                ids.append(match.id)
            
            return {
                'documents': [documents],
                'metadatas': [metadatas],
                'distances': [distances],
                'ids': [ids]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na busca no Pinecone: {e}")
            raise

    def delete_by_ids(self, ids: list, namespace: str = "contracts"):
        """Remove documentos por IDs."""
        try:
            self.index.delete(ids=ids, namespace=namespace)
            logger.info(f"🗑️ Removidos {len(ids)} documentos do namespace '{namespace}'")
        except Exception as e:
            logger.error(f"❌ Erro ao remover documentos do Pinecone: {e}")
            raise

    def get_stats(self, namespace: str = "contracts"):
        """Obtém estatísticas do índice."""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas do Pinecone: {e}")
            return None

# Instância global do cliente
pinecone_client = PineconeClient()

# Funções de compatibilidade com o código existente
def get_pinecone_client_contract():
    """Retorna o cliente Pinecone para contratos."""
    return pinecone_client, "contracts"

def get_pinecone_client_faqs():
    """Retorna o cliente Pinecone para FAQs."""
    return pinecone_client, "faqs"

def get_embedding_model():
    """Retorna o modelo de embeddings OpenAI."""
    return pinecone_client.embedding_model
