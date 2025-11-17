# -*- coding: utf-8 -*-
import time
import sys
import os
import json
import asyncio
import logging
from asyncio import Queue
import queue
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import OPENAI_API_KEY, ZATTEN_API_KEY, ZATTEN_ATTENDANT_ID
from llm_assistant.assistant_manager import create_or_get_assistant, update_assistant_instructions, list_all_assistants
from llm_assistant.prompt_templates import DEFAULT_ASSISTANT_INSTRUCTIONS
from llm_assistant.tools import AVAILABLE_FUNCTIONS, TOOLS_DEFINITION
from sentiment_analyses.sentiment import analisar_sentimento
from sentiment_analyses.advanced_sentiment import sentiment_analyzer
from data_store.conversation_schema import conversation_manager
from data_store.dynamodb_handler import get_user_thread_id, save_user_thread_id
from external_services.zatten_client import send_zatten_message, send_meta_message
from llm_assistant.clients import get_chroma_client_contract, get_chroma_client_faqs, get_embedding_model
from ingest.ingest_contracts import index_all_contracts
from ingest.ingest_faqs import index_all_faqs

from logging_config import setup_logging, log_webhook_received, log_tool_call, log_ai_response, log_error, log_success

# Configuração de logging
logger = setup_logging()

# --- Inicializações ---
app = Flask(__name__)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
ASSISTANT_ID = None
user_locks = {}

# Inicializa o conversation_manager
conversation_manager._load_tables()

# Loop global
try:
    event_loop = asyncio.get_running_loop()
except RuntimeError:
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

# === Fila e pool de threads ===
message_queue = queue.Queue(maxsize=100)
executor = ThreadPoolExecutor(max_workers=4)

def initialize_application():
    """Inicializa o assistente LLM."""
    global ASSISTANT_ID
    logger.info("🚀 Inicializando aplicação...")
    try:
        assistant_id_local = create_or_get_assistant("Assistente Jurídico de Contratos")
        if not assistant_id_local:
            raise ValueError("Falha crítica: não foi possível criar/obter Assistant ID.")
        ASSISTANT_ID = assistant_id_local
        logger.info(f"✅ Assistant ID obtido: {ASSISTANT_ID}")
        logger.info("✅ Aplicação inicializada com sucesso!")
    except (APIError, AuthenticationError, RateLimitError, APIConnectionError, ValueError, Exception) as e:
        logger.error(f"❌ ERRO na inicialização: {type(e).__name__}: {e}")
        sys.exit(1)

initialize_application()

logger.info("📄 Iniciando indexação de documentos do S3...")
index_all_contracts()
index_all_faqs()
logger.info("✅ Indexação completa finalizada!")

@app.route('/')
def home():
    return "Assistente Jurídico de Contratos ativo!"

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

@app.route('/api/tools/query_spreadsheet', methods=['POST'])
def query_spreadsheet():
    """Endpoint para consultas em planilhas Excel do S3."""
    data = request.json
    query = data.get("query")
    if not query:
        log_error('app.main', "Missing 'query' parameter")
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        from ingest.query_spreadsheet import query_spreadsheet_data
        result = query_spreadsheet_data(query)
        log_tool_call('query_spreadsheet', query, len(result) if result else 0)
        return jsonify({"result": result}), 200
    except Exception as e:
        log_error('app.main', f"Erro na consulta de planilha: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# --- Webhook Zatten (async polling com Lock) ---
async def process_message_async(phone_number: str, message_content: str):
    logger.info(f"🔄 [PROCESS] Iniciando processamento para {phone_number}")
    log_webhook_received(phone_number, message_content, "LEAD_INTERACTION")

    if phone_number not in user_locks:
        user_locks[phone_number] = asyncio.Lock()

    async with user_locks[phone_number]:
        thread_id = get_user_thread_id(phone_number)
        if not thread_id:
            logger.info(f"🆕 [THREAD] Criando nova thread para {phone_number}")
            thread = openai_client.beta.threads.create()
            thread_id = thread.id
            save_user_thread_id(phone_number, thread_id)
        else:
            logger.info(f"🔄 [THREAD] Usando thread existente: {thread_id}")

        try:
            # Análise de sentimento da mensagem
            logger.info(f"🎭 [SENTIMENT] Analisando sentimento da mensagem...")
            sentiment_analysis = sentiment_analyzer.analyze_sentiment(message_content)
            logger.info(f"🎭 [SENTIMENT] {phone_number} - Sentimento: {sentiment_analysis['sentiment']} (Confiança: {sentiment_analysis['confidence']:.2f})")
            
            # Salva mensagem e análise no banco
            logger.info(f"💾 [DATABASE] Salvando mensagem no banco...")
            message_id = conversation_manager.save_message(
                conversation_id=thread_id,
                phone_number=phone_number,
                message=message_content,
                sender='user'
            )
            
            if message_id:
                logger.info(f"✅ [DATABASE] Mensagem salva com ID: {message_id}")
                conversation_manager.save_sentiment_analysis(
                    message_id=message_id,
                    conversation_id=thread_id,
                    sentiment_data=sentiment_analysis
                )
                logger.info(f"✅ [DATABASE] Análise de sentimento salva")
            else:
                logger.error(f"❌ [DATABASE] Falha ao salvar mensagem")

            # Adiciona mensagem do usuário na thread
            openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_content
            )

            # Gera run do assistant
            run = openai_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=ASSISTANT_ID
            )

            # Loop de processamento com suporte a tool calls
            while run.status in ['queued', 'in_progress', 'requires_action']:
                if run.status == 'requires_action':
                    # Processa tool calls
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"🔧 [TOOL] Executando tool: {function_name} com args: {function_args}")
                        
                        # Executa a função correspondente
                        if function_name in AVAILABLE_FUNCTIONS:
                            try:
                                function_to_call = AVAILABLE_FUNCTIONS[function_name]
                                
                                # Chama a função com os argumentos
                                if function_name == "query_spreadsheet":
                                    result = function_to_call(function_args.get("query", ""))
                                elif function_name in ["search_contracts", "search_faqs"]:
                                    result = function_to_call(
                                        function_args.get("query", ""),
                                        function_args.get("k", 5)
                                    )
                                else:
                                    result = function_to_call(**function_args)
                                
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": str(result) if not isinstance(result, str) else result
                                })
                                
                                log_tool_call(function_name, str(function_args), len(str(result)))
                                logger.info(f"✅ [TOOL] Tool {function_name} executada com sucesso")
                                
                            except Exception as e:
                                logger.error(f"❌ [TOOL] Erro ao executar {function_name}: {e}")
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": f"Erro ao executar tool: {str(e)}"
                                })
                        else:
                            logger.warning(f"⚠️  [TOOL] Função {function_name} não encontrada em AVAILABLE_FUNCTIONS")
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": f"Função {function_name} não disponível"
                            })
                    
                    # Submete os resultados das tools
                    run = openai_client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    logger.info(f"📤 [TOOL] {len(tool_outputs)} tool outputs submetidos")
                
                await asyncio.sleep(1)
                run = openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            if run.status == 'completed':
                logger.info(f"✅ [AI] Resposta gerada com sucesso")
                messages_page = openai_client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
                assistant_messages = [msg for msg in messages_page.data if msg.role == "assistant" and msg.run_id == run.id]
                if assistant_messages:
                    response_text = assistant_messages[0].content[0].text.value
                    log_ai_response(phone_number, response_text)
                    
                    # Salva resposta do assistente no banco
                    logger.info(f"💾 [DATABASE] Salvando resposta do assistente...")
                    assistant_message_id = conversation_manager.save_message(
                        conversation_id=thread_id,
                        phone_number=phone_number,
                        message=response_text,
                        sender='assistant'
                    )
                    
                    if assistant_message_id:
                        logger.info(f"✅ [DATABASE] Resposta do assistente salva com ID: {assistant_message_id}")
                    else:
                        logger.error(f"❌ [DATABASE] Falha ao salvar resposta do assistente")
                    
                    # Envia resposta com análise de sentimento da mensagem original
                    send_meta_message(response_text, sentiment_data=sentiment_analysis)
                    logger.info(f"📤 [ZATTEN] Resposta enviada para {phone_number} com sentimento: {sentiment_analysis['sentiment']}")
                    return {"status": "success", "response": response_text}

            send_meta_message("Desculpe, não consegui gerar uma resposta agora.")
            return {"status": "error"}

        except Exception as e:
            logger.error(f"❌ [WEBHOOK] Erro no processamento: {e}")
            send_meta_message("Ocorreu um erro interno e não consigo responder no momento.")
            return {"status": "error"}

def background_worker():
    """Worker que consome mensagens da fila e processa."""
    logger.info("🔄 [WORKER] Worker iniciado")
    while True:
        try:
            logger.info("⏳ [WORKER] Aguardando mensagem na fila...")
            phone_number, message_content = message_queue.get()
            logger.info(f"📥 [WORKER] Processando mensagem de {phone_number}")
            asyncio.run(process_message_async(phone_number, message_content))
            logger.info(f"✅ [WORKER] Mensagem processada com sucesso")
        except Exception as e:
            logger.error(f"❌ [WORKER] Erro ao processar mensagem: {e}")
            import traceback
            traceback.print_exc()
        finally:
            message_queue.task_done()

@app.route('/webhook/zatten', methods=['POST'])
def zatten_webhook():
    data = request.json
    phone_number = data.get('number')
    messages_list = data.get('messages', [])
    event_type = data.get('event')

    logger.info(f"📥 [WEBHOOK] Recebido: {event_type} de {phone_number}")
    logger.info(f"📝 [WEBHOOK] Dados: {json.dumps(data, indent=2)}")

    if event_type != 'LEAD_INTERACTION' or not messages_list:
        logger.info(f"⏭️ [WEBHOOK] Pulando: {event_type}")
        return jsonify({"status": "skipped"}), 200

    message_content = messages_list[0].get('message', '').strip()
    if not message_content:
        logger.info("⏭️ [WEBHOOK] Pulando: mensagem vazia")
        return jsonify({"status": "skipped"}), 200

    logger.info(f"💬 [WEBHOOK] Processando mensagem: {message_content[:50]}...")

    # Proteção contra fila cheia
    if message_queue.full():
        logger.warning("⚠️ [QUEUE] Fila cheia, descartando mensagem")
        return jsonify({"status": "queue_full"}), 429

    # Enfileira mensagem no loop global
    event_loop.call_soon_threadsafe(message_queue.put_nowait, (phone_number, message_content))
    logger.info(f"🚀 [WEBHOOK] Mensagem enfileirada para {phone_number}")
    return jsonify({"status": "queued"}), 200

# 🔧 Inicia o worker após todas as definições
Thread(target=background_worker, daemon=True).start()
logger.info("🧵 Worker background iniciado para processamento assíncrono.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
