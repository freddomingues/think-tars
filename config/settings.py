import os
from dotenv import load_dotenv

load_dotenv()

# --- OpenAI ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não definida no ambiente ou no arquivo .env")

ASSISTANT_ID = os.getenv('ASSISTANT_ID')


LLM_MODEL = os.getenv('LLM_MODEL', "gpt-4o")
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

# --- Pinecone ---
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'genai-documents')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

# --- Binance ---
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# --- Email Notifications ---
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_TO = os.getenv('EMAIL_TO', 'fred_domingues@outlook.com')

# --- Z-API (WhatsApp) — SDR interno ---
ZAPI_BASE_URL = os.getenv('ZAPI_BASE_URL', 'https://api.z-api.io')
ZAPI_INSTANCE_ID = os.getenv('ZAPI_INSTANCE_ID', '')
ZAPI_TOKEN_INSTANCE = os.getenv('ZAPI_TOKEN_INSTANCE', '')
# Token de segurança da conta (Client-Token). Se a Z-API exigir, configure no painel e coloque aqui.
# Ver: https://developer.z-api.io/en/security/client-token
ZAPI_CLIENT_TOKEN = os.getenv('ZAPI_CLIENT_TOKEN', '')
