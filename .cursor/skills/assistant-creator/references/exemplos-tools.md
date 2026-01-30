# Exemplos de definição de tools

Formato OpenAI em `llm_assistant/tools.py`. Implementações em `ingest/`, `trading/`, etc.

---

## Tool sem parâmetros

```python
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
}
```

---

## Tool com parâmetros obrigatórios

```python
{
    "type": "function",
    "function": {
        "name": "search_contracts",
        "description": "Busca trechos de contratos jurídicos relevantes.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    }
}
```

---

## Tool com parâmetro opcional

```python
{
    "type": "function",
    "function": {
        "name": "buy_bitcoin",
        "description": "Compra Bitcoin seguindo a estratégia conservadora. Use quando a análise indicar oportunidade.",
        "parameters": {
            "type": "object",
            "properties": {
                "quantity": {
                    "type": "number",
                    "description": "Quantidade de BTC (opcional; estratégia define se omitido)"
                }
            },
            "required": []
        }
    }
}
```

---

## Registrar em AVAILABLE_FUNCTIONS

```python
# tools.py
from ingest.ingest_contracts import search_contracts
from trading.trading_tools import buy_bitcoin

AVAILABLE_FUNCTIONS = {
    "search_contracts": search_contracts,
    "buy_bitcoin": buy_bitcoin,
    # ...
}
```

---

## Dispatch em app/main.py (requires_action)

Padrões já usados:

- `search_contracts`, `search_faqs`: `(query, k)`
- `query_spreadsheet`: `(query,)`
- `buy_bitcoin`, `sell_bitcoin`: `quantity` opcional; sem args ou `quantity=...`
- `analyze_bitcoin_market`, `get_bitcoin_price`, `get_portfolio_status`: sem argumentos

Ao adicionar nova tool, incluir um `elif` no bloco de tool calls com a assinatura correta e adicionar ao `AVAILABLE_FUNCTIONS`.
