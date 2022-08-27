FROM alpine:3.16.2
RUN apk update
RUN apk install python3
RUN apk install py3-pip
COPY ./yourls-bot /home/