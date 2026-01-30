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
    get_portfolio_status,
    buy_bitcoin,
    sell_bitcoin,
)
from ai.tools.planilha import query_spreadsheet_data
from ai.tools.sdr import schedule_meeting

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
}
