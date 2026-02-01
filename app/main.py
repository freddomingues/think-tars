# -*- coding: utf-8 -*-
import sys
import os
import json
import logging
from flask import Flask, request, jsonify
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import OPENAI_API_KEY
from ai.agents import DEFAULT_AGENT_ID
from ai.assistant_manager import create_or_get_assistant_from_registry
from ai.tools.dispatch import dispatch_tool_call
from ai.clients import get_chroma_client_contract, get_chroma_client_faqs, get_embedding_model

from config.logging_config import setup_logging, log_tool_call, log_error

# Configuração de logging
logger = setup_logging()

# --- Inicializações ---
app = Flask(__name__)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
ASSISTANT_ID = None

def initialize_application():
    """Inicializa o assistente LLM a partir do registry (ai.agents)."""
    global ASSISTANT_ID
    logger.info("🚀 Inicializando aplicação...")
    try:
        assistant_id_local = create_or_get_assistant_from_registry(DEFAULT_AGENT_ID)
        if not assistant_id_local:
            raise ValueError("Falha crítica: não foi possível criar/obter Assistant ID.")
        ASSISTANT_ID = assistant_id_local
        logger.info(f"✅ Assistant ID obtido: {ASSISTANT_ID}")
        logger.info("✅ Aplicação inicializada com sucesso!")
    except (APIError, AuthenticationError, RateLimitError, APIConnectionError, ValueError, Exception) as e:
        logger.error(f"❌ ERRO na inicialização: {type(e).__name__}: {e}")
        sys.exit(1)

initialize_application()

logger.info("✅ Base de conhecimento: arquivos enviados pelos clientes na aplicação + Pinecone")

@app.route('/')
def home():
    return (
        'Think TARS — Soluções em IA ativo! '
        '<a href="/demos/">Playground e site</a>'
    )

# API de demos (Playground) e frontend em /demos
from backend.routes import register_demo_routes
register_demo_routes(app)
logger.info("✅ API de demos (Playground) registrada em /api/demos")

# Webhook Z-API (SDR WhatsApp — uso interno)
from backend.zapi_webhook import bp as zapi_bp
app.register_blueprint(zapi_bp)
logger.info("✅ Webhook Z-API registrado em /api/zapi/webhook")

# Serve frontend de demos em /demos (quando frontend/dist existir)
_frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.isdir(_frontend_dist):
    from flask import send_from_directory
    @app.route("/demos")
    @app.route("/demos/")
    def demos_index():
        response = send_from_directory(_frontend_dist, "index.html")
        # Força atualização do cache do navegador
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    @app.route("/demos/<path:path>")
    def demos_static(path):
        p = os.path.join(_frontend_dist, path)
        if os.path.isfile(p):
            response = send_from_directory(_frontend_dist, path)
            # Para assets, permite cache mas com validação
            if path.startswith('assets/'):
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            else:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return response
        response = send_from_directory(_frontend_dist, "index.html")
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    logger.info("✅ Frontend de demos em /demos")
else:
    logger.warning("⚠️ frontend/dist não encontrado. Rode 'cd frontend && npm run build' para servir /demos")

@app.route('/api/tools/search_contracts', methods=['POST'])
def search_contracts():
    data = request.json
    query = data.get("query")
    if not query:
        log_error('app.main', "Missing 'query' parameter")
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        client, namespace = get_chroma_client_contract()
        results = client.search(query=query, k=3, namespace=namespace)
        docs_found = len(results.get('documents', [[]])[0])
        log_tool_call('search_contracts', query, docs_found)
        return jsonify(results), 200
    except Exception as e:
        log_error('app.main', f"Erro na busca de contratos: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/tools/search_faqs', methods=['POST'])
def search_faqs():
    data = request.json
    query = data.get("query")
    if not query:
        log_error('app.main', "Missing 'query' parameter")
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        client, namespace = get_chroma_client_faqs()
        results = client.search(query=query, k=3, namespace=namespace)
        docs_found = len(results.get('documents', [[]])[0])
        log_tool_call('search_faqs', query, docs_found)
        return jsonify(results), 200
    except Exception as e:
        log_error('app.main', f"Erro na busca de FAQs: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Handler de erro global para garantir que sempre retorne JSON em caso de erro
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.exception("Erro interno do servidor")
    return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
