#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para realizar consultas e análises em planilhas Excel do S3.
"""

import boto3
import pandas as pd
import io
import logging
from typing import Dict, Any, Optional, List
from config import settings

logger = logging.getLogger(__name__)

# Inicializa cliente S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

# Cache para a planilha em memória
_spreadsheet_cache = None
_cache_file_name = None

def load_spreadsheet_from_s3(file_name: str = "base_dados_mock.xlsx") -> Optional[pd.DataFrame]:
    """
    Carrega uma planilha Excel do S3.
    
    Args:
        file_name: Nome do arquivo Excel no bucket S3
        
    Returns:
        DataFrame com os dados da planilha ou None se houver erro
    """
    global _spreadsheet_cache, _cache_file_name
    
    # Verifica se já está em cache
    if _spreadsheet_cache is not None and _cache_file_name == file_name:
        logger.info(f"📊 [SPREADSHEET] Usando planilha em cache: {file_name}")
        return _spreadsheet_cache
    
    try:
        # Busca o arquivo no S3
        logger.info(f"📥 [SPREADSHEET] Carregando planilha do S3: {file_name}")
        
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_name
        )
        
        # Lê o conteúdo do arquivo
        file_bytes = response['Body'].read()
        
        # Carrega o Excel usando pandas
        excel_file = io.BytesIO(file_bytes)
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        # Atualiza cache
        _spreadsheet_cache = df
        _cache_file_name = file_name
        
        logger.info(f"✅ [SPREADSHEET] Planilha carregada com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
        logger.info(f"📋 [SPREADSHEET] Colunas: {', '.join(df.columns.tolist())}")
        
        return df
        
    except s3_client.exceptions.NoSuchKey:
        logger.error(f"❌ [SPREADSHEET] Arquivo '{file_name}' não encontrado no bucket '{settings.S3_BUCKET_NAME}'")
        return None
    except Exception as e:
        logger.error(f"❌ [SPREADSHEET] Erro ao carregar planilha: {e}")
        return None

def get_spreadsheet_info(file_name: str = "base_dados_mock.xlsx") -> Dict[str, Any]:
    """
    Retorna informações sobre a planilha.
    
    Args:
        file_name: Nome do arquivo Excel no bucket S3
        
    Returns:
        Dicionário com informações da planilha
    """
    df = load_spreadsheet_from_s3(file_name)
    
    if df is None:
        return {
            "error": "Não foi possível carregar a planilha",
            "available": False
        }
    
    return {
        "available": True,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "sample_data": df.head(5).to_dict('records'),
        "summary_stats": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
    }

def query_spreadsheet(
    query: str,
    file_name: str = "base_dados_mock.xlsx",
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Realiza uma consulta/análise na planilha.
    
    Args:
        query: Tipo de consulta/análise a realizar
        file_name: Nome do arquivo Excel no bucket S3
        sheet_name: Nome da aba da planilha (opcional)
        
    Returns:
        Dicionário com os resultados da consulta
    """
    df = load_spreadsheet_from_s3(file_name)
    
    if df is None:
        return {
            "error": "Não foi possível carregar a planilha",
            "success": False
        }
    
    # Se houver múltiplas abas, carrega a aba específica
    if sheet_name:
        try:
            excel_file = s3_client.get_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_name
            )
            file_bytes = excel_file['Body'].read()
            excel_file_io = io.BytesIO(file_bytes)
            df = pd.read_excel(excel_file_io, sheet_name=sheet_name, engine='openpyxl')
        except Exception as e:
            logger.error(f"❌ [SPREADSHEET] Erro ao carregar aba '{sheet_name}': {e}")
            return {
                "error": f"Erro ao carregar aba '{sheet_name}': {str(e)}",
                "success": False
            }
    
    try:
        # Análise de KPIs e estatísticas básicas
        query_lower = query.lower()
        
        # Informações gerais
        if "informações" in query_lower or "info" in query_lower or "estrutura" in query_lower:
            return {
                "success": True,
                "type": "info",
                "data": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "data_types": df.dtypes.astype(str).to_dict()
                },
                "message": f"Planilha possui {len(df)} linhas e {len(df.columns)} colunas"
            }
        
        # Estatísticas descritivas
        elif "estatística" in query_lower or "resumo" in query_lower or "describe" in query_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats = df[numeric_cols].describe()
                return {
                    "success": True,
                    "type": "statistics",
                    "data": stats.to_dict(),
                    "message": "Estatísticas descritivas das colunas numéricas"
                }
            else:
                return {
                    "success": True,
                    "type": "statistics",
                    "data": {},
                    "message": "Nenhuma coluna numérica encontrada para análise estatística"
                }
        
        # Valores únicos de uma coluna
        elif "valores únicos" in query_lower or "unique" in query_lower or "distintos" in query_lower:
            # Tenta identificar a coluna mencionada na query
            cols = [col for col in df.columns if col.lower() in query_lower]
            if cols:
                col = cols[0]
                unique_values = df[col].unique().tolist()
                return {
                    "success": True,
                    "type": "unique_values",
                    "column": col,
                    "data": unique_values,
                    "count": len(unique_values),
                    "message": f"Valores únicos da coluna '{col}': {len(unique_values)} valores"
                }
            else:
                # Retorna valores únicos de todas as colunas
                result = {}
                for col in df.columns:
                    unique_count = df[col].nunique()
                    result[col] = {
                        "unique_count": unique_count,
                        "sample_values": df[col].unique()[:10].tolist()
                    }
                return {
                    "success": True,
                    "type": "unique_values_all",
                    "data": result,
                    "message": "Valores únicos de todas as colunas"
                }
        
        # Contagem/agregação
        elif "contar" in query_lower or "count" in query_lower or "quantidade" in query_lower:
            # Tenta identificar filtros na query
            cols = [col for col in df.columns if col.lower() in query_lower]
            if cols:
                col = cols[0]
                value_counts = df[col].value_counts().to_dict()
                return {
                    "success": True,
                    "type": "count",
                    "column": col,
                    "data": value_counts,
                    "total": len(df),
                    "message": f"Contagem de valores da coluna '{col}'"
                }
            else:
                return {
                    "success": True,
                    "type": "count",
                    "data": {"total_rows": len(df)},
                    "message": f"Total de linhas: {len(df)}"
                }
        
        # Média, soma, máximo, mínimo
        elif any(word in query_lower for word in ["média", "médio", "average", "mean"]):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                means = df[numeric_cols].mean().to_dict()
                return {
                    "success": True,
                    "type": "mean",
                    "data": means,
                    "message": "Médias das colunas numéricas"
                }
            else:
                return {
                    "success": False,
                    "error": "Nenhuma coluna numérica encontrada para calcular média"
                }
        
        elif any(word in query_lower for word in ["soma", "total", "sum"]):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                sums = df[numeric_cols].sum().to_dict()
                return {
                    "success": True,
                    "type": "sum",
                    "data": sums,
                    "message": "Somas das colunas numéricas"
                }
            else:
                return {
                    "success": False,
                    "error": "Nenhuma coluna numérica encontrada para calcular soma"
                }
        
        elif any(word in query_lower for word in ["máximo", "maximo", "max", "maior"]):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                maxs = df[numeric_cols].max().to_dict()
                return {
                    "success": True,
                    "type": "max",
                    "data": maxs,
                    "message": "Valores máximos das colunas numéricas"
                }
            else:
                return {
                    "success": False,
                    "error": "Nenhuma coluna numérica encontrada para calcular máximo"
                }
        
        elif any(word in query_lower for word in ["mínimo", "minimo", "min", "menor"]):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                mins = df[numeric_cols].min().to_dict()
                return {
                    "success": True,
                    "type": "min",
                    "data": mins,
                    "message": "Valores mínimos das colunas numéricas"
                }
            else:
                return {
                    "success": False,
                    "error": "Nenhuma coluna numérica encontrada para calcular mínimo"
                }
        
        # Filtrar dados
        elif "filtrar" in query_lower or "filter" in query_lower or "onde" in query_lower:
            # Retorna amostra dos dados
            filtered_df = df.head(100)  # Limita a 100 linhas para não sobrecarregar
            return {
                "success": True,
                "type": "filter",
                "data": filtered_df.to_dict('records'),
                "rows_returned": len(filtered_df),
                "total_rows": len(df),
                "message": f"Primeiras {len(filtered_df)} linhas da planilha"
            }
        
        # Análise de KPIs
        elif "kpi" in query_lower or "indicador" in query_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            result = {
                "kpis": {}
            }
            
            for col in numeric_cols:
                result["kpis"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "sum": float(df[col].sum()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "std": float(df[col].std())
                }
            
            return {
                "success": True,
                "type": "kpis",
                "data": result,
                "message": "Análise de KPIs das colunas numéricas"
            }
        
        # Consulta padrão - retorna amostra dos dados
        else:
            sample_df = df.head(50)
            return {
                "success": True,
                "type": "sample",
                "data": sample_df.to_dict('records'),
                "rows_returned": len(sample_df),
                "total_rows": len(df),
                "column_names": df.columns.tolist(),
                "message": f"Amostra dos dados: {len(sample_df)} de {len(df)} linhas"
            }
    
    except Exception as e:
        logger.error(f"❌ [SPREADSHEET] Erro ao processar query: {e}")
        return {
            "error": f"Erro ao processar consulta: {str(e)}",
            "success": False
        }

# Função principal para ser usada como tool
def query_spreadsheet_data(query: str) -> str:
    """
    Função principal para consultar dados da planilha.
    Esta função será chamada pelo assistente de IA.
    
    Args:
        query: Descrição da consulta/análise desejada
        
    Returns:
        String formatada com os resultados da consulta
    """
    try:
        result = query_spreadsheet(query)
        
        if not result.get("success", False):
            error_msg = result.get("error", "Erro desconhecido")
            return f"❌ Erro ao consultar planilha: {error_msg}"
        
        result_type = result.get("type", "unknown")
        data = result.get("data", {})
        message = result.get("message", "")
        
        # Formata a resposta baseado no tipo
        response = f"📊 {message}\n\n"
        
        if result_type == "info":
            response += f"Linhas: {data.get('rows', 0)}\n"
            response += f"Colunas: {data.get('columns', 0)}\n"
            response += f"Nomes das colunas: {', '.join(data.get('column_names', []))}\n"
        
        elif result_type in ["statistics", "mean", "sum", "max", "min"]:
            for key, value in data.items():
                if isinstance(value, dict):
                    response += f"\n{key}:\n"
                    for k, v in value.items():
                        response += f"  {k}: {v}\n"
                else:
                    response += f"{key}: {value}\n"
        
        elif result_type in ["count", "unique_values"]:
            if isinstance(data, dict):
                for key, value in data.items():
                    response += f"{key}: {value}\n"
            else:
                response += f"Resultado: {data}\n"
        
        elif result_type == "kpis":
            if "kpis" in data:
                for col, kpi_data in data["kpis"].items():
                    response += f"\n📈 KPIs para '{col}':\n"
                    for kpi, value in kpi_data.items():
                        response += f"  {kpi}: {value:.2f}\n"
        
        elif result_type in ["filter", "sample"]:
            records = data if isinstance(data, list) else []
            response += f"\nMostrando {len(records)} registros:\n\n"
            for i, record in enumerate(records[:10], 1):  # Limita a 10 para não ficar muito longo
                response += f"Registro {i}:\n"
                for key, value in record.items():
                    response += f"  {key}: {value}\n"
                response += "\n"
            if len(records) > 10:
                response += f"... e mais {len(records) - 10} registros\n"
        
        else:
            response += f"Resultado: {data}\n"
        
        return response
        
    except Exception as e:
        logger.error(f"❌ [SPREADSHEET] Erro na função query_spreadsheet_data: {e}")
        return f"❌ Erro ao consultar planilha: {str(e)}"

