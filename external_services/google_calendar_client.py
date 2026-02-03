# -*- coding: utf-8 -*-
"""
Cliente para integração com Google Calendar API.
Permite consultar horários disponíveis, agendar, cancelar e confirmar eventos.
"""
import os
from datetime import datetime, timedelta, timezone, time
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import logging

logger = logging.getLogger(__name__)

# Escopos necessários para Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# ID do calendário padrão (primary) ou um calendário específico
DEFAULT_CALENDAR_ID = 'primary'


class GoogleCalendarClient:
    """Cliente para interagir com Google Calendar API."""
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Inicializa o cliente do Google Calendar.
        
        Args:
            credentials_path: Caminho para o arquivo credentials.json (OAuth 2.0)
            token_path: Caminho para salvar/carregar o token de acesso
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_CALENDAR_TOKEN_PATH', 'token.json')
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica com Google Calendar API usando OAuth 2.0."""
        creds = None
        
        # Tenta carregar token existente
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                logger.warning(f"Erro ao carregar token: {e}")
        
        # Se não há credenciais válidas, solicita autorização
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Erro ao renovar token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Arquivo de credenciais não encontrado: {self.credentials_path}. "
                        "Baixe o arquivo credentials.json do Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Salva o token para próximas execuções
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.warning(f"Erro ao salvar token: {e}")
        
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("✅ Cliente Google Calendar autenticado com sucesso")
    
    def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30,
        calendar_id: str = DEFAULT_CALENDAR_ID
    ) -> List[Dict[str, Any]]:
        """
        Consulta horários disponíveis em um período.
        
        Args:
            start_date: Data/hora inicial para buscar disponibilidade
            end_date: Data/hora final para buscar disponibilidade
            duration_minutes: Duração do evento em minutos (padrão: 30)
            calendar_id: ID do calendário (padrão: 'primary')
        
        Returns:
            Lista de slots disponíveis com data/hora de início e fim
        """
        try:
            # Busca eventos existentes no período
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Horário de trabalho padrão (9h às 18h)
            work_start = time(9, 0)
            work_end = time(18, 0)
            
            # Gera slots disponíveis
            available_slots = []
            current = start_date.replace(hour=work_start.hour, minute=work_start.minute, second=0, microsecond=0)
            end = end_date.replace(hour=work_end.hour, minute=work_end.minute, second=0, microsecond=0)
            
            # Cria lista de horários ocupados
            busy_times = []
            for event in events:
                if 'start' in event and 'dateTime' in event['start']:
                    start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                    busy_times.append((start, end_time))
            
            # Verifica cada slot de 30 minutos
            while current < end:
                slot_end = current + timedelta(minutes=duration_minutes)
                
                # Verifica se o slot está livre
                is_available = True
                for busy_start, busy_end in busy_times:
                    if (current < busy_end and slot_end > busy_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'start': current.isoformat(),
                        'end': slot_end.isoformat(),
                        'duration_minutes': duration_minutes
                    })
                
                current += timedelta(minutes=30)
            
            return available_slots
            
        except HttpError as e:
            logger.error(f"Erro ao consultar horários disponíveis: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        attendee_email: Optional[str] = None,
        description: str = "",
        location: str = "",
        calendar_id: str = DEFAULT_CALENDAR_ID
    ) -> Optional[Dict[str, Any]]:
        """
        Cria um evento no Google Calendar.
        
        Args:
            summary: Título do evento
            start_time: Data/hora de início
            end_time: Data/hora de fim
            attendee_email: Email do participante (opcional)
            description: Descrição do evento
            location: Local do evento
            calendar_id: ID do calendário
        
        Returns:
            Dados do evento criado ou None em caso de erro
        """
        try:
            event = {
                'summary': summary,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all' if attendee_email else 'none'
            ).execute()
            
            logger.info(f"✅ Evento criado: {created_event.get('id')}")
            return {
                'id': created_event.get('id'),
                'summary': created_event.get('summary'),
                'start': created_event.get('start'),
                'end': created_event.get('end'),
                'htmlLink': created_event.get('htmlLink'),
            }
            
        except HttpError as e:
            logger.error(f"Erro ao criar evento: {e}")
            return None
    
    def cancel_event(
        self,
        event_id: str,
        calendar_id: str = DEFAULT_CALENDAR_ID,
        notify_attendees: bool = True
    ) -> bool:
        """
        Cancela um evento no Google Calendar.
        
        Args:
            event_id: ID do evento a ser cancelado
            calendar_id: ID do calendário
            notify_attendees: Se True, notifica os participantes
        
        Returns:
            True se cancelado com sucesso, False caso contrário
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all' if notify_attendees else 'none'
            ).execute()
            
            logger.info(f"✅ Evento cancelado: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Erro ao cancelar evento: {e}")
            return False
    
    def get_events_by_date(
        self,
        date: datetime,
        calendar_id: str = DEFAULT_CALENDAR_ID
    ) -> List[Dict[str, Any]]:
        """
        Consulta eventos de uma data específica.
        
        Args:
            date: Data para consultar eventos
            calendar_id: ID do calendário
        
        Returns:
            Lista de eventos do dia
        """
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'Sem título'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'attendees': [a.get('email') for a in event.get('attendees', [])],
                })
            
            return formatted_events
            
        except HttpError as e:
            logger.error(f"Erro ao consultar eventos: {e}")
            return []
    
    def get_tomorrow_events(
        self,
        calendar_id: str = DEFAULT_CALENDAR_ID
    ) -> List[Dict[str, Any]]:
        """
        Consulta eventos do próximo dia útil.
        
        Args:
            calendar_id: ID do calendário
        
        Returns:
            Lista de eventos do próximo dia
        """
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        return self.get_events_by_date(tomorrow, calendar_id)


def get_google_calendar_client() -> Optional[GoogleCalendarClient]:
    """
    Factory function para obter instância do cliente Google Calendar.
    Retorna None se as credenciais não estiverem configuradas.
    """
    try:
        credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH', 'credentials.json')
        if not os.path.exists(credentials_path):
            logger.warning("⚠️ Credenciais do Google Calendar não encontradas. Configure GOOGLE_CALENDAR_CREDENTIALS_PATH.")
            return None
        
        return GoogleCalendarClient()
    except Exception as e:
        logger.error(f"Erro ao inicializar cliente Google Calendar: {e}")
        return None
