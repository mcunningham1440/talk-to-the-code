import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    def __init__(self):
        self.code_dir = "../T2TC"

        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

        self.agent_config = [
            {
                # "model": "gpt-4-turbo",
                "model": "gpt-3.5-turbo",
                "api_key": self.OPENAI_API_KEY
            }
        ]

        self.llm_config = {
            "timeout": 600,
            "config_list": self.agent_config,
            "temperature": 0
        }

        self.ignore = [
            "__pycache__",
            ".venv",
            ".git",
            "sandbox.ipynb"
            ]
        
        self.sampling_freq = 44100

        self.speech_output_mode = "local"

config = Config()