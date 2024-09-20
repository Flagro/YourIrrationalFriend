import logging
from decouple import config

from bot.tg_bot import TelegramBot


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    tg_bot = TelegramBot(
        telegram_token=config("TELEGRAM_BOT_TOKEN"),
    )
    tg_bot.run()


if __name__ == "__main__":
    main()
