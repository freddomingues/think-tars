# -*- coding: utf-8 -*-
"""Tools exclusivas do Assistente de Investimento (CryptoAnalyst): trading e Binance."""

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "analyze_bitcoin_market",
            "description": """Analisa o mercado de Bitcoin usando análise técnica avançada.
            Retorna análise completa com RSI, médias móveis, suporte/resistência e recomendações de trading.
            Use esta ferramenta quando o usuário pedir análise do mercado ou previsões.
            NOTA: Esta ferramenta fornece apenas análise de mercado, não executa operações de compra ou venda.""",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_bitcoin_price",
            "description": "Obtém o preço atual do Bitcoin em USDT e estatísticas das últimas 24 horas.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]
