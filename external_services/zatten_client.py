# external_services/zatten_client.py
import requests
import json

def send_zatten_message(api_key: str, phone_number: str, attendant_id: str, message: str) -> dict:
    """Envia uma mensagem via API do Zatten."""
    url = "https://zatten.up.railway.app/api/send-message"
    headers = {"Content-Type": "application/json"}
    payload = {
        "apiKey": api_key,
        "phoneNumber": phone_number,
        "attendantId": attendant_id,
        "message": message
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error ao enviar mensagem Zatten: {e}")
        print(f"Response content: {e.response.text}")
        return {"error": str(e), "response_content": e.response.text}
    except requests.exceptions.RequestException as e:
        print(f"Erro inesperado ao enviar mensagem Zatten: {e}")
        return {"error": str(e)}

def send_meta_message(text="hello, world", sentiment_data=None):

    page_id = "1823092665253620"
    psid = "5514998309606"
    acess_token = "EAAQUB0WDUl4BPJOVrbKzyX4MkwiZAj3EvvbRgaJzhvhJ6rMswJuOaNA2F3N4c3xAHiGcZBdrlxsFe0ZAZBfv3ZCwOFhf9ZBBhPZCx0jje2wnCF6QCABdn2nDZA3K2deOa70N97xcy8MYFtdtP1Fx0XVJ503FNqMTjZA6c67GGWuce1chya0QdSP09NtwYg61PVWbV6nmbcGDmOplhMxurZBMuiDZBPNHFeZCVcK5334Xl26X07aZCRz8ZCiEfzrXUIqZCfh"

    url = f"https://graph.facebook.com/v23.0/{page_id}/messages"
    
    payload = {
        "recipient": {"id": psid},
        "messaging_type": "RESPONSE",
        "message": {"text": text}
    }
    
    # Adiciona análise de sentimento aos metadata se disponível
    if sentiment_data:
        payload["messaging_type"] = "MESSAGE_TAG"
        # Adiciona sentimento como metadata
        sentiment = sentiment_data.get('sentiment', 'neutro')
        confidence = sentiment_data.get('confidence', 0.0)
        payload["message"]["metadata"] = f"SENTIMENT_{sentiment.upper()}_{confidence:.0%}"
    
    params = {
        "access_token": acess_token
    }
    
    response = requests.post(url, params=params, json=payload)
    
    # Retorna o JSON de resposta ou mensagem de erro
    try:
        return response.json()
    except Exception:
        return {"error": response.text}