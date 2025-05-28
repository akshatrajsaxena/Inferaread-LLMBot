import os
from dataclasses import dataclass

@dataclass
class Config:    
    BACKEND_URL: str = "http://localhost:8000"
    PAGE_TITLE: str = "InferaRead - RAG PDF Query System"
    PAGE_ICON: str = ""
    MAX_FILE_SIZE_MB: int = 200
    ALLOWED_FILE_TYPES: list = None
    CHAT_HISTORY_MAX_DISPLAY: int = 50
    DEFAULT_QUERY_EXAMPLES: list = None
    REQUEST_TIMEOUT: int = 30
    UPLOAD_TIMEOUT: int = 60
    
    def __post_init__(self):
        if self.ALLOWED_FILE_TYPES is None:
            self.ALLOWED_FILE_TYPES = ['pdf']        
        if self.DEFAULT_QUERY_EXAMPLES is None:
            self.DEFAULT_QUERY_EXAMPLES = ["What is the main topic of this document?","Summarize the key points in bullet format","What are the main conclusions mentioned?","List all important dates mentioned","What methodology was used?","Who are the main authors or contributors?","What are the key findings?","What recommendations are provided?","Are there any limitations mentioned?","What is the scope of this document?"]
config = Config()