# -*- coding: utf-8 -*-
"""Tools exclusivas do assistente SDR (atendimento WhatsApp — uso interno)."""

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
