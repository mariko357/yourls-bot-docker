#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module provides a conversation allowing to change a short URLs long URL and the
corresponding handler callbacks."""
from ptbcontrib.roles import RolesHandler, Role
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    CallbackContext,
)
from yourls.exceptions import YOURLSAPIError

from bot.constants import YOURLS_KEY, DELETE_KEYBOARD_KEY, CHANGE_URL_KEY
from bot.utils import (
    extract_keyword,
    cancel_button,
    abort,
    delete_keyboard,
    sanitize_protocol,
    cancel_keyboard,
)

GET_KEYWORD_STATE = 'get keyword'
CHANGE_URL_STATE = 'change url'
CANCEL_CALLBACK_DATA = 'cancel_url_exchange'
CANCEL_KEYBOARD = cancel_keyboard(CANCEL_CALLBACK_DATA)


def start(update: Update, context: CallbackContext) -> str:
    """
    Initializes the conversation and asks for the short URL to change the long URL for.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    message = update.effective_message.reply_text(
        'Which short URL/keyword needs updating??',
        reply_markup=CANCEL_KEYBOARD,
    )
    context.user_data[DELETE_KEYBOARD_KEY] = message
    return GET_KEYWORD_STATE


def get_keyword(update: Update, context: CallbackContext) -> str:
    """
    Parses the user input and asks for the new long URL. If the short URL/keyword does not exist
    (see :meth:`bot.utils.check_keyword_existence`), asks the user to double check the input.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    yourls = context.bot_data[YOURLS_KEY]
    keyword = extract_keyword(update.effective_message.text)
    delete_keyboard(context)

    try:
        yourls.expand(keyword)
    except YOURLSAPIError:
        message = update.effective_message.reply_text(
            f'The keyword »<code>{keyword}</code>« does not exist. Maybe a typo?',
            reply_markup=CANCEL_KEYBOARD,
        )
        context.user_data[DELETE_KEYBOARD_KEY] = message
        return GET_KEYWORD_STATE

    context.user_data[CHANGE_URL_KEY] = keyword
    message = update.effective_message.reply_text(
        'Please send the new long URL.', reply_markup=CANCEL_KEYBOARD
    )
    context.user_data[DELETE_KEYBOARD_KEY] = message

    return CHANGE_URL_STATE


def change_url(update: Update, context: CallbackContext) -> int:
    """
    Parses the user input and updates the short URL. On exceptions, the user is informed.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    delete_keyboard(context)
    yourls = context.bot_data[YOURLS_KEY]
    keyword = context.user_data[CHANGE_URL_KEY]
    url = sanitize_protocol(update.effective_message.text)

    try:
        yourls.update(keyword, url, 'auto')
        update.effective_message.reply_text('All done.')
    except YOURLSAPIError:
        update.effective_message.reply_text(
            'Something went wrong. The short URL was not updated. Sorry about that 😕'
        )

    return ConversationHandler.END


def build_change_url_conversation_handler(user_role: Role) -> ConversationHandler:
    """
    Gives a conversation handler that allows to change the URL of a short URL. Will only be
    accessible to the users in the :attr:`bot.constants.USER_ROLE` role.

    Args:
        user_role: The user role.

    """
    return ConversationHandler(
        entry_points=[RolesHandler(CommandHandler('change_url', start), roles=user_role)],
        states={
            GET_KEYWORD_STATE: [
                MessageHandler(Filters.text & ~Filters.command, get_keyword),
                CallbackQueryHandler(cancel_button, pattern=CANCEL_CALLBACK_DATA),
            ],
            CHANGE_URL_STATE: [
                MessageHandler(Filters.text & ~Filters.command, change_url),
                CallbackQueryHandler(cancel_button, pattern=CANCEL_CALLBACK_DATA),
            ],
        },
        fallbacks=[MessageHandler(Filters.all, abort)],
    )
