import os
from dotenv import load_dotenv
import boto3

load_dotenv()

# --- OpenAI ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não definida no ambiente ou no arquivo .env")

ASSISTANT_ID = os.getenv('ASSISTANT_ID')


LLM_MODEL = os.getenv('LLM_MODEL', "gpt-4o")
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')

# --- AWS DynamoDB ---
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "AssistantUserThreads")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# --- Zatten ---
ZATTEN_API_KEY = os.getenv('ZATTEN_API_KEY')
ZATTEN_PHONE_NUMBER = os.getenv('ZATTEN_PHONE_NUMBER')
ZATTEN_ATTENDANT_ID = os.getenv('ZATTEN_ATTENDANT_ID')

# --- AWS S3 ---
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'gen-ai-contratos')
S3_CONTRACTS_PREFIX = os.getenv('S3_CONTRACTS_PREFIX', 'contratos/')
S3_FAQS_PREFIX = os.getenv('S3_FAQS_PREFIX', 'faqs/')

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

# --- Cron Security ---
CRON_SECRET_TOKEN = os.getenv('CRON_SECRET_TOKEN', '')
