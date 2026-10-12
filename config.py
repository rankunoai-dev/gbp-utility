import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Credentials are loaded from .env — never hardcode here.
    # See .env.example for the required variables.
    BRIGHT_DATA_AUTH: str = ""
    BRIGHT_DATA_WS_URL: str = ""
    
    # 11 Sister Brands under Learning Care Group
    LCG_SISTER_BRANDS: list[str] = [
        "Childtime",
        "La Petite Academy",
        "Tutor Time",
        "The Children's Courtyard",
        "Everbrook Academy",
        "Montessori Unlimited",
        "Creative Kids Learning Centers",
        "Pathways Learning Academy",
        "Young School",
        "Apple Tree Children's Centers",
        "U-GRO Learning Centres"
    ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
