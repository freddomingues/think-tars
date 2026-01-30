# -*- coding: utf-8 -*-
"""
Definições das ferramentas de trading para o assistente de investimento.
Este módulo é independente e não requer Pinecone ou outras dependências.
"""

TRADING_TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "analyze_bitcoin_market",
            "description": """Analisa o mercado de Bitcoin usando análise técnica avançada.
            Retorna análise completa com RSI, médias móveis, suporte/resistência e recomendações de trading.
            Use esta ferramenta quando o usuário pedir análise do mercado, previsões ou recomendações de compra/venda.""",
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
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_status",
            "description": "Obtém o status completo do portfólio incluindo saldos de BTC e USDT, valor total e lucro/prejuízo não realizado.",
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
            "name": "buy_bitcoin",
            "description": """Compra Bitcoin seguindo a estratégia conservadora.
            A quantidade será determinada automaticamente pela estratégia baseada em análise técnica.
            Só compra quando há sinais claros de oportunidade (RSI oversold, preço próximo ao suporte).
            Use apenas quando a análise do mercado indicar que é um bom momento para comprar.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "quantity": {
                        "type": "number",
                        "description": "Quantidade de BTC a comprar (opcional, usa estratégia se não fornecido)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sell_bitcoin",
            "description": """Vende Bitcoin seguindo a estratégia conservadora.
            A quantidade será determinada automaticamente pela estratégia baseada em análise técnica e lucro atual.
            Só vende quando há lucro garantido (take profit) ou stop loss, ou quando sinais técnicos indicam venda.
            Use apenas quando a análise do mercado indicar que é um bom momento para vender.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "quantity": {
                        "type": "number",
                        "description": "Quantidade de BTC a vender (opcional, usa estratégia se não fornecido)"
                    }
                },
                "required": []
            }
        }
    }
]

