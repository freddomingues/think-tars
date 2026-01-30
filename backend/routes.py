# -*- coding: utf-8 -*-
"""Rotas da API de demos (Blueprint Flask)."""
import logging
from flask import Blueprint, request, jsonify

from backend import services

logger = logging.getLogger(__name__)

bp = Blueprint("demos", __name__, url_prefix="/api/demos")


@bp.route("/assistants", methods=["GET"])
def list_assistants_route():
    """Lista assistentes disponíveis para demos."""
    data = services.list_assistants()
    return jsonify({"assistants": data})


@bp.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    """
    Faz upload de um PDF e cria um vector store.
    Espera multipart/form-data com:
    - file: arquivo PDF
    - agent_id: (opcional) ID do agente
    
    Retorna: { conversation_id, vector_store_id, agent_id }
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio."}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Apenas arquivos PDF são suportados."}), 400
    
    agent_id = request.form.get('agent_id')
    
    try:
        # Lê o arquivo
        pdf_bytes = file.read()
        
        # Gera ID temporário para a conversa
        import uuid
        temp_conversation_id = str(uuid.uuid4())
        
        # Cria vector store
        logger.info(f"Processando PDF: {file.filename} ({len(pdf_bytes)} bytes)")
        vector_store_id = services.upload_pdf_and_create_vector_store(
            pdf_bytes=pdf_bytes,
            filename=file.filename,
            conversation_id=temp_conversation_id
        )
        
        if not vector_store_id:
            return jsonify({"error": "Erro ao processar PDF."}), 500
        
        # Cria conversa com o vector store
        out = services.create_conversation(agent_id=agent_id, vector_store_id=vector_store_id)
        if not out:
            return jsonify({"error": "Não foi possível criar conversa."}), 500
        
        logger.info(f"PDF processado com sucesso. Vector store: {vector_store_id}")
        return jsonify(out), 201
        
    except Exception as e:
        logger.error(f"Erro ao processar upload: {e}")
        return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500


@bp.route("/conversations", methods=["POST"])
def create_conversation():
    """Cria nova conversa. Body opcional: { \"agent_id\": \"juridico\", \"vector_store_id\": \"vs_xxx\" }."""
    body = request.get_json() or {}
    agent_id = body.get("agent_id")
    vector_store_id = body.get("vector_store_id")
    out = services.create_conversation(agent_id=agent_id, vector_store_id=vector_store_id)
    if not out:
        return jsonify({"error": "Não foi possível criar conversa."}), 500
    return jsonify(out), 201


@bp.route("/conversations/<conversation_id>/messages", methods=["POST"])
def post_message(conversation_id):
    """Envia mensagem na conversa. Body: { \"content\": \"...\" }."""
    body = request.get_json() or {}
    content = (body.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Campo 'content' é obrigatório."}), 400
    out = services.send_message(conversation_id, content)
    if not out:
        return jsonify({"error": "Conversa não encontrada."}), 404
    if "error" in out:
        return jsonify(out), 502
    return jsonify(out), 200


@bp.route("/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """Deleta uma conversa e seus recursos (assistente customizado e vector store)."""
    success = services.cleanup_conversation(conversation_id)
    if not success:
        return jsonify({"error": "Conversa não encontrada ou erro ao limpar recursos."}), 404
    return jsonify({"message": "Conversa deletada com sucesso."}), 200


def register_demo_routes(app):
    """Registra o blueprint de demos e configura CORS para /api/demos."""
    try:
        from flask_cors import CORS
        CORS(app, resources={r"/api/demos/*": {"origins": "*"}})
    except ImportError:
        pass
    app.register_blueprint(bp)
