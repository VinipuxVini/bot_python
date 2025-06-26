from dataclasses import dataclass
from os import getenv
from typing import List

from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    token: str
    admin_id: str
    pg_url:str
    admin_code:str
    moder_code:str

    @property
    def admins(self) -> List[int]:
        return [int(admin_id) for admin_id in self.admin_id.split(",")]

def load_config() -> Config:
    """Загрузка конфигурации из переменных окружения"""
    return Config(
        token=getenv("BOT_TOKEN", ""),
        admin_id=getenv("ADMIN_ID", ""),
        pg_url=getenv("PG_URL", ""),
        admin_code=getenv("ADMIN_CODE", ""),
        moder_code=getenv("MODER_CODE", ""),
    )
config = load_config() 