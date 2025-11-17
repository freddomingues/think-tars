from ingest.ingest_contracts import search_contracts
from ingest.ingest_faqs import search_faqs
from ingest.query_spreadsheet import query_spreadsheet_data

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "search_contracts",
            "description": "Busca trechos de contratos jurídicos relevantes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_faqs",
            "description": "Busca trechos de FAQs relevantes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_spreadsheet",
            "description": """Realiza consultas e análises de dados em planilhas Excel do S3.
            Use esta ferramenta para:
            - Obter informações sobre a estrutura da planilha (colunas, linhas, tipos de dados)
            - Calcular estatísticas descritivas (média, mediana, soma, máximo, mínimo)
            - Analisar KPIs e indicadores
            - Contar valores únicos ou totais
            - Filtrar e visualizar dados
            - Realizar análises de dados e métricas
            
            A planilha padrão é 'base_dados_mock.xlsx' que está no mesmo bucket S3 dos outros arquivos.
            Esta ferramenta é útil para responder perguntas sobre dados, métricas, KPIs e análises.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": """Descrição da consulta ou análise desejada. 
                        Exemplos: 
                        - 'mostrar informações da planilha'
                        - 'calcular média da coluna vendas'
                        - 'contar valores únicos de produtos'
                        - 'analisar KPIs de performance'
                        - 'estatísticas descritivas'
                        - 'filtrar dados onde status é ativo'"""
                    }
                },
                "required": ["query"]
            }
        }
    }
]

AVAILABLE_FUNCTIONS = {
    "search_contracts": search_contracts,
    "search_faqs": search_faqs,
    "query_spreadsheet": query_spreadsheet_data
}
