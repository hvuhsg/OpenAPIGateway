from functools import lru_cache

from pydantic import BaseSettings

__all__ = ["get_settings"]


class Settings(BaseSettings):
    secret_key: str

    allow_session_over_http: bool

    qwhale_token: str

    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"
        fields = {
            'secret_key': {
                'env': 'secret_key',
            },
            'allow_session_over_http': {
                'env': "allow_session_over_http"
            },
            'qwhale_token': {
                'env': "qwhale_token"
            },
            'redis_port': {
                'env': "redis_port"
            },
            'redis_host': {
                'env': "redis_host"
            },
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
