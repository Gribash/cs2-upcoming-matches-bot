from typing import List

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_allow_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://cs2matches.online",
    ]

    class Config:
        env_prefix = "CS2_"


settings = Settings()


