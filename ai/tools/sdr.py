# -*- coding: utf-8 -*-
"""Tools exclusivas do assistente SDR (atendimento WhatsApp — uso interno)."""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Registra o agendamento de reunião com especialista. Use quando o cliente aceitar falar com um especialista ou quiser agendar. Retorna confirmação para o cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_name": {"type": "string", "description": "Nome do lead/cliente."},
                    "lead_phone": {"type": "string", "description": "Telefone do lead (com DDI/DDD)."},
                    "interest": {"type": "string", "description": "Resumo do interesse: IA, automação, ou ambos."},
                    "preferred_schedule": {"type": "string", "description": "Preferência de data/horário informada pelo cliente, se houver."},
                    "notes": {"type": "string", "description": "Observações adicionais do lead."},
                },
                "required": ["lead_name", "lead_phone", "interest"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_available_slots",
            "description": "Consulta horários disponíveis no Google Calendar para agendamento. Use quando o cliente perguntar sobre disponibilidade ou quiser agendar uma reunião.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Data/hora inicial para buscar disponibilidade (formato ISO: YYYY-MM-DDTHH:MM:SS ou YYYY-MM-DD). Se não informado, usa hoje."},
                    "end_date": {"type": "string", "description": "Data/hora final para buscar disponibilidade (formato ISO). Se não informado, usa 7 dias a partir de start_date."},
                    "duration_minutes": {"type": "integer", "description": "Duração do evento em minutos (padrão: 30)."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Cria um evento no Google Calendar. Use quando o cliente confirmar um horário para reunião. Retorna link do evento e confirmação.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Título do evento (ex: 'Reunião com [Nome do Cliente] - Think TARS')."},
                    "start_time": {"type": "string", "description": "Data/hora de início no formato ISO (YYYY-MM-DDTHH:MM:SS) ou YYYY-MM-DD HH:MM."},
                    "end_time": {"type": "string", "description": "Data/hora de fim no formato ISO ou YYYY-MM-DD HH:MM. Se não informado, adiciona 30 minutos ao start_time."},
                    "attendee_email": {"type": "string", "description": "Email do cliente/participante (opcional)."},
                    "description": {"type": "string", "description": "Descrição do evento (ex: interesse do cliente, telefone, etc.)."},
                    "location": {"type": "string", "description": "Local do evento (ex: 'Google Meet', 'Presencial', etc.)."},
                },
                "required": ["summary", "start_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_calendar_event",
            "description": "Cancela um evento no Google Calendar. Use quando o cliente solicitar cancelamento de uma reunião agendada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID do evento a ser cancelado. Use get_tomorrow_events ou get_events_by_date para encontrar o ID."},
                    "notify_attendees": {"type": "boolean", "description": "Se True, notifica os participantes do cancelamento (padrão: True)."},
                },
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_events_by_date",
            "description": "Consulta eventos de uma data específica no Google Calendar. Use para verificar a agenda do dia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Data para consultar eventos (formato: YYYY-MM-DD). Se não informado, usa hoje."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_tomorrow_events",
            "description": "Consulta eventos do próximo dia útil no Google Calendar. Use para confirmar a agenda do próximo dia com os clientes.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_tomorrow_agenda",
            "description": "Consulta a agenda do próximo dia e envia mensagens de confirmação para os clientes agendados via WhatsApp. Use diariamente para confirmar reuniões.",
            "parameters": {
                "type": "object",
                "properties": {
                    "send_confirmation": {"type": "boolean", "description": "Se True, envia mensagens de confirmação via WhatsApp (padrão: True)."},
                },
                "required": [],
            },
        },
    },
]


def schedule_meeting(
    lead_name: str,
    lead_phone: str,
    interest: str,
    preferred_schedule: str = "",
    notes: str = "",
) -> str:
    """
    Registra pedido de reunião com especialista (SDR).
    Em produção pode integrar com calendário ou CRM; por ora retorna mensagem de confirmação.
    """
    # Normaliza telefone para exibição
    phone_display = lead_phone.strip()
    pref = f" Preferência: {preferred_schedule}." if preferred_schedule else ""
    obs = f" Observações: {notes}." if notes else ""
    # Aqui pode: salvar em DB, enviar para CRM, criar evento no Google Calendar, etc.
    return (
        f"Reunião anotada para {lead_name} ({phone_display}), interesse em {interest}.{pref}{obs} "
        "Nosso time entrará em contato em breve para confirmar o melhor horário. Obrigado!"
    )


def check_available_slots(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    duration_minutes: int = 30,
) -> str:
    """
    Consulta horários disponíveis no Google Calendar.
    """
    try:
        from external_services.google_calendar_client import get_google_calendar_client
        
        client = get_google_calendar_client()
        if not client:
            return "⚠️ Google Calendar não está configurado. Entre em contato com o administrador."
        
        # Parse das datas
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                except:
                    start = datetime.now(timezone.utc)
        else:
            start = datetime.now(timezone.utc)
        
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                try:
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                except:
                    end = start + timedelta(days=7)
        else:
            end = start + timedelta(days=7)
        
        slots = client.get_available_slots(start, end, duration_minutes)
        
        if not slots:
            return f"❌ Não há horários disponíveis no período de {start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}."
        
        # Formata os slots para exibição
        slots_text = f"✅ Horários disponíveis ({len(slots)} opções):\n\n"
        for i, slot in enumerate(slots[:10], 1):  # Limita a 10 slots
            slot_start = datetime.fromisoformat(slot['start'].replace('Z', '+00:00'))
            slot_end = datetime.fromisoformat(slot['end'].replace('Z', '+00:00'))
            slots_text += f"{i}. {slot_start.strftime('%d/%m/%Y às %H:%M')} - {slot_end.strftime('%H:%M')}\n"
        
        if len(slots) > 10:
            slots_text += f"\n... e mais {len(slots) - 10} horários disponíveis."
        
        return slots_text
        
    except Exception as e:
        logger.error(f"Erro ao consultar horários disponíveis: {e}")
        return f"❌ Erro ao consultar horários disponíveis: {str(e)}"


def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: Optional[str] = None,
    attendee_email: Optional[str] = None,
    description: str = "",
    location: str = "",
    lead_name: Optional[str] = None,
) -> str:
    """
    Cria um evento no Google Calendar e OBRIGATORIAMENTE envia notificação via WhatsApp.
    
    Args:
        summary: Título/resumo do evento
        start_time: Data/hora de início
        end_time: Data/hora de fim (opcional)
        attendee_email: Email do participante (opcional)
        description: Descrição do evento
        location: Local do evento
        lead_name: Nome do lead/cliente (obrigatório para notificação WhatsApp)
    """
    try:
        from external_services.google_calendar_client import get_google_calendar_client
        from external_services.zapi_client import send_text
        from config.settings import AGENDAMENTO_WHATSAPP_NUMBER
        
        client = get_google_calendar_client()
        if not client:
            return "⚠️ Google Calendar não está configurado. Entre em contato com o administrador."
        
        # Parse das datas
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            try:
                start = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            except:
                return "❌ Formato de data/hora inválido. Use YYYY-MM-DDTHH:MM:SS ou YYYY-MM-DD HH:MM"
        
        if end_time:
            try:
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except:
                try:
                    end = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
                except:
                    return "❌ Formato de data/hora de fim inválido."
        else:
            end = start + timedelta(minutes=30)
        
        # Cria o evento no Google Calendar
        event = client.create_event(
            summary=summary,
            start_time=start,
            end_time=end,
            attendee_email=attendee_email,
            description=description,
            location=location
        )
        
        if not event:
            return "❌ Erro ao criar evento no calendário."
        
        event_link = event.get('htmlLink', '')
        result_message = (
            f"✅ Evento criado com sucesso!\n\n"
            f"📅 {summary}\n"
            f"🕐 {start.strftime('%d/%m/%Y às %H:%M')} - {end.strftime('%H:%M')}\n"
            f"{f'👤 Participante: {attendee_email}' if attendee_email else ''}\n"
            f"{f'🔗 Link: {event_link}' if event_link else ''}"
        )
        
        # OBRIGATÓRIO: Enviar notificação via WhatsApp após criar evento
        logger.info(f"🔔 Iniciando envio sistemático de notificação WhatsApp para {AGENDAMENTO_WHATSAPP_NUMBER}")
        try:
            # Extrai nome do lead da description ou usa o parâmetro lead_name
            nome_lead = lead_name or ""
            if not nome_lead and description:
                # Tenta extrair nome do lead da descrição (formato comum: "Lead: Nome" ou similar)
                import re
                nome_match = re.search(r'(?:lead|cliente|nome)[\s:]+([A-Za-zÀ-ÿ\s]+)', description, re.IGNORECASE)
                if nome_match:
                    nome_lead = nome_match.group(1).strip()
            
            # Se ainda não tem nome, tenta extrair do summary
            if not nome_lead:
                # Remove palavras comuns e pega primeira parte
                nome_lead = summary.replace("Reunião com", "").replace("Reunião", "").strip()
                if " - " in nome_lead:
                    nome_lead = nome_lead.split(" - ")[0].strip()
            
            # Formata data/hora para o WhatsApp
            data_formatada = start.strftime('%d/%m/%Y')
            hora_formatada = start.strftime('%H:%M')
            
            # Monta mensagem para WhatsApp
            whatsapp_message = (
                f"📅 *NOVO AGENDAMENTO*\n\n"
                f"👤 *Lead:* {nome_lead if nome_lead else 'Não informado'}\n"
                f"📋 *Assunto:* {summary}\n"
                f"📅 *Data:* {data_formatada}\n"
                f"🕐 *Horário:* {hora_formatada}\n"
            )
            
            if description:
                whatsapp_message += f"\n📝 *Detalhes:* {description[:200]}\n"
            
            if event_link:
                whatsapp_message += f"\n🔗 {event_link}"
            
            # Envia mensagem via Z-API
            whatsapp_sent = send_text(AGENDAMENTO_WHATSAPP_NUMBER, whatsapp_message)
            
            if whatsapp_sent:
                result_message += f"\n\n✅ Notificação enviada via WhatsApp para {AGENDAMENTO_WHATSAPP_NUMBER}"
                logger.info(f"Notificação de agendamento enviada para {AGENDAMENTO_WHATSAPP_NUMBER}: {summary}")
            else:
                result_message += f"\n\n⚠️ Evento criado, mas falha ao enviar notificação WhatsApp para {AGENDAMENTO_WHATSAPP_NUMBER}"
                logger.warning(f"Falha ao enviar notificação WhatsApp após criar evento: {summary}")
                
        except Exception as whatsapp_error:
            logger.error(f"Erro ao enviar notificação WhatsApp: {whatsapp_error}")
            result_message += f"\n\n⚠️ Evento criado, mas erro ao enviar notificação WhatsApp: {str(whatsapp_error)}"
        
        return result_message
        
    except Exception as e:
        logger.error(f"Erro ao criar evento: {e}")
        return f"❌ Erro ao criar evento: {str(e)}"


def cancel_calendar_event(
    event_id: str,
    notify_attendees: bool = True,
) -> str:
    """
    Cancela um evento no Google Calendar.
    """
    try:
        from external_services.google_calendar_client import get_google_calendar_client
        
        client = get_google_calendar_client()
        if not client:
            return "⚠️ Google Calendar não está configurado. Entre em contato com o administrador."
        
        success = client.cancel_event(event_id, notify_attendees=notify_attendees)
        
        if success:
            return f"✅ Evento cancelado com sucesso. {'Participantes foram notificados.' if notify_attendees else ''}"
        else:
            return "❌ Erro ao cancelar evento. Verifique se o ID do evento está correto."
        
    except Exception as e:
        logger.error(f"Erro ao cancelar evento: {e}")
        return f"❌ Erro ao cancelar evento: {str(e)}"


def get_events_by_date(date: Optional[str] = None) -> str:
    """
    Consulta eventos de uma data específica.
    """
    try:
        from external_services.google_calendar_client import get_google_calendar_client
        
        client = get_google_calendar_client()
        if not client:
            return "⚠️ Google Calendar não está configurado. Entre em contato com o administrador."
        
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d')
            except:
                return "❌ Formato de data inválido. Use YYYY-MM-DD"
        else:
            target_date = datetime.now(timezone.utc)
        
        events = client.get_events_by_date(target_date)
        
        if not events:
            return f"📅 Nenhum evento agendado para {target_date.strftime('%d/%m/%Y')}."
        
        events_text = f"📅 Eventos do dia {target_date.strftime('%d/%m/%Y')} ({len(events)}):\n\n"
        for i, event in enumerate(events, 1):
            start = event['start']
            if 'T' in start:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_str = start_dt.strftime('%H:%M')
            else:
                start_str = "Dia inteiro"
            
            events_text += f"{i}. {event['summary']} - {start_str}\n"
            if event.get('attendees'):
                events_text += f"   👤 Participantes: {', '.join(event['attendees'])}\n"
        
        return events_text
        
    except Exception as e:
        logger.error(f"Erro ao consultar eventos: {e}")
        return f"❌ Erro ao consultar eventos: {str(e)}"


def get_tomorrow_events() -> str:
    """
    Consulta eventos do próximo dia útil.
    """
    try:
        from external_services.google_calendar_client import get_google_calendar_client
        
        client = get_google_calendar_client()
        if not client:
            return "⚠️ Google Calendar não está configurado. Entre em contato com o administrador."
        
        events = client.get_tomorrow_events()
        
        if not events:
            tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
            return f"📅 Nenhum evento agendado para {tomorrow.strftime('%d/%m/%Y')}."
        
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        events_text = f"📅 Agenda de amanhã ({tomorrow.strftime('%d/%m/%Y')}) - {len(events)} evento(s):\n\n"
        for i, event in enumerate(events, 1):
            start = event['start']
            if 'T' in start:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_str = start_dt.strftime('%H:%M')
            else:
                start_str = "Dia inteiro"
            
            events_text += f"{i}. {event['summary']} - {start_str}\n"
            if event.get('attendees'):
                events_text += f"   👤 Participantes: {', '.join(event['attendees'])}\n"
            if event.get('description'):
                events_text += f"   📝 {event['description'][:100]}...\n"
        
        return events_text
        
    except Exception as e:
        logger.error(f"Erro ao consultar eventos de amanhã: {e}")
        return f"❌ Erro ao consultar eventos: {str(e)}"


def confirm_tomorrow_agenda(send_confirmation: bool = True) -> str:
    """
    Consulta a agenda do próximo dia e envia mensagens de confirmação para os clientes.
    """
    try:
        from external_services.google_calendar_client import get_google_calendar_client
        from external_services.zapi_client import send_text
        
        client = get_google_calendar_client()
        if not client:
            return "⚠️ Google Calendar não está configurado."
        
        events = client.get_tomorrow_events()
        
        if not events:
            tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
            return f"📅 Nenhum evento agendado para {tomorrow.strftime('%d/%m/%Y')}. Nada a confirmar."
        
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        confirmed_count = 0
        
        confirmation_text = f"📅 Confirmação de agenda - {tomorrow.strftime('%d/%m/%Y')}:\n\n"
        
        for event in events:
            start = event['start']
            if 'T' in start:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_str = start_dt.strftime('%H:%M')
            else:
                start_str = "Dia inteiro"
            
            confirmation_text += f"✅ {event['summary']} - {start_str}\n"
            
            if send_confirmation and event.get('attendees'):
                # Envia confirmação via WhatsApp para cada participante
                for attendee_email in event['attendees']:
                    # Extrai telefone do email ou usa o email como referência
                    # Nota: Em produção, você pode ter um mapeamento email -> telefone
                    message = (
                        f"Olá! Este é um lembrete automático da Think TARS.\n\n"
                        f"📅 Você tem uma reunião agendada para amanhã ({tomorrow.strftime('%d/%m/%Y')}) às {start_str}.\n"
                        f"📋 {event['summary']}\n\n"
                        f"Por favor, confirme sua presença ou entre em contato se precisar reagendar.\n\n"
                        f"Obrigado!"
                    )
                    # Nota: send_text precisa do número de telefone, não email
                    # Em produção, você precisaria de um mapeamento email -> telefone
                    # Por ora, apenas registra a confirmação
                    confirmed_count += 1
        
        confirmation_text += f"\n✅ {confirmed_count} confirmação(ões) enviada(s)."
        
        return confirmation_text
        
    except Exception as e:
        logger.error(f"Erro ao confirmar agenda: {e}")
        return f"❌ Erro ao confirmar agenda: {str(e)}"
