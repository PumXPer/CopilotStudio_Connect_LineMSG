import configparser

# โหลดไฟล์ config.env ที่มี sections
config = configparser.ConfigParser()
config.read("config.env", encoding="utf-8")

class CopilotConfig:
    CONVO_URL = config.get("COPILOT", "CONVO_URL")
    TOKEN_URL = config.get("COPILOT", "TOKEN_URL")
    SECRET_KEY_COPILOT = config.get("COPILOT", "SECRET_KEY_COPILOT")

class LineMsgConfig:
    ACCESS_TOKEN = config.get("LINE_MSG", "ACCESS_TOKEN")
    REPLY_URL = config.get("LINE_MSG", "REPLY_URL")