FROM python:3.13-rc-alpine

USER root

#Installing MongoDB
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/main' >> /etc/apk/repositories
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.6/community' >> /etc/apk/repositories
RUN apk add py3-pip

#Installing relevant python packages
RUN pip install pymongo pathlib bcrypt

COPY ./init_database.py /init_database.py
COPY ./data /data

CMD ["python3", "/init_database.py"]

