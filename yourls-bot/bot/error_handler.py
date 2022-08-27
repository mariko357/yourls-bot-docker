#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The module contains the error handler."""
import html
import json
import logging
import traceback
from typing import Any, cast

from ptbcontrib.roles import BOT_DATA_KEY, Roles
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def error_handler(update: Any, context: CallbackContext) -> None:
    """
    Log the error and send a telegram message to notify the admin.

    Args:
        update: The incoming update. Not necessarily a Telegram update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = (
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))
        if isinstance(update, Update)
        else "None"
    )
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {update_str}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message to all admins
    for admin in cast(Roles, context.bot_data[BOT_DATA_KEY]).admins.chat_ids:
        try:
            context.bot.send_message(chat_id=admin, text=message)
        except Exception:  # pylint: disable=W0703
            pass
