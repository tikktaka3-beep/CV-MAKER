import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "1691140865"))

settings = Settings()