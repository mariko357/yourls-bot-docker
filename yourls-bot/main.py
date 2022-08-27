#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The script that runs the bot."""
import logging
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, Defaults, PicklePersistence

from bot.setup import setup_dispatcher

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='yourls.log',
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read('bot.ini')
    token = config['yourls-bot']['token']
    signature = config['yourls-bot']['signature']
    client = config['yourls-bot']['client']
    cache_timeout = int(config['yourls-bot']['cache_timeout'])
    admin = int(config['yourls-bot']['admins_chat_id'])

    # Create the Updater and pass it your bot's token.
    defaults = Defaults(
        parse_mode=ParseMode.HTML, disable_notification=True, disable_web_page_preview=True
    )
    persistence = PicklePersistence(filename='yourls_db', single_file=False)
    updater = Updater(token, defaults=defaults, persistence=persistence)

    # Register handlers
    setup_dispatcher(updater.dispatcher, client, signature, cache_timeout, admin)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
