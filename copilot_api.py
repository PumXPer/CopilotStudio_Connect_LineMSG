import requests
from config import CopilotConfig

config = CopilotConfig()

class CopilotAPI:
    def __init__(self):
        self.convo_url = config.CONVO_URL
        self.token_url = config.TOKEN_URL
        self.secret_key_copilot = config.SECRET_KEY_COPILOT

    def get_token(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret_key_copilot}"
        }
        response = requests.post(self.token_url, headers=headers)
        if response.status_code == 200:
            return response.json()["token"]
        else:
            print(f"Error fetching token: {response.status_code}")
            print(response.text)
            return None

    def start_conversation(self, token):
        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            res = requests.post(self.convo_url, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data.get("conversationId")
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return None
        
    def send_message(self, token, conversation_id, message):
        url = f"{self.convo_url}/{conversation_id}/activities"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "type": "message",
            "from": {"id": "user1"},  # id ของผู้ส่ง (user)
            "text": message
        }

        try:
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
        
    def get_messages(self, token, conversation_id):
        url = f"{self.convo_url}/{conversation_id}/activities" 
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data
        except Exception as e:
            print(f"Error getting messages: {e}")
            return None
        
    def test(self):
        response = {
            "message": "Hello from CopilotAPI",
            "convo_url": self.convo_url,
            "token_url": self.token_url,
            "secret_key_copilot": self.secret_key_copilot
        }
        return response
        
