import os
from dataclasses import dataclass
from enum import Enum
import random
from dotenv import load_dotenv

# Carrega o .env automaticamente
load_dotenv()


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"


@dataclass
class ModelConfig:
    name: str
    temperature: float
    provider: ModelProvider


QWEN3_32B = ModelConfig("qwen/qwen3-32b", 0.2, ModelProvider.GROQ)


class Config:
    # API KEY do Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # Banco SQL
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    SEED = 42
    MODEL = QWEN3_32B
    CONTEXT_WINDOW = 32768


def seed_everything(seed: int = Config.SEED):
    random.seed(seed)
