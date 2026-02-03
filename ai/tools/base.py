# -*- coding: utf-8 -*-
"""
Registry central de implementações de tools (AVAILABLE_FUNCTIONS).

Cada assistente tem suas próprias tools em juridico, investment, planilha;
o dispatch usa este módulo para resolver nome → função em qualquer chamada de tool.
"""
from ingest.pinecone_search import search_contracts, search_faqs
from ai.trading.trading_tools import (
    analyze_bitcoin_market,
    get_bitcoin_price,
    get_portfolio_status,  # Desabilitada - retorna mensagem de segurança
    buy_bitcoin,  # Desabilitada - retorna mensagem de segurança
    sell_bitcoin,  # Desabilitada - retorna mensagem de segurança
)
from ai.tools.planilha import query_spreadsheet_data
from ai.tools.sdr import (
    schedule_meeting,
    check_available_slots,
    create_calendar_event,
    cancel_calendar_event,
    get_events_by_date,
    get_tomorrow_events,
    confirm_tomorrow_agenda,
)
from ai.tools.marketing import analyze_marketing_metrics
from ai.tools.rh import analyze_hr_metrics
from ai.tools.suporte import search_knowledge_base
from ai.tools.vendas import analyze_sales_funnel
from ai.tools.redacao import analyze_content

# Todas as funções disponíveis para o dispatch (cada assistente usa apenas seu subconjunto)
AVAILABLE_FUNCTIONS = {
    "search_contracts": search_contracts,
    "search_faqs": search_faqs,
    "analyze_bitcoin_market": analyze_bitcoin_market,
    "get_bitcoin_price": get_bitcoin_price,
    "get_portfolio_status": get_portfolio_status,
    "buy_bitcoin": buy_bitcoin,
    "sell_bitcoin": sell_bitcoin,
    "query_spreadsheet": query_spreadsheet_data,
    "schedule_meeting": schedule_meeting,
    "check_available_slots": check_available_slots,
    "create_calendar_event": create_calendar_event,
    "cancel_calendar_event": cancel_calendar_event,
    "get_events_by_date": get_events_by_date,
    "get_tomorrow_events": get_tomorrow_events,
    "confirm_tomorrow_agenda": confirm_tomorrow_agenda,
    "analyze_marketing_metrics": analyze_marketing_metrics,
    "analyze_hr_metrics": analyze_hr_metrics,
    "search_knowledge_base": search_knowledge_base,
    "analyze_sales_funnel": analyze_sales_funnel,
    "analyze_content": analyze_content,
}
