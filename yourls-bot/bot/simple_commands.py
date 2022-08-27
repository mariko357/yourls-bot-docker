#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The module contains some basic functionality."""
from ptbcontrib.extract_urls import extract_urls
from telegram import MessageEntity, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from yourls import YOURLSKeywordExistsError

from bot.constants import USER_GUIDE, YOURLS_KEY
from bot.utils import sanitize_protocol


def info(update: Update, context: CallbackContext) -> None:
    """
    Returns some info about the bot.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.
    """
    yourls = context.bot_data[YOURLS_KEY]
    text = (
        f'Hi! I am <b>{context.bot.bot.full_name}</b> and here to create and manage short URLs '
        f'with the YOURLS instance hosted at {yourls.url}. Please note that I will only respond '
        f'to users explicitly allowed by my admin.'
        f'\n\nFor details on how to use me, please visit the user guide below. 🙂.'
    )

    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton('User Guide 🤖', url=USER_GUIDE),
            InlineKeyboardButton('Official YOURLS Homepage', url='https://yourls.org'),
            InlineKeyboardButton('This YOURLS instance', url=yourls.url),
        ]
    )

    update.effective_message.reply_text(text, reply_markup=keyboard)


def shorten(update: Update, context: CallbackContext) -> None:
    """
    Shortens all (unique) links contained in a message and sends the short links as reply in the
    order of appearance.

    Args:
        update: The incoming update containing links to shorten.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`

    """
    all_links = (sanitize_protocol(link) for link in extract_urls(update.effective_message))
    unique_links = {}
    for link in all_links:
        if link not in unique_links:
            unique_links[link] = link

    yourls = context.bot_data[YOURLS_KEY]
    message_list = ['The following short links were created:\n']

    for url in unique_links:
        short_url_instance = yourls.shorten(url)
        message_list.append(short_url_instance.shorturl)

    message = '\n'.join(message_list)
    update.effective_message.reply_text(message, disable_web_page_preview=True)


def shorten_with_keyword(update: Update, context: CallbackContext) -> None:
    """
    Given a message with URL (text link or URL) and keyword, in arbitrary order, creates a
    short link with the given keyword and sends it as response.

    Args:
        update: The incoming update containing links to shorten.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`

    """
    entity = update.effective_message.entities[0]
    if entity.type == MessageEntity.TEXT_LINK:
        url = sanitize_protocol(entity.url)
        word = update.effective_message.parse_entity(entity)
    # if entity.type == MessageEntity.URL:
    else:
        entity_text = update.effective_message.parse_entity(entity)
        url = sanitize_protocol(entity_text)
        word = entity_text

    words = update.effective_message.text.split()
    words.remove(word)
    keyword = words[0]

    yourls = context.bot_data[YOURLS_KEY]
    try:
        update.effective_message.reply_text(yourls.shorten(url, keyword=keyword).shorturl)
    except YOURLSKeywordExistsError:
        update.effective_message.reply_text(
            f'The keyword <code>{keyword}</code> is already in use. Please choose another.'
        )
