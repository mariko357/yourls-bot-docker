#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module provides a conversation allowing to kick a user."""
from typing import cast

from ptbcontrib.roles import RolesHandler, Role, BOT_DATA_KEY
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    CallbackContext,
    InlineQueryHandler,
    ChosenInlineResultHandler,
)

from bot.utils import cancel_button, abort, delete_keyboard, cancel_keyboard
from .constants import DELETE_KEYBOARD_KEY, USER_ROLE

GET_UID_STATE = 'get user id'
KICK_USER_STATE = 'delete user'
CANCEL_CALLBACK_DATA = 'cancel_user_exchange'
CANCEL_KEYBOARD = cancel_keyboard(CANCEL_CALLBACK_DATA)


def start(update: Update, context: CallbackContext) -> str:
    """
    Initializes the conversation and asks for the user to kick.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    button = InlineKeyboardButton('Click Me 👆', switch_inline_query_current_chat='')
    reply_markup = cancel_keyboard(CANCEL_CALLBACK_DATA)
    reply_markup.inline_keyboard.insert(0, [button])
    message = update.effective_message.reply_text(
        'Which user do you want to kick? Click the button below to select the user.',
        reply_markup=reply_markup,
    )
    context.user_data[DELETE_KEYBOARD_KEY] = message
    return GET_UID_STATE


def select_user(update: Update, context: CallbackContext) -> str:
    """
    Shows the list of currently allowed users, excluding the admin.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    role = cast(Role, context.bot_data[BOT_DATA_KEY][USER_ROLE])
    results = []
    for user_id in role.chat_ids:
        # For new we just don't worry about flood limits here ...
        chat = context.bot.get_chat(user_id)
        name = chat.first_name
        if chat.last_name:
            name = f'{name} {chat.last_name}'
        if chat.username:
            name = f'{name} (@{chat.username})'
        article = InlineQueryResultArticle(user_id, name, InputTextMessageContent(name))

        results.append(article)

    update.inline_query.answer(results, auto_pagination=True, cache_time=0)
    return KICK_USER_STATE


def kick_user(update: Update, context: CallbackContext) -> str:
    """
    Kicks the selected user and confirms the action.

    Args:
        update: The incoming Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state.

    """
    delete_keyboard(context)
    role = cast(Role, context.bot_data[BOT_DATA_KEY][USER_ROLE])
    role.kick_member(int(update.chosen_inline_result.result_id))
    update.effective_user.send_message('The user was kicked and can no longer use this bot.')
    return ConversationHandler.END


def build_kick_user_conversation_handler(admin_role: Role, bot_id: int) -> ConversationHandler:
    """
    Gives a conversation handler that allows to kick a user. Will only be accessible to the bot
    admin/s.

    Args:
        admin_role: The admin role.
        bot_id: The bot's ID.

    """
    return ConversationHandler(
        entry_points=[RolesHandler(CommandHandler('kick_user', start), roles=admin_role)],
        states={
            GET_UID_STATE: [
                InlineQueryHandler(select_user),
                CallbackQueryHandler(cancel_button, pattern=CANCEL_CALLBACK_DATA),
            ],
            KICK_USER_STATE: [ChosenInlineResultHandler(kick_user)],
        },
        fallbacks=[MessageHandler(Filters.all & ~Filters.via_bot(bot_id), abort)],
        per_chat=False,
    )
