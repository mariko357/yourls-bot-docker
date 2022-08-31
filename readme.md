# Containerized version of [Yourls Telegram Bot](https://gitlab.com/HirschHeissIch/yourls-bot)
## Note: I'm not the author of this project, I just made the containerized version of it, please be sure to check out the original project's repo.
## Setting up
To run container in detached mode simply copy the command below:
```
$ docker run -d --name container-name -v path/to/bot.ini/file/bot.ini:/home/yourls-bot/bot.ini markbel/docker-yourls-bot:latest
```
Where:
* ``` container-name ``` is the name of your container;
* ```path/to/bot.ini/file/bot.ini``` is the path to bot.ini file;
## bot.ini file
This file is used to configure credentails for bot.
**This file stores private information and shouldn't be published anywhere!**
```
[yourls-bot]
token = token
admins_chat_id = 123456
client = https://examp.le
signature = yourls-api-signature
# in seconds:
cache_timeout = 10

```

Where:
* ``token``: your bots token
* ``admins_chat_id``: your Telegram ID. Used to send error reports
* ``client``: URL of your YOURLS instance. The ``/yourls-api.php`` suffix can be skipped
* ``signature``: Your signature for the YOURLS API.
* ``cache_timeout``: For some of the functionality it's necessary to get all short URLs currently stored on your YOURLS
  instance. This is done in a cached manner, i.e. the short URLS are retrieved at most every ``cache_timeout`` seconds.
  Defaults to 10 seconds.


## For detailed information see original repo: https://gitlab.com/HirschHeissIch/yourls-bot
## For dockerfile see this repo: https://github.com/mariko357/yourls-bot-docker
