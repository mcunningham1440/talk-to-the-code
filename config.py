import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

        self.agent_config = [
            {
                "model": "gpt-3.5-turbo",
                "api_key": self.OPENAI_API_KEY
            }
        ]

        self.llm_config = {
            "request_timeout": 600,
            "config_list": self.agent_config,
            "temperature": 0
        }

config = Config()