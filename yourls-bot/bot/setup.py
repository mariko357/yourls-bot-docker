#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The module contains functions that register the handlers."""
import warnings
from typing import cast

from telegram.ext import (
    Dispatcher,
    MessageHandler,
    Filters,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    CommandHandler,
)

from ptbcontrib.roles import setup_roles, RolesHandler, Roles

from .add_user import build_add_user_conversation_handler
from .change_keyword import build_change_keyword_conversation_handler
from .change_url import build_change_url_conversation_handler
from .delete_shorturl import build_delete_conversation_handler
from .kick_user import build_kick_user_conversation_handler
from .error_handler import error_handler
from .inline import inline_redirect_info, inline_shorten, delete_temp_links
from .simple_commands import shorten, shorten_with_keyword, info
from .utils import YOURLSClient, TwoWordFilter
from .constants import USER_ROLE, YOURLS_KEY, CACHE_TIMEOUT_KEY

# B/C we know what we're doing
warnings.filterwarnings('ignore', message="If 'per_", module='telegram.ext.conversationhandler')
warnings.filterwarnings(
    'ignore',
    message="BasePersistence.insert_bot does not handle objects",
    module='telegram.ext.basepersistence',
)
warnings.filterwarnings(
    'ignore',
    message="BasePersistence.replace_bot does not handle objects",
    module='telegram.ext.basepersistence',
)


def setup_dispatcher(
    dispatcher: Dispatcher, client: str, signature: str, cache_timeout: int, admin: int
) -> None:
    """
    Registers the different handlers, prepares ``chat/user/bot_data`` etc.

    Args:
        dispatcher: The dispatcher.
        client: The URL of the YOURLS instance.
        signature: The signature to access the YOURLS API
        cache_timeout: Timeout for YOURLS statistics cache.
        admin: The admins Telegram chat ID.

    """
    yourls = YOURLSClient(client, signature=signature, nonce_life=True)
    dispatcher.bot_data[YOURLS_KEY] = yourls
    dispatcher.bot_data[CACHE_TIMEOUT_KEY] = cache_timeout
    bot_id = dispatcher.bot.id

    roles = cast(Roles, setup_roles(dispatcher))

    roles.add_admin(admin)
    if USER_ROLE not in roles:
        roles.add_role(name=USER_ROLE)
    user_role = roles[USER_ROLE]

    dispatcher.add_handler(build_delete_conversation_handler(user_role))
    dispatcher.add_handler(build_change_url_conversation_handler(user_role))
    dispatcher.add_handler(build_change_keyword_conversation_handler(user_role))
    dispatcher.add_handler(build_add_user_conversation_handler(roles.admins))
    dispatcher.add_handler(build_kick_user_conversation_handler(roles.admins, bot_id))

    dispatcher.add_handler(ChosenInlineResultHandler(delete_temp_links))
    dispatcher.add_handler(
        RolesHandler(
            MessageHandler(TwoWordFilter() & ~Filters.via_bot(bot_id), shorten_with_keyword),
            roles=user_role,
        )
    )
    dispatcher.add_handler(
        RolesHandler(
            MessageHandler(Filters.text & ~Filters.command & ~Filters.via_bot(bot_id), shorten),
            roles=user_role,
        )
    )
    dispatcher.add_handler(RolesHandler(InlineQueryHandler(inline_shorten), roles=user_role))
    dispatcher.add_handler(
        RolesHandler(
            CommandHandler('start', inline_redirect_info, filters=Filters.regex(r'\s')),
            roles=user_role,
        )
    )
    dispatcher.add_handler(CommandHandler(['start', 'help', 'info'], info))

    dispatcher.bot.set_my_commands(
        [
            ('change_keyword', 'Change the keyword of existing short URL'),
            ('change_url', 'Change the URL for existing keyword'),
            ('delete_url', 'Delete existing keyword'),
            ('add_user', 'Authorize a user to use this bot'),
            ('kick_user', 'Disallow a user from using this bot'),
            ('help', 'Display general information'),
        ]
    )

    dispatcher.add_error_handler(error_handler)
