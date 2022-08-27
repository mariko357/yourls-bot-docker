#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module provides a conversation allowing to add a new user."""
from typing import cast

from ptbcontrib.roles import RolesHandler, Role, BOT_DATA_KEY
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    CallbackContext,
)

from bot.utils import cancel_button, abort, delete_keyboard, cancel_keyboard
from .constants import DELETE_KEYBOARD_KEY, USER_ROLE

GET_UID_STATE = 'get user id'
CANCEL_CALLBACK_DATA = 'cancel_user_exchange'
CANCEL_KEYBOARD = cancel_keyboard(CANCEL_CALLBACK_DATA)


def start(update: Update, context: CallbackContext) -> str:
    """
    Initializes the conversation and asks for the ID of the user to add.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    message = update.effective_message.reply_text(
        'Which user do you want to add? You may forward a message or give me their Telegram ID.',
        reply_markup=CANCEL_KEYBOARD,
    )
    context.user_data[DELETE_KEYBOARD_KEY] = message
    return GET_UID_STATE


def get_uid(update: Update, context: CallbackContext) -> str:
    """
    Initializes the conversation and asks for the ID of the user to add.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    delete_keyboard(context)
    role = cast(Role, context.bot_data[BOT_DATA_KEY][USER_ROLE])
    message = update.effective_message

    if message.forward_date:
        if message.forward_from:
            role.add_member(message.forward_from.id)
            message.reply_text(f'User {message.forward_from.full_name} was successfully added.')
            return ConversationHandler.END

        reply_message = message.reply_text(
            "The user apparently disallowed to include their contact details in forwarded "
            "messages, so I can't read their ID from that message. Please send me the ID "
            "directly.",
            reply_markup=CANCEL_KEYBOARD,
        )
        context.user_data[DELETE_KEYBOARD_KEY] = reply_message
        return GET_UID_STATE

    role.add_member(int(message.text.strip()))
    message.reply_text('User was successfully added.')
    return ConversationHandler.END


def build_add_user_conversation_handler(admin_role: Role) -> ConversationHandler:
    """
    Gives a conversation handler that allows to add a user. Will only be accessible to the bot
    admin/s.

    Args:
        admin_role: The admin role.

    """
    return ConversationHandler(
        entry_points=[RolesHandler(CommandHandler('add_user', start), roles=admin_role)],
        states={
            GET_UID_STATE: [
                MessageHandler(Filters.forwarded | Filters.regex(r'^\s*\d+\s*$'), get_uid),
                CallbackQueryHandler(cancel_button, pattern=CANCEL_CALLBACK_DATA),
            ]
        },
        fallbacks=[MessageHandler(Filters.all, abort)],
    )
