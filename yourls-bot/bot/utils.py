#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The module contains utility functionality used by the bot."""

import time
import re
from typing import List, Optional

from telegram import MessageEntity, InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import Filters, ConversationHandler, UpdateFilter, CallbackContext
from yourls import YOURLSClientBase, YOURLSAPIMixin, ShortenedURL
from yourls.extensions import YOURLSDeleteMixin, YOURLSEditUrlMixin

from bot.constants import YOURLS_KEY, CACHE_TIMEOUT_KEY, STATS_KEY, DELETE_KEYBOARD_KEY

TIME_STAMP = '42'


def get_cached_stats(context: CallbackContext) -> List[ShortenedURL]:
    """
    Calls :meth:`yourls.core.stats` in a cached manner and saves the list of short URLS to
    ``context.bot_data[STATS_KEY]``.

    .. seealso:: :attr:`bot.constants.CACHE_TIMEOUT_KEY` and :attr:`bot.constants.STATS_KEY`

    Args:
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns: The list of short URLS, either from memory or fetched from the YOURLS instance.

    """
    cache_timeout = context.bot_data[CACHE_TIMEOUT_KEY]
    now = time.time()
    time_stamp = context.bot_data.get(TIME_STAMP, now - cache_timeout - 1)
    if now - time_stamp > cache_timeout:
        context.bot_data[TIME_STAMP] = now
        yourls = context.bot_data[YOURLS_KEY]
        shortened_urls_list = yourls.stats('last', int(10e42))[0]
        context.bot_data[STATS_KEY] = shortened_urls_list
    return context.bot_data[STATS_KEY]


def check_keyword_existence(context: CallbackContext, keyword: str) -> Optional[ShortenedURL]:
    """
    Checks if a given keyword already exists in the YOURLS instance.

    Note:
        The result is based on :meth:`get_cached_stats`.

    Args:
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
        keyword: The keyword to check.

    Returns:
        :class:`yourls.data.ShortenedURL` | :obj:`None`: The :class:`yourls.data.ShortenedURL`
        instance if the keyword exists, :obj:`None` otherwise.

    """
    short_urls = get_cached_stats(context)
    return next((su for su in short_urls if su.keyword == keyword), None)


def extract_keyword(short_url: str) -> str:
    """
    Extracts the keyword from a short url. More precisely, the part of the URL after the last slash
    (disregarding trailing slashes) will be returned.

    Examples:
        .. code:: python

            assert extract_keyword('https://sho.rt/foo//') == 'foo'

    Args:
        short_url: The short URL.

    Returns:
        The keyword.

    """
    return short_url.rstrip('/').rpartition('/')[-1]


def cancel_button(update: Update, _: CallbackContext) -> int:
    """
    Changes the messages text to ``Operation aborted.``, deletes the keyboard and returns
    :attr:`telegram.ext.ConversationHandler.END`.

    Args:
        update: The incoming Telegram update containing a :class:`telegram.CallbackQuery`.
        _: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`telegram.ext.ConversationHandler.END`

    """
    update.callback_query.answer()
    update.callback_query.edit_message_text(text='Operation aborted.')
    return ConversationHandler.END


def abort(update: Update, context: CallbackContext) -> int:
    """
    Calls :meth:`delete_keyboard`, replies to the message with ``Operation aborted.`` and returns
    :attr:`telegram.ext.ConversationHandler.END`.

    Args:
        update: The incoming Telegram update containing a message.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`telegram.ext.ConversationHandler.END`

    """
    delete_keyboard(context)
    update.effective_message.reply_text('Operation aborted.')
    return ConversationHandler.END


def delete_keyboard(context: CallbackContext) -> None:
    """
    Deletes the keyboard from a message stored in ``context.user_data[DELETE_KEYBOARD_KEY]``,
    if present.

    Args:
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    message = context.user_data.pop(DELETE_KEYBOARD_KEY, None)
    if message:
        message.edit_reply_markup(reply_markup=None)


def sanitize_protocol(url: str) -> str:
    """
    Sanitizes the prefix of a URL. More precisely, if ``url`` already as a protocol prefix
    (e.g. ``mailto:`` or ``https:``), the ``url`` is returned unchanged. Otherwise it's assumed to
    be a web link and the prefix ``http://`` is added.

    Args:
        url: The URL to sanitize.

    Returns:
        The sanitized URL.

    """
    if re.match('^[a-zA-Z][a-zA-z+.-]*:', url):
        return url
    return f'http://{url}'


def cancel_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """
    Creates a new :class:`telegram.ext.InlineKeyboardMarkup` with a single button with the text
    ``Cancel``.

    Args:
        callback_data: The callback data to pass via the button.

    Returns:
        The keyboard.

    """
    return InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("Cancel", callback_data=callback_data)
    )


class YOURLSClient(  # pylint: disable=R0903
    YOURLSClientBase,
    YOURLSAPIMixin,
    YOURLSDeleteMixin,
    YOURLSEditUrlMixin,
):
    """YOURLS client with API delete & edit support."""


class TwoWordFilter(UpdateFilter):  # pylint: disable=R0903
    """
    Custom :class:`telegram.ext.UpdateFilter` that allows only text messages with exactly two
    words, where exactly one of them is a text link or a URL.
    """

    def filter(self, update: Update) -> bool:  # pylint: disable=R0201
        """
        Method that does the actual filtering.

        Args:
            update: The incoming update.

        Returns:
            The result.

        """
        if not Filters.regex(r'^\s*\S+\s+\S+\s*$')(update):
            return False
        if Filters.entity(MessageEntity.URL)(update) & ~Filters.entity(MessageEntity.TEXT_LINK)(
            update
        ):
            return (
                len([e for e in update.effective_message.entities if e.type == MessageEntity.URL])
                == 1
            )
        if ~Filters.entity(MessageEntity.URL)(update) & Filters.entity(MessageEntity.TEXT_LINK)(
            update
        ):
            return (
                len(
                    [
                        e
                        for e in update.effective_message.entities
                        if e.type == MessageEntity.TEXT_LINK
                    ]
                )
                == 1
            )
        return False
