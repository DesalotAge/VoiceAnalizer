"""Declaring basic config required for our application."""
from betterconf import Config, field


class MainConfig(Config):
    """Declare main configuration constants."""

    TG_TOKEN = field('TG_TOKEN')
    BUCKET_NAME = field('BUCKET_NAME')
