#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module provides a conversation allowing to delete a short URL and the corresponding
handler callbacks."""
from typing import Union

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
from yourls.extensions import YOURLSURLNotExistsError

from bot.constants import DELETE_KEYBOARD_KEY, YOURLS_KEY
from bot.utils import extract_keyword, cancel_button, abort, delete_keyboard, cancel_keyboard

DELETE_STATE = 'delete'
CANCEL_CALLBACK_DATA = 'cancel_url_deletion'
CANCEL_KEYBOARD = cancel_keyboard(CANCEL_CALLBACK_DATA)


def start(update: Update, context: CallbackContext) -> str:
    """
    Initializes the conversation and asks for the short URL to delete.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    message = update.effective_message.reply_text(
        'Which short URL/keyword do you want to delete?', reply_markup=CANCEL_KEYBOARD
    )
    context.user_data[DELETE_KEYBOARD_KEY] = message
    return DELETE_STATE


def delete_url(update: Update, context: CallbackContext) -> Union[str, int]:
    """
    Tries to delete the short URL. On exceptions, asks the user to double check or abort.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    delete_keyboard(context)
    yourls = context.bot_data[YOURLS_KEY]
    keyword = extract_keyword(update.effective_message.text)

    try:
        yourls.delete(keyword)
        update.effective_message.reply_text('Deletion successful.')
        return ConversationHandler.END
    except YOURLSURLNotExistsError:
        message = update.effective_message.reply_text(
            f'The keyword »<code>{keyword}</code>« does not exist. Maybe a typo?',
            reply_markup=CANCEL_KEYBOARD,
        )
        context.user_data[DELETE_KEYBOARD_KEY] = message
        return DELETE_STATE


def build_delete_conversation_handler(user_role: Role) -> ConversationHandler:
    """
    Gives a conversation handler that allows to change delete a short URL. Will only be
    accessible to the users in the :attr:`bot.constants.USER_ROLE` role.

    Args:
        user_role: The user role.

    """
    return ConversationHandler(
        entry_points=[RolesHandler(CommandHandler('delete_url', start), roles=user_role)],
        states={
            DELETE_STATE: [
                MessageHandler(Filters.text & ~Filters.command, delete_url),
                CallbackQueryHandler(cancel_button, pattern=CANCEL_CALLBACK_DATA),
            ]
        },
        fallbacks=[MessageHandler(Filters.all, abort)],
    )
