Creating Short URLs
===================

To shorten a link, simply send it to the bot. It will reply with a short URL.

You can also send multiple links in one message. The bot will reply with the corresponding short URLs in the same order.
Note that exact duplicate links will produce only one short URL, but there might still be multiple links leading to the
same source (e.g. sending ``https://yourls.org http://yourls.org`` will create two short URLs).

To shorten a link with a custom keyword send the link and the keyword separated by a whitespace (order doesn't matter).

.. note::
    The bot does not check, if the link was already shortened and just creates a new short URL.

Inline Mode
===========

The bot supports usage in `inline mode <https://core.telegram.org/bots/inline>`_.

To shorten a link directly in a chat with friends, type ``@your_yourls_bot <link>``. The bot will show a button with the short URL. Tap it to send it in the chat.

You can also shorten a link with a custom keyword via ``@your_yourls_bot <link> <keyword>``.

Finally, type ``@your_yourls_bot <keyword>`` to retrieve the short link of an already existing keyword.

.. note::
    You might take a while to type the ``<link>`` or ``<keyword>`` in ``@your_yourls_bot <link> (<keyword>)``, which will lead to the bot creating unwanted short URLs. Those temporary results will be deleted once you select the final short URL to send.

Managing Short URLs
===================

The bot offers a number of commands allowing you to manage your short URLs:

* With ``/delete_url`` you can delete a short URl.
* With ``/change_keyword`` you can change the keyword of a short URL, i.e. change ``http://your.ls/foo`` to ``http://your.ls/bar``, while not changing the linked long URL
* With ``/change_url`` you can change the long URL associated with a keyword.

Administration
==============

As privately hosted YOURLS instances usually are not open for public use, this bot can be used only by authorized users.
Only the admin specified in ``bot.ini`` can use the bot without authorization and the admin is the only one who can
add and kick users. To do so, please use the commands ``/add_user`` and ``/kick_user``.
