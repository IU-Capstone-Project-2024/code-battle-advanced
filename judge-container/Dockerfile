FROM python:3.13-rc-alpine

USER root

#Installing MongoDB
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/main' >> /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/community' >> /etc/apk/repositories
RUN apk add py3-pip mongodb g++ bash

#Installing relevant python packages
RUN pip install pymongo redis

COPY ./worker.py /worker.py
COPY ./judge.sh /judge.sh
COPY ./tasks /tasks
COPY ./useless.py /useless.py
COPY ./submissions /submissions
COPY ./rediswq.py /rediswq.py

EXPOSE 5000

CMD ["python3", "/worker.py"]

