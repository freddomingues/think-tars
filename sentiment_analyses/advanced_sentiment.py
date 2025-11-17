#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema avançado de análise de sentimento com múltiplos modelos.
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

class AdvancedSentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Palavras-chave para contexto específico
        self.positive_keywords = [
            'obrigado', 'obrigada', 'perfeito', 'excelente', 'ótimo', 'bom', 'legal',
            'gostei', 'interessante', 'sim', 'claro', 'entendi', 'beleza', 'show',
            'maravilhoso', 'fantástico', 'incrível', 'top', 'demais', 'massa'
        ]
        
        self.negative_keywords = [
            'não', 'nunca', 'jamais', 'ruim', 'péssimo', 'terrível', 'horrível',
            'problema', 'erro', 'falha', 'defeito', 'reclamação', 'insatisfeito',
            'frustrado', 'irritado', 'chateado', 'bravo', 'raiva', 'ódio'
        ]
        
        self.urgency_keywords = [
            'urgente', 'rápido', 'agora', 'imediato', 'emergência', 'pressa',
            'depressa', 'logo', 'já', 'hoje', 'amanhã', 'asap'
        ]

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analisa o sentimento de um texto usando múltiplos métodos.
        """
        try:
            # Limpa o texto
            cleaned_text = self._clean_text(text)
            
            # Análise com VADER
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
            
            # Análise com TextBlob
            blob = TextBlob(cleaned_text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Análise de palavras-chave
            keyword_analysis = self._analyze_keywords(cleaned_text)
            
            # Análise de urgência
            urgency_score = self._analyze_urgency(cleaned_text)
            
            # Score combinado
            combined_score = self._calculate_combined_score(
                vader_scores, textblob_polarity, keyword_analysis, urgency_score
            )
            
            # Determina o sentimento final
            sentiment = self._determine_sentiment(combined_score)
            confidence = self._calculate_confidence(vader_scores, textblob_polarity, keyword_analysis)
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'vader': vader_scores,
                    'textblob_polarity': textblob_polarity,
                    'textblob_subjectivity': textblob_subjectivity,
                    'keyword_analysis': keyword_analysis,
                    'urgency_score': urgency_score,
                    'combined_score': combined_score
                },
                'timestamp': datetime.now().isoformat(),
                'text_length': len(cleaned_text),
                'word_count': len(cleaned_text.split())
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de sentimento: {e}")
            return {
                'sentiment': 'neutro',
                'confidence': 0.0,
                'scores': {},
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def _clean_text(self, text: str) -> str:
        """Limpa o texto para análise."""
        # Remove emojis e caracteres especiais
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text)
        # Converte para minúsculas
        return text.lower().strip()

    def _analyze_keywords(self, text: str) -> Dict:
        """Analisa palavras-chave no texto."""
        words = text.split()
        
        positive_count = sum(1 for word in words if word in self.positive_keywords)
        negative_count = sum(1 for word in words if word in self.negative_keywords)
        
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            return {'score': 0, 'positive': 0, 'negative': 0, 'ratio': 0}
        
        score = (positive_count - negative_count) / total_keywords
        ratio = positive_count / total_keywords if total_keywords > 0 else 0
        
        return {
            'score': score,
            'positive': positive_count,
            'negative': negative_count,
            'ratio': ratio
        }

    def _analyze_urgency(self, text: str) -> float:
        """Analisa o nível de urgência do texto."""
        words = text.split()
        urgency_count = sum(1 for word in words if word in self.urgency_keywords)
        
        # Normaliza baseado no tamanho do texto
        return min(urgency_count / len(words) * 10, 1.0) if words else 0.0

    def _calculate_combined_score(self, vader_scores: Dict, textblob_polarity: float, 
                                keyword_analysis: Dict, urgency_score: float) -> float:
        """Calcula score combinado de todos os métodos."""
        # Peso para cada método
        vader_weight = 0.4
        textblob_weight = 0.3
        keyword_weight = 0.2
        urgency_weight = 0.1
        
        # Score do VADER (compound score)
        vader_score = vader_scores['compound']
        
        # Score do TextBlob
        textblob_score = textblob_polarity
        
        # Score das palavras-chave
        keyword_score = keyword_analysis['score']
        
        # Combina os scores
        combined = (
            vader_score * vader_weight +
            textblob_score * textblob_weight +
            keyword_score * keyword_weight +
            urgency_score * urgency_weight
        )
        
        return combined

    def _determine_sentiment(self, combined_score: float) -> str:
        """Determina o sentimento baseado no score combinado."""
        if combined_score >= 0.1:
            return 'positivo'
        elif combined_score <= -0.1:
            return 'negativo'
        else:
            return 'neutro'

    def _calculate_confidence(self, vader_scores: Dict, textblob_polarity: float, 
                           keyword_analysis: Dict) -> float:
        """Calcula a confiança da análise."""
        # Confiança baseada na consistência entre os métodos
        vader_confidence = abs(vader_scores['compound'])
        textblob_confidence = abs(textblob_polarity)
        keyword_confidence = abs(keyword_analysis['score'])
        
        # Média das confianças
        avg_confidence = (vader_confidence + textblob_confidence + keyword_confidence) / 3
        
        return min(avg_confidence * 2, 1.0)  # Normaliza para 0-1

    def analyze_conversation_sentiment(self, messages: List[Dict]) -> Dict:
        """Analisa o sentimento geral de uma conversa."""
        if not messages:
            return {'overall_sentiment': 'neutro', 'confidence': 0.0, 'trend': 'estável'}
        
        sentiments = []
        confidences = []
        
        for message in messages:
            if message.get('sender') == 'user':  # Apenas mensagens do usuário
                analysis = self.analyze_sentiment(message.get('message', ''))
                sentiments.append(analysis['sentiment'])
                confidences.append(analysis['confidence'])
        
        if not sentiments:
            return {'overall_sentiment': 'neutro', 'confidence': 0.0, 'trend': 'estável'}
        
        # Determina sentimento geral
        positive_count = sentiments.count('positivo')
        negative_count = sentiments.count('negativo')
        neutral_count = sentiments.count('neutro')
        
        total = len(sentiments)
        
        if positive_count > negative_count and positive_count > neutral_count:
            overall_sentiment = 'positivo'
        elif negative_count > positive_count and negative_count > neutral_count:
            overall_sentiment = 'negativo'
        else:
            overall_sentiment = 'neutro'
        
        # Calcula tendência
        if len(sentiments) >= 3:
            recent_sentiments = sentiments[-3:]
            if recent_sentiments.count('positivo') > recent_sentiments.count('negativo'):
                trend = 'melhorando'
            elif recent_sentiments.count('negativo') > recent_sentiments.count('positivo'):
                trend = 'piorando'
            else:
                trend = 'estável'
        else:
            trend = 'estável'
        
        # Confiança média
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence': avg_confidence,
            'trend': trend,
            'sentiment_distribution': {
                'positivo': positive_count,
                'negativo': negative_count,
                'neutro': neutral_count
            },
            'total_messages': total
        }

# Instância global
sentiment_analyzer = AdvancedSentimentAnalyzer()
