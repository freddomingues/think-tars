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

def get_frontend_dist_path():
    """Retorna o caminho para frontend/dist."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

def frontend_dist_exists():
    """Verifica se frontend/dist existe e tem index.html."""
    dist_path = get_frontend_dist_path()
    return os.path.isdir(dist_path) and os.path.isfile(os.path.join(dist_path, "index.html"))

@app.route('/')
def home():
    """Serve o frontend na raiz quando frontend/dist existe, senão retorna mensagem."""
    if frontend_dist_exists():
        from flask import send_from_directory
        response = send_from_directory(get_frontend_dist_path(), "index.html")
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
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

# Serve frontend estático (rotas registradas de forma lazy)
from flask import send_from_directory

@app.route("/assets/<path:path>")
def frontend_assets(path):
    """Serve assets do frontend (JS, CSS, etc.)"""
    if not frontend_dist_exists():
        return jsonify({"error": "Frontend não buildado"}), 404
    _frontend_dist = get_frontend_dist_path()
    assets_dir = os.path.join(_frontend_dist, "assets")
    if os.path.isfile(os.path.join(assets_dir, path)):
        response = send_from_directory(assets_dir, path)
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response
    return jsonify({"error": "Asset não encontrado"}), 404

# Mantém /demos para compatibilidade
@app.route("/demos")
@app.route("/demos/")
def demos_index():
    if not frontend_dist_exists():
        return jsonify({"error": "Frontend não buildado"}), 404
    _frontend_dist = get_frontend_dist_path()
    response = send_from_directory(_frontend_dist, "index.html")
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/demos/<path:path>")
def demos_static(path):
    """Serve arquivos estáticos do frontend em /demos/<path>"""
    if not frontend_dist_exists():
        return jsonify({"error": "Frontend não buildado"}), 404
    _frontend_dist = get_frontend_dist_path()
    p = os.path.join(_frontend_dist, path)
    if os.path.isfile(p):
        response = send_from_directory(_frontend_dist, path)
        if path.startswith('assets/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        else:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    # Fallback para SPA: retorna index.html para rotas do React Router
    response = send_from_directory(_frontend_dist, "index.html")
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# Log de status do frontend (verificação lazy)
if frontend_dist_exists():
    logger.info("✅ Frontend estático configurado (raiz e /demos)")
else:
    logger.warning("⚠️ frontend/dist não encontrado. O frontend será buildado durante o deploy.")

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

# Handler de erro global
@app.errorhandler(404)
def not_found(error):
    """Para rotas de API, retorna JSON. Para outras rotas, tenta servir o frontend (SPA)."""
    # Se for uma rota de API, retorna JSON
    if request.path.startswith('/api/'):
        return jsonify({"error": "Endpoint não encontrado"}), 404
    
    # Para outras rotas, tenta servir o frontend (SPA fallback)
    if frontend_dist_exists():
        _frontend_dist = get_frontend_dist_path()
        from flask import send_from_directory
        response = send_from_directory(_frontend_dist, "index.html")
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.exception("Erro interno do servidor")
    return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
