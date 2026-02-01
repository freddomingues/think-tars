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


@bp.route("/conversations/<conversation_id>/upload-file", methods=["POST"])
def upload_file_to_conversation(conversation_id):
    """
    Faz upload de um arquivo e retorna o file_id da OpenAI.
    Espera multipart/form-data com:
    - file: arquivo (qualquer tipo)
    
    Retorna: { "file_id": "file_xxx" }
    """
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio."}), 400
    
    try:
        from backend.services import get_client
        import io
        import time
        client = get_client()
        
        # Faz upload do arquivo para a OpenAI
        file_bytes = file.read()
        # Cria um objeto file-like a partir dos bytes
        file_obj = io.BytesIO(file_bytes)
        file_obj.name = file.filename
        
        file_stream = client.files.create(
            file=file_obj,
            purpose="assistants"
        )
        
        # Aguarda o arquivo ser processado pela OpenAI (necessário para PDF, Excel, etc.)
        max_wait = 30  # máximo de 30 segundos
        wait_time = 0
        while wait_time < max_wait:
            file_status = client.files.retrieve(file_stream.id)
            if file_status.status == "processed":
                break
            elif file_status.status == "error":
                logger.error(f"Erro ao processar arquivo {file.filename}: {file_status.error}")
                return jsonify({"error": f"Erro ao processar arquivo: {file_status.error}"}), 500
            time.sleep(1)
            wait_time += 1
        
        if wait_time >= max_wait:
            logger.warning(f"Timeout ao processar arquivo {file.filename}, mas continuando...")
        
        logger.info(f"Arquivo {file.filename} enviado e processado pela OpenAI: {file_stream.id}")
        return jsonify({"file_id": file_stream.id}), 201
        
    except Exception as e:
        logger.error(f"Erro ao fazer upload de arquivo: {e}")
        return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500


@bp.route("/conversations/<conversation_id>/messages", methods=["POST"])
def post_message(conversation_id):
    """
    Envia mensagem na conversa. 
    Body: { "content": "...", "file_ids": ["file_xxx", ...] } (file_ids opcional).
    """
    body = request.get_json() or {}
    content = (body.get("content") or "").strip()
    file_ids = body.get("file_ids")  # Lista opcional de file_ids
    
    if not content:
        return jsonify({"error": "Campo 'content' é obrigatório."}), 400
    
    out = services.send_message(conversation_id, content, file_ids=file_ids)
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


@bp.route("/contact/send-to-sdr", methods=["POST"])
def send_to_sdr():
    """
    Envia mensagem para o SDR via WhatsApp.
    Body: { "message": "texto da mensagem" }
    """
    logger.info("Endpoint /contact/send-to-sdr chamado")
    try:
        # Garante que sempre retorna JSON
        if not request.is_json:
            logger.warning("Content-Type não é application/json")
            return jsonify({"error": "Content-Type deve ser application/json"}), 400
        
        body = request.get_json() or {}
        message = (body.get("message") or "").strip()
        if not message:
            logger.warning("Campo 'message' vazio")
            return jsonify({"error": "Campo 'message' é obrigatório."}), 400
        
        logger.info("Tentando enviar mensagem para SDR (tamanho: %d chars)", len(message))
        from external_services.zapi_client import send_text
        from config.settings import SDR_WHATSAPP_NUMBER
        
        if not SDR_WHATSAPP_NUMBER:
            logger.error("SDR_WHATSAPP_NUMBER não configurado")
            return jsonify({"error": "Configuração do servidor incompleta. Contate o suporte."}), 500
        
        success = send_text(SDR_WHATSAPP_NUMBER, message)
        if success:
            logger.info("Mensagem enviada para SDR via WhatsApp: %s", message[:80])
            return jsonify({"success": True, "message": "Mensagem enviada com sucesso!"}), 200
        else:
            logger.warning("Falha ao enviar mensagem para SDR via WhatsApp")
            return jsonify({"error": "Falha ao enviar mensagem. Tente novamente."}), 500
    except Exception as e:
        logger.exception("Erro ao enviar mensagem para SDR: %s", e)
        return jsonify({"error": f"Erro ao enviar mensagem: {str(e)}"}), 500


def register_demo_routes(app):
    """Registra o blueprint de demos e configura CORS para /api/demos."""
    try:
        from flask_cors import CORS
        CORS(app, resources={r"/api/demos/*": {"origins": "*"}})
    except ImportError:
        pass
    app.register_blueprint(bp)
