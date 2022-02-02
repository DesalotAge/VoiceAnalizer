"""Start whole project."""
from config import MainConfig
from google_interaction import GoogleCloudInteraction
from bot import BotConfiguration
from utils import create_all_texts


def main():
    """Maintain whole interface."""
    config = MainConfig()
    google_interaction_module = GoogleCloudInteraction(config.BUCKET_NAME)
    bot = BotConfiguration(
        config.TG_TOKEN,
        google_interaction_module,
        create_all_texts()
    )
    bot.start_bot()


if __name__ == '__main__':
    main()
