FROM alpine:3.16.2

RUN apk update
RUN apk add python3
RUN apk add py3-pip
RUN apk add git

COPY ./yourls-bot /home/yourls-bot

WORKDIR /home/yourls-bot

RUN pip install -r requirements.txt

RUN apk del git

CMD ["python3", "main.py"]