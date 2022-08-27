#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The module contains functions for the inline mode."""
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import CallbackContext
from yourls import YOURLSKeywordExistsError, YOURLSNoURLError

from bot.constants import (
    YOURLS_KEY,
    TEMPORARY_KEYWORDS_KEY,
    DONT_DELETE_CIR,
    EMPTY_SWITCH_PM_PARAMETER,
)
from bot.utils import check_keyword_existence, sanitize_protocol


def inline_redirect_info(update: Update, context: CallbackContext) -> None:
    """
    Shows an explanation message to users redirected here from :meth:`inline_shorten`.

    Args:
        update: The incoming Telegram update containing a message.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    if context.args[0] != EMPTY_SWITCH_PM_PARAMETER:
        update.message.reply_text(
            f'The keyword <i>{context.args[0]}</i> is already occupied. Please try another!'
        )
    else:
        update.message.reply_text('You tried to shorten an invalid URL. Please try another!')


def inline_shorten(update: Update, context: CallbackContext) -> None:
    """
    Shortens URLs in inline mode. The query must be either

    * a URL or
    * a URL followed by a keyword (separated by whitespace).

    If an already existing keyword is requested, the user will be presented a button that leads
    to :meth:`inline_redirect_info`.

    Args:
        update: The incoming Telegram update containing an :class:`telegram.InlineQuery`
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    yourls = context.bot_data[YOURLS_KEY]
    if TEMPORARY_KEYWORDS_KEY not in context.user_data:
        context.user_data[TEMPORARY_KEYWORDS_KEY] = []

    if not update.inline_query.query.strip():
        return

    split_query = update.inline_query.query.split()
    if len(split_query) == 2:
        url = split_query[0]
        keyword = split_query[1]
    elif len(split_query) == 1:
        url = split_query[0]
        keyword = None
        short_url = check_keyword_existence(context, url)
        if short_url:
            title = short_url.shorturl
            article = InlineQueryResultArticle(
                DONT_DELETE_CIR, title, InputTextMessageContent(title)
            )
            update.inline_query.answer([article], is_personal=True, cache_time=0)
            return
    else:
        return

    url = sanitize_protocol(url)
    try:
        short_url_instance = yourls.shorten(url, keyword=keyword)
        short_url = short_url_instance.shorturl

        title = f'{keyword} | {short_url_instance.title}' if keyword else short_url_instance.title
        article = InlineQueryResultArticle(
            short_url_instance.keyword, title, InputTextMessageContent(short_url)
        )
        update.inline_query.answer([article], is_personal=True, cache_time=0)
        # we do this here so that the keyword is only appended if nothing went wrong
        context.user_data[TEMPORARY_KEYWORDS_KEY].append(short_url_instance.keyword)

    except YOURLSKeywordExistsError:
        update.inline_query.answer(
            [],
            is_personal=True,
            cache_time=0,
            switch_pm_text='❌ Keyword occupied',
            switch_pm_parameter=keyword,
        )

    except YOURLSNoURLError:
        update.inline_query.answer(
            [],
            is_personal=True,
            cache_time=0,
            switch_pm_text='❌ Invalid URL',
            switch_pm_parameter=EMPTY_SWITCH_PM_PARAMETER,
        )


def delete_temp_links(update: Update, context: CallbackContext) -> None:
    """
    Deletes temporary short URL created by the inline mode.

    Args:
        update: Incoming Telegram update containing a :class:`telegram.ChosenInlineResult`.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    """
    yourls = context.bot_data[YOURLS_KEY]
    chosen_keyword = update.chosen_inline_result.result_id

    if chosen_keyword == DONT_DELETE_CIR:
        return

    # Copy in case the list changes while we iterate
    for keyword in context.user_data[TEMPORARY_KEYWORDS_KEY].copy():
        if keyword != chosen_keyword:
            try:
                yourls.delete(keyword)
            except Exception:  # pylint: disable=W0703
                pass

    context.user_data[TEMPORARY_KEYWORDS_KEY].clear()
