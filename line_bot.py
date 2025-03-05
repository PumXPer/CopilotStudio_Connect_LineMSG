import requests
from config import LineMsgConfig

config = LineMsgConfig()

class LineBot:
    def __init__(self):
        self.access_token = config.ACCESS_TOKEN
        self.reply_url = config.REPLY_URL  # ควรจะเป็น "https://api.line.me/v2/bot/message/reply"

    def reply_message(self, reply_token, message):
        url = self.reply_url  # ใช้ URL จาก config เพื่อความถูกต้อง
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        payload = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # จะโยน exception หากเกิด error
        return response.json()
