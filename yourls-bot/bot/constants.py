#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains constants used throughout the bot."""

HOMEPAGE: str = 'https://hirschheissich.gitlab.io/yourls-bot/'
""":obj:`str`: Homepage of this bot."""
USER_GUIDE: str = f'{HOMEPAGE}userguide.html'
""":obj:`str`: User guide for this bot."""
USER_ROLE = 'user_role'
""":obj:`str`: Name of the user role."""
DONT_DELETE_CIR = 'dont_delete_cir'
"""
:obj:`str`: Use as ``id`` for :class:`telegram.ChosenInlineResult` that should not be deleted by
  :meth:`bot.inline.delete_temp_links`.
"""
EMPTY_SWITCH_PM_PARAMETER = 'empty_switch_pm'
"""
:obj:`str`: Use for the `switch_pm_parameter` of :meth:`telegram.bot.answer_inline_query` when you
    have to supply it but don't want to. Filter out in your callback.
"""

# Keys bot bot/chat/user_data
DELETE_KEYBOARD_KEY = 'delete_keyboard_key'
""":obj:`str`: Key for ``bot_data`` to store messages in for :meth:`bot.utils.delete_keyboard`."""
YOURLS_KEY = 'yourls_key'
""":obj:`str`: The key of ``bot_data`` where the :class:`bot.utils.YOURLSClient` is stored."""
CHANGE_KEYWORD_KEY = 'change_keyword_old'
""":obj:`str`: Key for ``bot_data`` to store temporary data for the conversation in
:attr:`bot.change_keyword`."""
CHANGE_URL_KEY = 'change_url_old'
""":obj:`str`: Key for ``bot_data`` to store temporary data for the conversation in
:attr:`bot.change_keyword`."""
TEMPORARY_KEYWORDS_KEY = 'temp_keywords'
""":obj:`str`: Key for ``bot_data`` to store temporary keywords created by inline mode on the
fly."""
STATS_KEY = 'stats_key'
""":obj:`str`: Key for ``bot_data`` to store statistics about the YOURLS instance in. Used for
:meth:`bot.utils.get_cached_stats`."""
CACHE_TIMEOUT_KEY = 'cache_timeout_key'
""":obj:`str`: Key for ``bot_data`` to store cache timeout for statistics in. Used for
:meth:`bot.utils.get_cached_stats`."""
